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
    path('listar/chamados/', listar_chamados, name='listar_chamados'),
    path('editar_usuario/<int:pk>/', editar_usuarios, name='editar_usuario'),
    path('abrir/chamado/', abrir_chamado, name='abrir_chamado'),

]


# Adicione a configuração para manipular erros
handler404 = 'main.views.error_handler'  # View que manipulará o erro 404
handler500 = 'main.views.error_handler'  # View que manipulará o erro 500


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)