from django.urls import path, include
from . import views
from .views import *
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import error_handler


urlpatterns = [
    path('login/', views.view_login, name='view_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('listar/usuarios/', listagem_de_usuarios, name='listagem_usuarios'),
    path('alterar_status/<str:username>/', alterar_status, name='alterar_status'),
    path('deletar_usuario/<int:pk>/', deletar_usuario, name='deletar_usuario'),
    path('erro_na_pagina/<str:exception>/', error_handler, name='error_handler'),
    path('listar/chamados/<str:tipo>/', listar_chamados, name='listar_chamados'),
    path('listar/meus/chamados/<str:tipo>/', meus_chamados, name='meus_chamados'),
    path('editar_usuario/<int:pk>/', editar_usuarios, name='editar_usuario'),
    path('abrir/chamado/', abrir_chamado, name='abrir_chamado'),
    path('abrir/chamado/<int:chamado_id>/', ver_chamado, name='ver_chamado'),
    path('atribuir/chamado/<int:chamado_id>/', atribuir_chamado, name='atribuir_chamado'),
    path('desatribuir/chamado/<int:chamado_id>/', desatribuir_chamado, name='desatribuir_chamado'),
    path('atribuir//chamado/pendente/<int:chamado_id>/', chamado_pendente, name='chamado_pendente'),
    path('atribuir/chamado/concluido/<int:chamado_id>/', chamado_concluido, name='chamado_concluido'),
    path('excluir/chamado/<int:chamado_id>/', excluir_chamado, name='excluir_chamado'),
    path('reabrir/chamado/<int:chamado_id>/', reabrir_chamado, name='reabrir_chamado'),
    path('finalizar/chamado/<int:chamado_id>/', finalizar_chamado, name='finalizar_chamado'),

]


# Adicione a configuração para manipular erros
handler404 = 'main.views.error_handler'  # View que manipulará o erro 404
handler500 = 'main.views.error_handler'  # View que manipulará o erro 500


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)