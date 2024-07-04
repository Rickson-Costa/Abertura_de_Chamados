from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.utils.translation import gettext_lazy as _

class Dados(AbstractUser):
    username = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100)
    setor = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)

    # Atributo REQUIRED_FIELDS para criar um usuário
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name='dados_set',
        related_query_name='dados',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='dados_set',
        related_query_name='dados',
    )

    def __str__(self):
        return self.username

class Chamados(models.Model):
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    setor = models.CharField(max_length=255, blank=True, null=True)
    para_o_setor = models.CharField(max_length=255)
    data_criacao = models.DateTimeField(auto_now_add=True)
    situacao = models.CharField(max_length=255, default='Chamado Aberto')
    nivel = models.CharField(max_length=255, default='Baixa Prioridade')
    assunto = models.CharField(max_length=255, blank=True, null=True)
    texto = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.criado_por   