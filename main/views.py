from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import logging, os
from .models import Dados, Chamados, Timeline, Arquivo
from copy import *
from functools import wraps
from django.shortcuts import redirect
from django.core.paginator import Paginator
from datetime import datetime
import locale
from django.conf import settings
logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

dia = str(datetime.now().day)
mês = datetime.now()
mês = mês.strftime('%B') 
ano = str(datetime.now().year)
hora_atual = datetime.now().strftime('%H:%M:%S')

def usuario_de_setor_especifico(setor):
    def decorador(view_func):
        @wraps(view_func)
        def visualizacao_envolvida(request, *args, **kwargs):
            usuario = Dados.objects.get(username=request.user.username)
            if usuario.setor == setor:
                return view_func(request, *args, **kwargs)
            else:
                e ='A Página foi bloquada para seu usuario.'
                return redirect(error_handler, e) 
        return visualizacao_envolvida
    return decorador


# Create your views here.
@usuario_de_setor_especifico('Tecnologia da Informação')
@login_required(login_url="/SOS/login/")
def listagem_de_usuarios(request):
        users = User.objects.all()
        data = Dados.objects.all()
        return render(request, 'listar.html', {'users': users, 'data': data})
    
def view_login(request):
    if request.user.is_authenticated:
        return redirect('base')

    elif request.method == "GET":
        return render(request, 'login.html', {'erro_code': None})
    
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
                # Verifica se o usuário já existe no banco de dados do Django
                b_usuario = User.objects.filter(username=username).first()
                if b_usuario:
                    print('existe')
                    pass
                else:
                    # Se o usuário não existe, cria um novo usuário inativo
                    logger.warning("Cadastro de um novo usuário")
                    b_usuario = User.objects.create_user(username=username, is_active=False)
                    b_usuario.set_password(password)
                    b_usuario.save()
                    return render(request, 'login.html', {'erro_code': "Conta criada! Entre em contato com a TI para ativar!"})

                # Autentica o usuário no Django
                user = authenticate(username=username, password=password)
                print (user)
                if user is not None:
                    login(request, user)
                    return redirect('base')
                else:
                    return render(request, 'login.html', {'erro_code': "Conta desativada!"})
            
        except:
            return render(request, 'login.html', {'erro_code': "Erro!"})
