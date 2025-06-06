"""
URL configuration for scraping_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from scraping_app import views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login'), name='root_redirect'),
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('exportar-csv/', views.exportar_csv, name='exportar_csv'),
    path('exportar-pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('exportar-word/', views.exportar_word, name='exportar_word'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
    path('buscar-comentario/', views.buscar_comentario, name='buscar_comentario'),
]