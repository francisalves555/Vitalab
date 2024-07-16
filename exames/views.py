from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import TiposExames, PedidosExames, SolicitacaoExame, AcessoMedico
from datetime import datetime
from django.contrib import messages
from django.contrib.messages import constants
# Create your views here.

@login_required
def solicitar_exames(request):
    if request.method == 'GET':
        tipos_exames = TiposExames.objects.all()
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames})
    
    elif request.method == 'POST':
        exames_id = request.POST.getlist('exames')
        tipos_exames = TiposExames.objects.all()
        solitacao = TiposExames.objects.filter(id__in=exames_id)
        data = datetime.today().date()
        
        soma_exames = 0
        for i in solitacao:
            if i.disponivel:
                soma_exames+= i.preco

        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames, 'soma_exames': soma_exames, 'solitacao': solitacao, 'data': data})

@login_required
def fechar_pedido(request):
    exames_id = request.POST.getlist('exames')
    solicita_exame = TiposExames.objects.filter(id__in=exames_id)
    
    for exame in solicita_exame:
        if not exame.disponivel:
            messages.add_message(request, constants.ERROR, 'O EXAME NÃO ESTA DISPONIVEL!')

            return redirect('/exames/solicitar_exames/') 
    
    pedidos_exame = PedidosExames(
        usuario = request.user,
        data = datetime.now()
    )
    pedidos_exame.save()
    
    for exames in solicita_exame:
        solicita_exame_temp = SolicitacaoExame(
            usuario = request.user,
            exame = exames,
            status = 'E'
        )
        solicita_exame_temp.save()
        pedidos_exame.exames.add(solicita_exame_temp)
    pedidos_exame.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido efetuado com sucesso!')

    return redirect('/exames/gerenciar_pedidos/') 

@login_required
def gerenciar_pedidos(request):
    pedidos_exames = PedidosExames.objects.filter(usuario=request.user)

    return render(request, 'gerenciar_pedidos.html', {'pedidos_exames':pedidos_exames})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = PedidosExames.objects.get(id=pedido_id)

    if not pedido.usuario == request.user:
        return redirect('/exames/gerenciar_pedidos/')
    
    else:
        pedido.agendado = False
        pedido.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido cancelado com sucesso!')
    return redirect('/exames/gerenciar_pedidos/')

@login_required
def gerenciar_exames(request):
    exames = SolicitacaoExame.objects.filter(usuario=request.user)
    pedidos = PedidosExames.objects.filter(usuario=request.user)

    return render(request, 'gerenciar_exames.html', {'exames':exames})

@login_required
def permitir_abrir_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)

    if not exame.requer_senha:
        if not exame.resultado:
            messages.add_message(request, constants.ERROR, 'O PDF não existe, entrar em contato com a equipe')
            return redirect('/exames/gerenciar_exames/')    
        return redirect(exame.resultado.url)
    
    return redirect(f'/exames/solicitar_senha_exame/{exame_id}')

@login_required
def solicitar_senha_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if request.method == 'GET':
        return render(request, 'solicitar_senha_exame.html', {'exame':exame})
    elif request.method =='POST':
        senha = request.POST.get('senha')
        if senha == exame.senha:
            return redirect(exame.resultado.url)
        
        messages.add_message(request, constants.ERROR, 'A senha do PDF é invalida')
        return redirect (f'/exames/solicitar_senha_exame/{exame_id}')
    

@login_required
def gerar_acesso_medico(request):
    if request.method == "GET":
        acessos_medicos = AcessoMedico.objects.filter(usuario=request.user)
        return render(request, 'gerar_acesso_medico.html', {'acessos_medicos': acessos_medicos})
    elif request.method == "POST":
        identificacao = request.POST.get('identificacao')
        tempo_de_acesso = request.POST.get('tempo_de_acesso')
        data_exame_inicial = request.POST.get("data_exame_inicial")
        data_exame_final = request.POST.get("data_exame_final")

        acesso_medico = AcessoMedico(
            usuario = request.user,
            identificacao = identificacao,
            tempo_de_acesso = tempo_de_acesso,
            data_exames_iniciais = data_exame_inicial,
            data_exames_finais = data_exame_final,
            criado_em = datetime.now()
        )

        acesso_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Acesso gerado com sucesso')
        return redirect('/exames/gerar_acesso_medico')
    
def acesso_medico(request, token):
    acesso_medico = AcessoMedico.objects.get(token=token)
    if acesso_medico.status == 'Expirado':
        messages.add_message(request, constants.ERROR, 'Esse tooken já expirou solicite outros')
        return redirect('/usuarios/login/')
    
    pedidos = PedidosExames.objects.filter(usuario = acesso_medico.usuario).filter(data__gte=acesso_medico.data_exames_iniciais).filter(data__lte=acesso_medico.data_exames_finais)

    return render(request, 'acesso_medico.html', {'pedidos':pedidos})
