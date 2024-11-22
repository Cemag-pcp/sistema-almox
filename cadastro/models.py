from django.db import models
from django.contrib import admin

class Cc(models.Model):

    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):

        return f'{self.nome}'
    
class Funcionario(models.Model):

    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=5, unique=True)
    cc = models.ManyToManyField(Cc, related_name='funcionario_cc')

    def __str__(self):
        return f'{self.nome} - {self.matricula}'

class ClasseRequisicao(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nome

class ItensSolicitacao(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=120)
    classe_requisicao = models.ManyToManyField(ClasseRequisicao)
    unidade = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'{self.codigo} - {self.nome}'
        
class ItensTransferencia(models.Model):

    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=120)
    unidade = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):

        return f'{self.codigo} - {self.nome}'

class DepositoDestino(models.Model):

    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):

        return f'{self.nome}'
 
class Operador(models.Model):

    matricula = models.CharField(max_length=5, unique=True)
    nome = models.CharField(max_length=100)
    status = models.BooleanField(default=True)    

    def __str__(self):

        return f'{self.matricula} - {self.nome}'

class FuncionarioAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'matricula', 'cc__nome']

class ItensSolicitacaoAdmin(admin.ModelAdmin):
    search_fields = ['codigo', 'nome', 'classe_requisicao__nome']

class ItensTransferenciaAdmin(admin.ModelAdmin):
    search_fields = ['codigo', 'nome']

class DepositoDestinoAdmin(admin.ModelAdmin):
    search_fields = ['nome']