@login_required(login_url="/SOS/login/")        
def editar_usuarios(request , pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        cargo = request.POST.get('cargo')
        setor = request.POST.get('setor')
        empresa = request.POST.get('empresa')


        usuario.last_name = cargo
        usuario.email = f"{usuario.username}@teste.org.br"
        usuario.save()

        dados_usuario, created = Dados.objects.get_or_create(username=usuario.username)
        dados_usuario.cargo = cargo
        dados_usuario.setor = setor
        dados_usuario.empresa = empresa
        dados_usuario.email = usuario.email
        dados_usuario.save()

        logger.error(f"O usuário {request.user}, alterou o setor do usuário {dados_usuario.username} para {dados_usuario.setor}.")
        logger.error(f"O usuário {request.user}, alterou o cargo do usuário {dados_usuario.username} para {dados_usuario.cargo}.")
        logger.error(f"O usuário {request.user}, alterou o local de trabalho do usuário {dados_usuario.username} para {dados_usuario.empresa}.")

        return redirect("listagem_usuarios")
        
    return render(request, 'editar_usuarios.html', {
        'usuario': usuario,
    })
@login_required(login_url="/SOS/login/")
def abrir_chamado(request):
    users = User.objects.all()
    dados = Dados.objects.all()
    print(request.user.username)
    if request.method == 'POST':
        usuario = Dados.objects.get(username=request.user.username)
        tipo_de_problema = request.POST['P11']
        setor_destino = request.POST['P15']
        setor_origem = usuario.setor
        detalhe_do_problema = request.POST['P12']
        nivel = request.POST.get('nivel')
        data = f'{dia}/{mês}/{ano} às {hora_atual}'
        
        # Cria uma instância do modelo Chamado                      
        novo_chamado = Chamados(
            criado_por = request.user,
            setor = setor_origem,
            para_o_setor = setor_destino,
            data_criacao = data,
            nivel = nivel,
            assunto = tipo_de_problema,
            texto = detalhe_do_problema,
        )
        novo_chamado.save()
        
        # Registra na Timeline
        timeline = Timeline(
            criado_por = request.user,    
            numero = novo_chamado.id,
            data_criacao = data,
            situacao = novo_chamado.situacao,    
        )
        timeline.save()
        # Salvando os arquivos enviados e registrando na Timeline
        if 'file_of' in request.FILES:
            files = request.FILES.getlist('file_of')
            for file in files:
                caminho_destino = os.path.join(settings.MEDIA_ROOT)
                os.makedirs(f'{caminho_destino}/{str(novo_chamado.id)}', exist_ok=True)
                with open(os.path.join(f'{caminho_destino}/{str(novo_chamado.id)}', file.name), 'wb+') as destino:
                    for chunk in file.chunks():
                        destino.write(chunk)
                        # Criando uma instância de Arquivo e associando à Timeline
                        novo_arquivo = Arquivo.objects.create(
                            arquivo=file,
                            descricao=f"{novo_chamado.id}"
                        )
                        timeline.arquivos.add(novo_arquivo)
        return  redirect(inicio)
        
    else:
        return render(request, 'abrir_chamado.html', {'data': dados, 'users': users})

def deletar_usuario(request, pk):
    try:
        # Busca o usuário pelo ID
        user = User.objects.get(id=pk)
        dados = Dados.objects.filter(username=user.username).first()
        # Deleta o usuário
        user.delete()
        if dados:
            dados.delete()
        logger.warning(f'O usuário {request.user.username}, deletou a conta de {user.username} com sucesso!')
    except User.DoesNotExist:
        logger.warning(f'Usuário com o ID {pk} não encontrado.')
    
    return redirect(listagem_de_usuarios)
        
@login_required(login_url="/SOS/login/")
def inicio(request):
    users = User.objects.all()
    data = Dados.objects.all()
    usuario_logador = Dados.objects.get(username=request.user.username)
    
    chamados = Chamados.objects.all()
    chamados_setor_destino = Chamados.objects.filter(para_o_setor = usuario_logador.setor)
    l_chamados_abertos = Chamados.objects.filter(para_o_setor = usuario_logador.setor, situacao='Chamado Aberto')
    l_chamados_concluidos = Chamados.objects.filter(para_o_setor = usuario_logador.setor, situacao='Chamado Concluido')
    l_chamados_finalizados = Chamados.objects.filter(para_o_setor = usuario_logador.setor, situacao='Chamado Finalizado')
    chamados_setor_origem = Chamados.objects.filter(setor = usuario_logador.setor)

    chamados_abertos = len(l_chamados_abertos)
    todos_os_chamados = len(chamados)
    chamados_por_setor = len(chamados_setor_destino)
    chamados_origem = len(chamados_setor_origem)
    chamados_concluido = len(l_chamados_concluidos)
    chamados_finalizados = len(l_chamados_finalizados)
    

    return render(request, 'home.html', {'data' : data, 'users' : users,'chamados_concluidos': chamados_concluido, 'chamados_finalizados' : chamados_finalizados, 'chamados_abertos': chamados_abertos, 'todos_os_chamados' : todos_os_chamados, 'chamados_por_setor' : chamados_por_setor, 'chamados_origem' : chamados_origem})

def alterar_status(request, username):
        usuario = User.objects.get(username = username)
        atual = usuario.is_active
        if atual == 1:
            usuario.is_active = 0
            logger.warning(f'{request.user} desativou a conta do usuario {username}')
        else:
            usuario.is_active = 1
            logger.warning(f'{request.user} ativou a conta do usuario {username}')
        usuario.save()

        # Redirecione ou retorne uma resposta de sucesso
        return redirect(listagem_de_usuarios)

@login_required(login_url="/SOS/login/")
def error_handler(request, exception=None):
    data = Dados.objects.all()
    
    return render(request, 'error.html', {'erro_code': exception, 'data': data}, status=500)

@login_required(login_url="/HNL/login/")
def ver_chamado(request, chamado_id):
    users = User.objects.all()
    data = Dados.objects.all()
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    timeline = Timeline.objects.filter(numero=chamado_id)
    timeline = timeline.order_by('-data_criacao')
    if request.method == 'POST':
        if request.POST.get('timeline_id'):
            timeline_id = request.POST.get('timeline_id')
            timeline = get_object_or_404(Timeline, pk=timeline_id)
            return render (request, 'ver_resposta.html', {'timeline': timeline, 'chamados':chamado, 'data': data, 'users': users})
        
        if request.POST.get('arquivos_anexados'):
            timeline_id = request.POST.get('arquivos_anexados')
            print(timeline_id)
            arquivos = Arquivo.objects.filter(descricao=timeline_id)
            return render(request, 'mensagem.html', {'arquivos': arquivos, 'data': data, 'users': users})

    

    return render(request, 'dados.html',  {'timeline': timeline, 'chamados':chamado, 'data': data, 'users': users})
@login_required(login_url="/SOS/login/")
def listar_chamados(request, tipo):
    users = User.objects.all()
    data = Dados.objects.all()
    usuario = Dados.objects.get(username=request.user.username)

    # Recupera os chamados filtrados pelo usuário logado e pelo tipo especificado
    if tipo == 'abertos':
        chamados = Chamados.objects.filter(para_o_setor=usuario.setor, situacao='Chamado Aberto')
    elif tipo == 'todos':
        chamados = Chamados.objects.filter(para_o_setor=usuario.setor)
    
    chamados = chamados.order_by('-data_criacao')
    paginator = Paginator(chamados, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_chamados.html', {'chamados': chamados, 'data': data, 'users': users, 'page_obj': page_obj})
@login_required(login_url="/SOS/login/")
def meus_chamados(request, tipo):
    users = User.objects.all()
    data = Dados.objects.all()

    if tipo == 'abertos':
        chamados = Chamados.objects.filter(criado_por=request.user, situacao='Chamado Aberto')
    elif tipo == 'todos':
        chamados = Chamados.objects.filter(criado_por=request.user)
    
    chamados = chamados.order_by('-data_criacao')
    paginator = Paginator(chamados, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'meus_chamados.html', {'chamados': chamados, 'data': data, 'users': users, 'page_obj': page_obj})

def atribuir_chamado(request, chamado_id):
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    data = f'{dia}/{mês}/{ano} às {hora_atual}'

    chamado.situacao = 'Chamado Atribuido'
    chamado.save()
    timeline = Timeline(
        criado_por = request.user,    
        numero = chamado_id,
        data_criacao = data,
        situacao = f'Chamado atribuido por {request.user}', 
        codigo = 1,   
    )
    timeline.save()
    
    return redirect('listar_chamados', 'todos')

def desatribuir_chamado(request, chamado_id):
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    data = f'{dia}/{mês}/{ano} às {hora_atual}'

    chamado.situacao = 'Chamado Aberto'
    chamado.save()
    timeline = Timeline(
        criado_por = request.user,    
        numero = chamado_id,
        data_criacao = data,
        situacao = f'Chamado desatribuido por {request.user}', 
        codigo = 2,   
    )
    timeline.save()
    
    return redirect('listar_chamados', 'todos')

def chamado_pendente(request, chamado_id):
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    data = f'{dia}/{mês}/{ano} às {hora_atual}'
    if request.method == 'POST':
        chamado.situacao = 'Chamado Pendente'
        resposta = request.POST['P12']
        chamado.save()
        timeline = Timeline(
            criado_por = request.user,    
            numero = chamado_id,
            data_criacao = data,
            situacao = f'Chamado atribuido como pendente por {request.user}', 
            resposta = resposta,
            codigo = 3,   
        )
        timeline.save()
        
        return redirect('listar_chamados', 'todos')
    else:
        return render(request, 'mensagem.html')

def chamado_concluido(request, chamado_id):
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    data = f'{dia}/{mês}/{ano} às {hora_atual}'
    if request.method == 'POST':
        resposta = request.POST['P12']
        chamado.situacao = 'Chamado Concluido'
        chamado.save()
        timeline = Timeline(
            criado_por = request.user,    
            numero = chamado_id,
            data_criacao = data,
            resposta = resposta,
            situacao = f'Chamado concluido por {request.user}', 
            codigo = 4,   
        )
        timeline.save()
        return redirect('listar_chamados', 'todos')
    else:
        return render(request, 'mensagem.html')
def excluir_chamado(request, chamado_id):
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)

    # Filtra as entradas de Timeline relacionadas ao chamado
    timeline = Timeline.objects.filter(numero=chamado_id)

    # Exclui todas as entradas da Timeline relacionadas ao chamado
    timeline.delete()

    # Em seguida, exclui o próprio chamado
    chamado.delete()
    
    # Redireciona para a página de "meus_chamados" após a exclusão
    return redirect('meus_chamados', 'todos')

def reabrir_chamado(request, chamado_id):
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    data = f'{dia}/{mês}/{ano} às {hora_atual}'
    if request.method == 'POST':
        resposta = request.POST['P12']
        chamado.situacao = 'Chamado Aberto'
        chamado.save()
        timeline = Timeline(
            criado_por = request.user,    
            numero = chamado_id,
            data_criacao = data,
            resposta = resposta,
            situacao = f'Chamado reaberto por {request.user}', 
            codigo = 5,   
        )
        timeline.save()
        return redirect('meus_chamados', 'todos')
    else:
        return render(request, 'mensagem.html')
    
def finalizar_chamado(request, chamado_id):
    # Recupera o objeto Chamados com base no chamado_id
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    data = f'{dia}/{mês}/{ano} às {hora_atual}'
    chamado.situacao = 'Chamado Finalizado'
    chamado.save()
    timeline = Timeline(
        criado_por = request.user,    
        numero = chamado_id,
        data_criacao = data,
        situacao = f'Chamado finalizado por {request.user}', 
        codigo = 6,   
    )
    timeline.save()
    return redirect('meus_chamados', 'todos')
