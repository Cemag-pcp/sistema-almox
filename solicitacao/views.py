from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import *
from .models import *
from cadastro.models import Cc

def criar_solicitacoes(request):

    funcionarios = Funcionario.objects.all()
    itens_requisicao = ItensSolicitacao.objects.all()
    itens_transferencia = ItensTransferencia.objects.all()
    depositos_destino = DepositoDestino.objects.all()
    form_requisicao = SolicitacaoRequisicaoForm(request.POST, prefix='requisicao')
    centro_custo = Cc.objects.all()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'requisicao':
            form_requisicao = SolicitacaoRequisicaoForm(request.POST, prefix='requisicao')
            if form_requisicao.is_valid():
                form_requisicao.save()
                return HttpResponseRedirect(reverse('criar_solicitacoes'))  
        
        elif form_type == 'transferencia':
            form_transferencia = SolicitacaoTransferenciaForm(request.POST, prefix='transferencia')
            if form_transferencia.is_valid():
                form_transferencia.save()
                return HttpResponseRedirect(reverse('criar_solicitacoes')) 

    context = {
        'form_requisicao':form_requisicao,
        'depositos':depositos_destino,
        'funcionarios': funcionarios,
        'itens': itens_requisicao,
        'itens_transferencia': itens_transferencia,
        'centro_custo': centro_custo,
    }

    return render(request, 'solicitacao.html', context)

def get_cc_by_matricula(request):
    matricula = request.GET.get('matricula')
    print(matricula)
    if matricula:
        try:
            funcionario = Funcionario.objects.get(pk=matricula)
            cc_list = funcionario.cc.values('id', 'nome')
            return JsonResponse({'cc': list(cc_list)})
        except Funcionario.DoesNotExist:
            return JsonResponse({'error': 'Funcionário não encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Matrícula não fornecida'}, status=400)

def get_unidade_by_item(request):
    item_id = request.GET.get('item_id')
    item = ItensSolicitacao.objects.filter(id=item_id).first()
    if item:
        unidade = item.unidade
        return JsonResponse({'unidade': unidade})
    return JsonResponse({'error': 'Item não encontrado'}, status=404)

def carregar_classes(request):
    item_id = request.GET.get('item_id')
    classes = ClasseRequisicao.objects.filter(itenssolicitacao=item_id).values('id', 'nome')
    return JsonResponse({'classes': list(classes)})

@login_required    
def historico_requisicao(request):

    return render(request, "historico-requisicao.html")

@csrf_exempt
def solicitacao_data_requisicao(request):
    if request.method == "POST":
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))

        # Ordenação
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')
        
        # Mapeamento do índice da coluna para o campo correspondente no banco de dados
        columns = [
            'classe_requisicao', 
            'quantidade',
            'obs',
            'data_solicitacao', 
            'cc__nome',
            'funcionario__nome',
            'item__nome',
            'entregue_por__nome',
            'data_entrega', 
            'rpa',
        ]
        
        order_column = columns[order_column_index]

        if order_dir == 'desc':
            order_column = '-' + order_column

        # Filtro de busca
        search_value = request.POST.get('search[value]', '')

        solicitacoes = SolicitacaoRequisicao.objects.all()

        if search_value:
            solicitacoes = solicitacoes.filter(
                Q(item__nome__icontains=search_value) |
                Q(funcionario__nome__icontains=search_value) |
                Q(classe_requisicao__nome__icontains=search_value)
            )

        # Ordenação
        solicitacoes = solicitacoes.order_by(order_column)

        # Paginação
        paginator = Paginator(solicitacoes, length)
        page_number = start // length + 1
        solicitacoes_page = paginator.get_page(page_number)

        data = []
        for solicitacao in solicitacoes_page:
            status = "Pendente entrega" if solicitacao.entregue_por is None else "Entregue"
    
            # Acessando centros de custo (cc) do Funcionario
            cc_nomes = ', '.join([cc.nome for cc in solicitacao.funcionario.cc.all()])

            data.append({
                'classe_requisicao': solicitacao.classe_requisicao.nome,  # Ajustado para evitar a serialização do objeto
                'quantidade': solicitacao.quantidade,
                'obs': solicitacao.obs,
                'data_solicitacao': solicitacao.data_solicitacao.strftime("%d/%m/%Y %H:%M"),
                'cc__nome': cc_nomes,  # Agora pegando corretamente os centros de custo
                'funcionario__nome': solicitacao.funcionario.nome,
                'item__nome': solicitacao.item.nome,
                'entregue_por__nome': solicitacao.entregue_por.nome if solicitacao.entregue_por else 'Não Entregue',
                'ultima_atualizacao': solicitacao.data_solicitacao.strftime("%d/%m/%Y %H:%M"),
                'data_entrega': solicitacao.data_entrega.strftime("%d/%m/%Y %H:%M") if solicitacao.data_entrega else '',
                'status': status,
                'rpa': solicitacao.rpa
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': paginator.count,
            'recordsFiltered': paginator.count,
            'data': data,
        })

