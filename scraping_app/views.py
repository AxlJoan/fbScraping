from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UrlForm
from scraping_tools.scraping import ejecutar_scraping  # Función que llamará al script de scraping

def index(request):
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            # Llamar a la función de scraping con la URL
            comentarios = ejecutar_scraping(url)  # Pasamos la URL al scraping
            return render(request, 'scraping_app/index.html', {'form': form, 'comentarios': comentarios})
    else:
        form = UrlForm()
    
    return render(request, 'scraping_app/index.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'scraping_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('index')
    return render(request, 'scraping_app/register.html')
