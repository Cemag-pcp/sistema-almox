from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse

from solicitacao.models import SolicitacaoRequisicao, SolicitacaoTransferencia
from solicitacao.forms import SolicitacaoRequisicaoForm, SolicitacaoTransferenciaForm
from cadastro.models import Operador, Funcionario, ItensSolicitacao, ItensTransferencia

from datetime import datetime

@login_required
def lista_solicitacoes(request):
    requisicoes = SolicitacaoRequisicao.objects.filter(entregue_por=None)
    transferencias = SolicitacaoTransferencia.objects.filter(entregue_por=None)
    operadores_entrega = Operador.objects.all()

    if request.method == "POST":
        if "entregar" in request.POST:
            solicitacao_id = request.POST.get("solicitacao_id")
            tipo_solicitacao = request.POST.get("tipo_solicitacao")
            if tipo_solicitacao == "requisicao":
                solicitacao = get_object_or_404(SolicitacaoRequisicao, id=solicitacao_id)
            else:
                solicitacao = get_object_or_404(SolicitacaoTransferencia, id=solicitacao_id)

            # Solicitar matrícula e data
            matricula = request.POST.get("matricula")
            data_entrega = request.POST.get("data_entrega")

            entregue_por = get_object_or_404(Operador, matricula=matricula)

            # Aqui você poderia adicionar a lógica para salvar esses dados ou marcar como entregue
            solicitacao.entregue_por = entregue_por
            solicitacao.data_entrega = data_entrega
            
            solicitacao.save()

            return redirect("lista_solicitacoes")

        elif "apagar" in request.POST:
            solicitacao_id = request.POST.get("solicitacao_id")
            tipo_solicitacao = request.POST.get("tipo_solicitacao")
            if tipo_solicitacao == "requisicao":
                SolicitacaoRequisicao.objects.filter(id=solicitacao_id).delete()
            else:
                SolicitacaoTransferencia.objects.filter(id=solicitacao_id).delete()

            return redirect("lista_solicitacoes")

        elif "editar" in request.POST:
            solicitacao_id = request.POST.get("solicitacao_id")
            tipo_solicitacao = request.POST.get("tipo_solicitacao")
            funcionario = request.POST.get("funcionario")
            item = request.POST.get("item")
            quantidade = request.POST.get("quantidade")

            if tipo_solicitacao == "requisicao":
                solicitacao = get_object_or_404(SolicitacaoRequisicao, id=solicitacao_id)
            else:
                solicitacao = get_object_or_404(SolicitacaoTransferencia, id=solicitacao_id)

            solicitacao.funcionario = funcionario
            solicitacao.item = item
            solicitacao.quantidade = quantidade
            solicitacao.save()

            return redirect("lista_solicitacoes")

    context = {
        "operadores":operadores_entrega,
        "requisicoes": requisicoes,
        "transferencias": transferencias,
    }

    return render(request, "home/lista_solicitacoes.html", context)

@login_required
def dashboard(request):
    requisicoes = SolicitacaoRequisicao.objects.filter(entregue_por=None)
    transferencias = SolicitacaoTransferencia.objects.filter(entregue_por=None)

    context = {
        "requisicoes": requisicoes,
        "transferencias": transferencias,
    }

    return render(request, "dashboard/dashboard.html", context)

@login_required
def atualizar_dados(request):
    requisicoes = SolicitacaoRequisicao.objects.filter(entregue_por=None)
    transferencias = SolicitacaoTransferencia.objects.filter(entregue_por=None)

    # Crie uma lista personalizada para requisições
    requisicoes_data = [
        {
            "funcionario": f"{req.funcionario.matricula} - {req.funcionario.nome}",
            "item": f"{req.item.codigo} - {req.item.nome}",  # Supondo que 'nome' é o campo que contém o nome do item
            "quantidade": req.quantidade,
        }
        for req in requisicoes
    ]

    # Crie uma lista personalizada para transferências
    transferencias_data = [
        {
            "funcionario": f"{trans.funcionario.matricula} - {trans.funcionario.nome}",
            "item": f"{trans.item.codigo} - {trans.item.nome}",  # Supondo que 'nome' é o campo que contém o nome do item
            "quantidade": trans.quantidade,
        }
        for trans in transferencias
    ]

    return JsonResponse({
        "requisicoes": requisicoes_data,
        "transferencias": transferencias_data,
    })

def processar_edicao(request):
    if request.method == "POST":
        solicitacao_id = request.POST.get("solicitacao_id")
        tipo_solicitacao = request.POST.get("tipo_solicitacao")
        funcionario_str = request.POST.get("funcionario")
        item_str = request.POST.get("item")
        quantidade = request.POST.get("quantidade")

        # Extraia a matrícula do funcionário da string recebida
        matricula = funcionario_str.split(" - ")[0].strip()  # Supondo que o segundo item seja a matrícula

        # Busque a instância de Funcionario usando a matrícula
        funcionario = get_object_or_404(Funcionario, matricula=matricula)

        # Identifica o tipo de solicitação e recupera o objeto correspondente
        if tipo_solicitacao == "requisicao":
            # Extraia o código do item da string recebida
            item_codigo = item_str.split(" - ")[0].strip()  # Supondo que o primeiro item seja o código do item
            item = get_object_or_404(ItensSolicitacao, codigo=item_codigo)
            solicitacao = get_object_or_404(SolicitacaoRequisicao, id=solicitacao_id)
        elif tipo_solicitacao == "transferencia":
            # Extraia o código do item da string recebida
            item_codigo = item_str.split(" - ")[0].strip()  # Supondo que o primeiro item seja o código do item
            item = get_object_or_404(ItensTransferencia, codigo=item_codigo)
            solicitacao = get_object_or_404(SolicitacaoTransferencia, id=solicitacao_id)

        # Atualiza os campos da solicitação com os novos valores
        solicitacao.funcionario = funcionario
        solicitacao.item = item
        solicitacao.quantidade = quantidade
        solicitacao.save()

        return redirect("lista_solicitacoes")

    return redirect("lista_solicitacoes")

def editar_transferencia(request, id):
    transferencia = get_object_or_404(SolicitacaoTransferencia, id=id)
    if request.method == "POST":
        form = SolicitacaoTransferenciaForm(request.POST, instance=transferencia)
        if form.is_valid():
            form.save()
            return redirect('lista_solicitacoes')
    else:
        form = SolicitacaoTransferenciaForm(instance=transferencia)

    return render(request, 'home/editar_solicitacao.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Autentica o usuário
            user = authenticate(username=username, password=password)
            if user is not None:
                # Faz o login do usuário
                login(request, user)
                return redirect('lista_solicitacoes')  # Redireciona após o login bem-sucedido
            else:
                # Se a autenticação falhar, você pode adicionar uma mensagem de erro personalizada
                form.add_error(None, "Usuário ou senha inválidos")
    else:
        form = AuthenticationForm()

    return render(request, 'login/login.html', {'form': form})

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