@login_required    
def historico_transferencia (request):

    return render(request, "historico-transferencia.html")

@csrf_exempt
def solicitacao_data_transferencia(request):
    if request.method == "POST":
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))

        # Ordenação
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')
        
        # Mapeamento do índice da coluna para o campo correspondente no banco de dados
        columns = [
            'quantidade',
            'obs',
            'data_solicitacao', 
            'deposito_destino__nome',
            'funcionario__nome',
            'item__nome',
            'entregue_por__nome',
            'ultima_atualizacao',
            'data_entrega', 
            'rpa',
        ]
        
        order_column = columns[order_column_index]

        if order_dir == 'desc':
            order_column = '-' + order_column

        # Filtrando as execuções (se houver busca)
        search_value = request.POST.get('search[value]', '')

        solicitacoes = SolicitacaoTransferencia.objects.all()

        if search_value:
            solicitacoes = solicitacoes.filter(
                item__nome__contains=search_value
            )

        # Aplicando ordenação
        solicitacoes = solicitacoes.order_by(order_column)

        # Paginação
        paginator = Paginator(solicitacoes, length)
        solicitacoes_page = paginator.get_page(start // length + 1)

        data = []
        for solicitacao in solicitacoes_page:
            status = "Pendente entrega" if solicitacao.entregue_por is None else "Entregue"
            data.append({
                'quantidade': solicitacao.quantidade,
                'obs': solicitacao.obs,
                'data_solicitacao': solicitacao.data_solicitacao.strftime("%d/%m/%Y %H:%M"),
                'deposito_destino__nome': solicitacao.deposito_destino.nome,
                'funcionario__nome': solicitacao.funcionario.nome,
                'item__nome': solicitacao.item.nome,
                'entregue_por__nome': solicitacao.entregue_por.nome if solicitacao.entregue_por else '',
                'data_entrega': solicitacao.data_entrega.strftime("%d/%m/%Y %H:%M") if solicitacao.data_entrega else '',
                'status': status,
                'rpa': solicitacao.rpa
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': paginator.count,
            'recordsFiltered': paginator.count,
            'data': data,
        })

def cadastro_novo_item(request):

    if request.method == 'POST':

        pk_funcionario = request.POST.get('id-funcionario-cadastro-item')
        tipo_solicitacao = request.POST.get('tipo_solicitacao')
        codigo = request.POST.get('id-codigo-item')
        descricao = request.POST.get('id-descricao-item')
        quantidade = request.POST.get('id-quantidade-solicitante')
        cc = request.POST.get('requisicao-cc-novo-item')

        funcionario = get_object_or_404(Funcionario, pk=pk_funcionario)

        if tipo_solicitacao == 'transferencia':

            pk_deposito = request.POST.get('id-cadastrar-deposito')

            deposito_destino_object = get_object_or_404(DepositoDestino, pk=pk_deposito)

            SolicitacaoCadastroItem.objects.create(
                funcionario=funcionario,
                tipo_solicitacao=tipo_solicitacao,
                codigo=codigo,
                descricao=descricao,
                quantidade=quantidade,
                deposito_destino=deposito_destino_object
            )

        else:

            cc_object = get_object_or_404(Cc, pk=cc)

            SolicitacaoCadastroItem.objects.create(
                funcionario=funcionario,
                tipo_solicitacao=tipo_solicitacao,
                codigo=codigo,
                descricao=descricao,
                quantidade=quantidade,
                cc=cc_object,
            )

    return redirect('criar_solicitacoes')

def cadastro_nova_matricula(request):

    if request.method == 'POST':

        matricula = request.POST.get('id-matricula-solicitante')
        nome = request.POST.get('id-nome-solicitante')
        pk_cc = request.POST.get('id-ccusto-solicitante')

        cc_object = get_object_or_404(Cc, pk=pk_cc)

        SolicitacaoNovaMatricula.objects.create(
            matricula=matricula,
            nome=nome,
            cc=cc_object
        )

    return redirect('criar_solicitacoes')

@login_required  
def gerir_solicitacoes(request):

    cadastro_matricula = SolicitacaoNovaMatricula.objects.filter(aprovado=False)
    cadastro_item = SolicitacaoCadastroItem.objects.filter(aprovado=False)
    mensagem_erro = None  # Variável para armazenar a mensagem de erro

    if request.method == 'POST':

        tipo_cadastro = request.POST.get("tipo_cadastro")
        solicitacao_id = request.POST.get('id')
        

        if "add" in request.POST:
            
            if tipo_cadastro == 'item':
                
                solicitacao = get_object_or_404(SolicitacaoCadastroItem, pk=solicitacao_id)
                solicitacao.aprovado = True
                solicitacao.data_aprovacao = datetime.datetime.now()
                solicitacao.save()
                
                if solicitacao.tipo_solicitacao == 'requisicao':
                    
                    try:
                        opcao = int(request.POST.get('opcao'))    
                        
                        classe_object = get_object_or_404(ClasseRequisicao, pk=opcao)

                        # Cadastrando novo item
                        novo_item = ItensSolicitacao.objects.create(
                            codigo=solicitacao.codigo,
                            nome=solicitacao.descricao
                        )

                        # Adicionando ao ManyToManyField 'classe_requisicao'
                        novo_item.classe_requisicao.add(classe_object)  # 'opcao' deve ser um objeto ClasseRequisicao
                        
                        # Criando a solicitação
                        funcionario_object = get_object_or_404(Funcionario, pk=solicitacao.funcionario.pk)
                        
                        # Criando a solicitação (você precisa decidir como lidar com o campo 'cc' na SolicitaçãoRequisicao)
                        nova_solicitacao = SolicitacaoRequisicao.objects.create(
                            quantidade=solicitacao.quantidade,
                            funcionario=funcionario_object,
                            item=novo_item,
                            classe_requisicao=classe_object,
                            cc=solicitacao.cc
                        )

                    except IntegrityError:
                        # Captura o erro de integridade (violação da chave UNIQUE ou outros erros de integridade)
                        mensagem_erro = "Erro: O código do item já existe."
                                
                else:
                    
                    try:
                    
                        # Cadastrando novo item
                        novo_item = ItensTransferencia.objects.create(
                            codigo = solicitacao.codigo,
                            nome = solicitacao.descricao,
                        )
                        novo_item.save()
                        
                        # Criando solicitação
                        funcionario_object = get_object_or_404(Funcionario, pk=solicitacao.funcionario.pk)
                        cc_object = funcionario_object.cc  # Aqui você acessa diretamente o 'cc' do funcionário

                        nova_solicitacao = SolicitacaoTransferencia.objects.create(
                            quantidade=solicitacao.quantidade,
                            deposito_destino=solicitacao.deposito_destino,
                            funcionario=solicitacao.funcionario,
                            item=novo_item,
                        )
                        nova_solicitacao.save()

                    except IntegrityError:
                        # Captura o erro de integridade (violação da chave UNIQUE)
                        mensagem_erro = "Erro: O código do item já existe."
                        
            else:
                
                solicitacao = get_object_or_404(SolicitacaoNovaMatricula, pk=solicitacao_id)
                solicitacao.aprovado = True
                solicitacao.data_aprovacao = datetime.datetime.now()
                solicitacao.save()
                
                try:
                    
                    # Cadastrando nova matricula
                    cc_object = get_object_or_404(Cc, nome=solicitacao.cc)

                    novo_item = Funcionario.objects.create(
                        matricula = solicitacao.matricula,
                        nome = solicitacao.nome,
                    )

                    novo_item.cc.add(cc_object)

                    novo_item.save()
                
                except IntegrityError:
                    mensagem_erro = "Erro: Matrícula já cadastrada"

        if "apagar" in request.POST:

            if tipo_cadastro == 'item':
                SolicitacaoCadastroItem.objects.filter(id=solicitacao_id).delete()
            else:
                SolicitacaoNovaMatricula.objects.filter(id=solicitacao_id).delete()

            return redirect("gerir_solicitacoes")

    context = {
        'cadastro_matricula': cadastro_matricula,
        'cadastro_item': cadastro_item,
        'mensagem_erro': mensagem_erro,  # Adiciona a mensagem de erro ao contexto

    }

    return render(request, 'solicitacao-cadastro.html', context)

def edit_solicitacao_cadastro_item(request,pk,tipo_cadastro):
    
    item=get_object_or_404(SolicitacaoCadastroItem,pk=pk)
    
    if request.method == 'POST':
        
        if tipo_cadastro == 'requisicao':
            
            form = SolicitacaoCadastroItemRequisicaoForm(request.POST, instance=item)
            
            if form.is_valid():
                
                form.save()
                
                return redirect('gerir_solicitacoes')

        else:
            form = SolicitacaoCadastroItemTransferenciaForm(request.POST, instance=item)
            
            if form.is_valid():
                
                form.save()
                
                return redirect('gerir_solicitacoes')

    else:
        
        if tipo_cadastro == 'requisicao':
            form=SolicitacaoCadastroItemRequisicaoForm(instance=item)
        else:
            form=SolicitacaoCadastroItemTransferenciaForm(instance=item)
        
    return render(request,'item/edit-solicitacao-cadastro.html', {'form':form})

def edit_solicitacao_cadastro_matricula(request,pk):
    
    matricula=get_object_or_404(SolicitacaoNovaMatricula,pk=pk)
    
    if request.method == 'POST':
        
        form = SolicitacaoCadastroMatriculaForm(request.POST, instance=matricula)
        
        if form.is_valid():
            
            form.save()
            
            return redirect('gerir_solicitacoes')
    else:
        
        form = SolicitacaoCadastroMatriculaForm(instance=matricula)
        
    return render(request,'matricula/edit-matricula-cadastro.html', {'form':form})

def edit_solicitacao(request, tipo_solicitacao, requisicao_id):
    
    if request.method == 'POST':

        if tipo_solicitacao == 'requisicao':

            item = request.POST.get('requisicao-item')
            classe_req = request.POST.get('requisicao-classe_requisicao')
            quantidade = request.POST.get('requisicao-quantidade')

            item_object = get_object_or_404(ItensSolicitacao, pk=item)
            classe_object = get_object_or_404(ClasseRequisicao, pk=classe_req)

            solicitacao = get_object_or_404(SolicitacaoRequisicao, pk=requisicao_id)

            solicitacao.item = item_object
            solicitacao.classe_requisicao = classe_object
            solicitacao.quantidade = quantidade

            solicitacao.save()
        
        else:

            solicitacao = get_object_or_404(SolicitacaoTransferencia, pk=requisicao_id)
            
            item = request.POST.get('transferencia-item')
            deposito_destino = request.POST.get('transferencia-deposito_destino')
            quantidade = float(request.POST.get('transferencia-quantidade').replace(',',"."))

            item_object = get_object_or_404(ItensTransferencia, pk=item)
            deposito_destino_object = get_object_or_404(DepositoDestino, pk=deposito_destino)

            solicitacao.item = item_object
            solicitacao.deposito_destino = deposito_destino_object
            solicitacao.quantidade = quantidade

            solicitacao.save()

        return redirect('lista_solicitacoes')

    else:
        # Verifica se o tipo de solicitação é 'requisicao'
        if tipo_solicitacao == 'requisicao':
            # Obtém a solicitação ou retorna um erro 404 se não for encontrada
            solicitacao = get_object_or_404(SolicitacaoRequisicao, pk=requisicao_id)
            
            # Obtém os itens relacionados a esta solicitação, filtrando pelo ID da solicitação
            itens_requisicao = ItensSolicitacao.objects.all()

            # Obtém o funcionário relacionado à solicitação
            solicitante = solicitacao.funcionario

            item = solicitacao.item

            # Obtém outros detalhes que você pode querer passar no contexto
            item_escolhido_codigo = solicitacao.item.codigo if solicitacao.item else None
            cc = solicitante.cc.all()  # Se `cc` for um campo ManyToManyField no funcionário
            classe = item.classe_requisicao.all()  # Supondo que exista um campo 'classe_requisicao' na solicitação
            obs = solicitacao.obs  # Caso haja um campo 'observacao'
            quantidade = solicitacao.quantidade 
            quantidade = str(quantidade).replace(',', '.')

            # Define o contexto a ser passado para o template
            context = {
                'solicitante': f'{solicitante.matricula} - {solicitante.nome}',
                'itens': itens_requisicao,
                'item_escolhido_codigo': item_escolhido_codigo,
                'ccs': cc,
                'classes': classe,
                'quantidade':quantidade,
                'obs': obs,
                'unidade': item.unidade,
                'classe_escolhida':solicitacao.classe_requisicao.pk,
                'tipo_solicitacao':tipo_solicitacao
            }

            # Renderiza o template com o contexto definido
            return render(request, 'editar_solicitacao.html', context)

        else:
            # Obtém a solicitação ou retorna um erro 404 se não for encontrada
            solicitacao = get_object_or_404(SolicitacaoTransferencia, pk=requisicao_id)
            
            # Obtém os itens relacionados a esta solicitação, filtrando pelo ID da solicitação
            itens_requisicao = ItensTransferencia.objects.all()

            # Obtém o funcionário relacionado à solicitação
            solicitante = solicitacao.funcionario

            item = solicitacao.item

            # Obtém outros detalhes que você pode querer passar no contexto
            item_escolhido_codigo = solicitacao.item.codigo if solicitacao.item else None
            obs = solicitacao.obs  # Caso haja um campo 'observacao'
            quantidade = solicitacao.quantidade 
            quantidade = str(quantidade).replace(',', '.')
            deposito_destino = solicitacao.deposito_destino.nome
            depositos = DepositoDestino.objects.all()

            # Define o contexto a ser passado para o template
            context = {
                'solicitante': f'{solicitante.matricula} - {solicitante.nome}',
                'itens': itens_requisicao,
                'item_escolhido_codigo': item_escolhido_codigo,
                'quantidade':quantidade,
                'obs': obs,
                'deposito_destino_escolhido':deposito_destino,
                'depositos':depositos,
                'tipo_solicitacao':tipo_solicitacao
            }

            # Renderiza o template com o contexto definido
            return render(request, 'editar_solicitacao.html', context)
