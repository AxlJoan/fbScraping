# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_pagina = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    password_hash = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clientes'


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
