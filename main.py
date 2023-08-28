import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import mysql.connector
import src.soporte as sp
import src.soporte_variables as var

paises = input("Especifica los paises separados por comas")
nombre_bbdd_usuario = input("Especifica el nombre de la base de datos")
contraseña_usuario = input("Especifica la contraseña de la base de datos")
user_usuario = input("Especifica el user de la base de datos")
host_usuario = input("Especifica el host de la base de datos")

lista_paises_usuario = paises.split(',')
lista_paises_final = [i.strip().lower().capitalize() for i in lista_paises_usuario]


print("Cargamos la clase")
print('-------------------------------------------')
clase = sp.Evaluacion(lista_paises_final,nombre_bbdd_usuario,contraseña_usuario,user_usuario,host_usuario)


print("Creamos el dataframe")
print('-------------------------------------------')
clase.sacar_informacion()


print("Limpiamos el dataframe")
print('-------------------------------------------')
df_final = clase.limpieza()

print("Creamos la base de datos")
print('-------------------------------------------')
clase.crear_bbdd()

print('-------------------------------------------')
print("Creamos las tablas")
print('-------------------------------------------')
clase.crear_insertar_tabla(var.query_paises)
clase.crear_insertar_tabla(var.query_universidades)

print("Insertamos los datos en la tabla paises")
print('-------------------------------------------')
for indice, fila in df_final.iterrows():
   
    query_paises = f"""
                INSERT INTO paises (nombre_pais, nombre_provincia, latitud, longitud) 
                VALUES ("{fila['country']}", "{fila['state_province']}","{fila['latitude']}","{fila['longitude']}");
                """
    
    provincias = clase.check_provincias()
    lista_provincias = [i[0] for i in provincias]
    if len(provincias) == 0 or fila['state_province'] not in lista_provincias: 
        clase.crear_insertar_tabla(query_paises)

print("Insertamos los datos en la tabla universidades")
print('-------------------------------------------')
for indice, fila in df_final.iterrows():

    query_uni = f"""
                INSERT INTO universidades (nombre_universidad, pagina_web, paises_idestado) 
                VALUES ('{fila["name"]}', '{fila["web_pages"]}', '{clase.sacar_id_estado(fila["state_province"])}');
                """
    universidades = clase.check_universidades()
    lista_universidades = [i[0] for i in universidades]
    if len(universidades) == 0 or fila['name'] not in lista_universidades: 
        clase.crear_insertar_tabla(query_uni)

print("Proceso finalizado")
print('-------------------------------------------')