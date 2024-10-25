from django.urls import path

from . import views
from .views import CustomLogoutView

urlpatterns = [
    path('solicitacoes/', views.lista_solicitacoes, name='lista_solicitacoes'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('atualizar-dados/', views.atualizar_dados, name='atualizar_dados'),

    path('processar_edicao/', views.processar_edicao, name='processar_edicao'),

    path('login/', views.user_login, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
]
