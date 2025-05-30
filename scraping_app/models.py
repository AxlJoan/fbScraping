# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from .roles import ADMIN_ROLE, VIEWER 

class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    nombre_pagina = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clientes'

    def __str__(self):
        return self.nombre_pagina


class Coincidencias(models.Model):
    id = models.AutoField(primary_key=True)
    post_url = models.TextField(blank=True, null=True)
    usuario_url = models.TextField(blank=True, null=True)
    empleado = models.ForeignKey('Empleados', on_delete=models.SET_NULL, blank=True, null=True)
    comentario = models.ForeignKey('Comentarios', on_delete=models.SET_NULL, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'coincidencias'


class Comentarios(models.Model):
    id = models.AutoField(primary_key=True)
    post_url = models.TextField(blank=True, null=True)
    usuario = models.CharField(max_length=255, blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    usuario_url = models.TextField(blank=True, null=True)
    nombre_pagina = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comentarios'
        unique_together = (('usuario', 'comentario'),)


class Empleados(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    facebook_user = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empleados'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=50, choices=[
        (ADMIN_ROLE, 'Administrador'),
        (VIEWER, 'Visualizador'),
    ])

    def __str__(self):
        return f'{self.user.username} ({self.role})'