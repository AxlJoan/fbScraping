from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UrlForm
from scraping_tools.scraping import ejecutar_scraping  # Función que llamará al script de scraping
from django.http import HttpResponse
import pandas as pd
import csv
import io
from django.contrib.auth.decorators import login_required
import os

def index(request):
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            comentarios = ejecutar_scraping(url)

            try:
                empleados_df = pd.read_csv('scraping_tools/empleados.csv')
                comentarios_df = pd.DataFrame(comentarios)
                comentarios_df['perfil_base'] = comentarios_df['perfil'].str.extract(r'(https://www\.facebook\.com/[^/?]+)')
                empleados_df['perfil'] = empleados_df['perfil'].str.strip()
                coincidencias = comentarios_df[comentarios_df['perfil_base'].isin(empleados_df['perfil'])]
                data = coincidencias[['nombre', 'texto', 'perfil']].to_dict(orient='records')
            except Exception as e:
                data = []
                print(f"Error en comparación: {e}")

            # Guardar temporalmente en la sesión (solo campos simples)
            request.session['comentarios'] = comentarios

            return render(request, 'scraping_app/index.html', {
                'form': form,
                'comentarios': comentarios,
                'data': data  # <- IMPORTANTE mandar también data
            })
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

def exportar_csv(request):
    comentarios = request.session.get('comentarios', [])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comentarios.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Comentario', 'Perfil'])
    for c in comentarios:
        writer.writerow([c['nombre'], c['texto'], c['perfil']])
    
    return response

def exportar_excel(request):
    comentarios = request.session.get('comentarios', [])
    df = pd.DataFrame(comentarios)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Comentarios')
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="comentarios.xlsx"'
    return response

@login_required
def comparar_perfiles_view(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tools_dir = os.path.join(base_dir, 'scraping_tools')

    # Rutas de archivos
    excel_path = os.path.join(tools_dir, 'comentarios_facebook.xlsx')
    csv_path = os.path.join(tools_dir, 'comentarios_facebook.csv')
    empleados_path = os.path.join(tools_dir, 'empleados.csv')

    try:
        # Intenta leer Excel, si no existe intenta con CSV
        if os.path.exists(excel_path):
            comentarios_df = pd.read_excel(excel_path)
        elif os.path.exists(csv_path):
            comentarios_df = pd.read_csv(csv_path)
        else:
            raise FileNotFoundError("No se encontró 'comentarios_facebook.xlsx' ni 'comentarios_facebook.csv'.")

        empleados_df = pd.read_csv(empleados_path)

        # Validación de columnas
        if 'perfil' not in comentarios_df.columns or 'perfil' not in empleados_df.columns:
            raise ValueError("Falta la columna 'perfil' en uno de los archivos.")

        # Extraer URLs base de comentarios
        comentarios_df['perfil_base'] = comentarios_df['perfil'].str.extract(r'(https://www\.facebook\.com/[^/?]+)')
        empleados_df['perfil'] = empleados_df['perfil'].str.strip()

        coincidencias = comentarios_df[comentarios_df['perfil_base'].isin(empleados_df['perfil'])]
        data = coincidencias[['nombre', 'texto', 'perfil']].to_dict(orient='records')

    except Exception as e:
        data = []
        print(f"⚠️ Error en comparación de perfiles: {e}")

    return render(request, 'scraping_app/index.html', {'data': data})
