from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.
def cadastro (resquet):

    if resquet.method == 'GET':
        return render(resquet, 'cadastro.html')
    else:
        primeiro_nome = resquet.POST.get('primeiro_nome')
        ultimo_nome = resquet.POST.get('ultimo_nome')
        username = resquet.POST.get('username')
        senha = resquet.POST.get('senha')
        email = resquet.POST.get('email')
        confirmar_senha = resquet.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(resquet, constants.ERROR, 'A senha sua senha de confirmação não é igual')
            return redirect('/usuarios/cadastro')
        
        if len(senha) < 6:
            messages.add_message(resquet, constants.ERROR, 'Digite uma senha com mais de 6 digitos')
            return redirect('/usuarios/cadastro')

        if User.objects.filter(username=username).exists():
            messages.add_message(resquet, constants.ERROR, 'O usuario que você digitou já existe')
            return redirect('/usuarios/cadastro')
        
        try:
            user = User.objects.create_user(
                first_name = primeiro_nome,
                last_name = ultimo_nome, 
                username = username,
                password = senha, 
                email = email 
            )
            messages.add_message(resquet, constants.SUCCESS, 'Usuario cadastrado com sucesso!')
        except:
            return redirect('/usuarios/cadastro')
        
        return redirect('/usuarios/cadastro')
    

def logar(resquet):
    if resquet.method == 'GET':
        return render(resquet, 'login.html')
    
    elif resquet.method == 'POST':
        username = resquet.POST.get('username')
        senha = resquet.POST.get('senha')

        user = authenticate(username=username, password=senha)
        if user:
            login(resquet, user)
            return redirect('/exames/solicitar_exames')
        else:
            messages.add_message(resquet, constants.ERROR, 'Sua senha ou usuario está errada')
            return redirect('/usuarios/login')


