import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import mysql.connector
import src.soporte_variables as var

class Evaluacion():
    def __init__(self,lista_paises,nombre_bbdd,contraseña,valor_user='root',valor_host='localhost',dataframe=pd.DataFrame()):
        self.lista_paises = lista_paises
        self.nombre_bbdd = nombre_bbdd
        self.contraseña = contraseña
        self.valor_user = valor_user
        self.valor_host = valor_host
        self.dataframe = dataframe

    def sacar_informacion(self):
        """Esta función saca toda la información de una api  de los paises definidos.
        Args:
            self: propia del constructor.
        return: aunque esta función no devuelve nada, genera un dataframe con la información actualizada de los paises seleccionados.
        """
        df = pd.DataFrame()
        for pais in self.lista_paises:
            api_url = f"http://universities.hipolabs.com/search?country={pais}"
            response = requests.get(api_url)
            if response.status_code != 200:
                print(response.reason)
                print(response.status_code)
                break
            df_pais = pd.json_normalize(response.json())
            df = pd.concat([df, df_pais], axis = 0)
        self.dataframe = df

    def limpieza(self):
        """Esta función incluye todo el proceso de limpiza del dataframe.
        Args:
            self: propia del constructor.
        return: esta función devuelve el dataframe limpio.
        """
        nuevas_columna = {col: col.replace("-", "_") for col in self.dataframe.columns}
        self.dataframe.rename(columns= nuevas_columna, inplace = True)

        self.dataframe.drop('domains',axis=1,inplace=True)

        df_explode = self.dataframe.explode('web_pages')
        self.dataframe = df_explode

        duplicados = self.dataframe.duplicated(subset='name').sum()
        if duplicados != 0:
            self.dataframe.drop_duplicates(subset='name',inplace=True)

        self.dataframe['state_province'].replace({None},np.nan,inplace=True)
        self.dataframe['state_province'].replace(np.nan,'Unknown',inplace=True)

        self.dataframe['state_province'].replace(var.cambios,inplace=True)

        self.dataframe['name'] = self.dataframe['name'].str.replace("'", '')

        provincias = list(self.dataframe['state_province'].unique())
        df_provincias = pd.DataFrame(provincias,columns=['state_province'])
        df_provincias[['latitude','longitude']] = df_provincias['state_province'].apply(self.localizacion).apply(pd.Series)
        df_unido = self.dataframe.merge(df_provincias,how='left',on = 'state_province')
        self.dataframe = df_unido
        return df_unido
    
    def localizacion(self,elemento):
        """Esta función extrae la latitud y la longitud de una población dada.

        Args:
            elemento (str): población de la cual queremos saber sus coordenadas.

        Returns: devuelve la longitud y la latitud, o en el caso de que no haya población devuelve 0.0/0.0
        """
        if elemento != 'Unknown':
            geo = Nominatim(user_agent = 'Monica')
            localizacion = geo.geocode(elemento)
            return localizacion[1][0], localizacion[1][1]
        else:
            return 0.0, 0.0

    def crear_bbdd(self):
        ''' 
        Esta función crea una base de datos con el nombre especificado.
        Args:
            self: propia del constructor.
        return: aunque no tiene return, crea una base de datos en MySQL.
        '''
        mydb = mysql.connector.connect(
            host=self.valor_host,
            user=self.valor_user,
            password=self.contraseña)
        print("Conexión realizada con éxito")
            
        mycursor = mydb.cursor()

        try:
            mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.nombre_bbdd};")
            print(mycursor)
        except mysql.connector.Error as err:
            print(err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)

    def crear_insertar_tabla(self, query):
        ''' 
    Esta función ejecuta una query dada en MySQL.
    Args:
        self: propia del constructor.
        query(str): query que queremos ejecutar.
    return: aunque no tiene return, ejecuta la query en MySQL, independiemente de que sea creación o insercción de tablas.
        '''
        cnx = mysql.connector.connect(host=self.valor_host,
            user=self.valor_user,
            password=self.contraseña, database= self.nombre_bbdd)
                                        
        mycursor = cnx.cursor()
        
        try: 
            mycursor.execute(query)
            cnx.commit() 
    
        except mysql.connector.Error as err:
            print(err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)

    def check_provincias(self):
        """ Esta función extrae todas las provincias que hay una tabla de MySQL.
        Args:
            self: propia del constructor.
        return: devuelve una lista de tuplas con todos los nombres de las provincias que hay en la tabla.
        """
        cnx = mysql.connector.connect(host=self.valor_host,
            user=self.valor_user,
            password=self.contraseña, database= self.nombre_bbdd)
        mycursor = cnx.cursor()


        query_existe_provincia = f"""
                SELECT DISTINCT nombre_provincia FROM paises
                """
        mycursor.execute(query_existe_provincia)
        provincia = mycursor.fetchall()
        return provincia
    
    def check_universidades(self):
        """ Esta función extrae todas las universidades que hay una tabla de MySQL.
            Args:
                self: propia del constructor.
            return: devuelve una lista de tuplas con todos los nombres de las universidades que hay en la tabla.
            """
        cnx = mysql.connector.connect(host=self.valor_host,
            user=self.valor_user,
            password=self.contraseña, database= self.nombre_bbdd)
        mycursor = cnx.cursor()


        query_existe_uni = f"""
                SELECT DISTINCT nombre_universidad FROM universidades
                """
        mycursor.execute(query_existe_uni)
        unis = mycursor.fetchall()
        return unis
    
    
    def sacar_id_estado(self,estado):
        """Esta función extrae el id de un estado dado.

        Args:
            self: propia del constructor.
            estado (str): el estado del cual queremos saber su id.

        Returns: devuelve el id del estado especificado.
        """
        mydb = mysql.connector.connect(host=self.valor_host,
            user=self.valor_user,
            password=self.contraseña, database= self.nombre_bbdd)
        mycursor = mydb.cursor()

        try:
            query_sacar_id = f"SELECT idestado FROM paises WHERE nombre_provincia = '{estado}'"
            mycursor.execute(query_sacar_id)
            id_ = mycursor.fetchall()[0][0]
            return id_
        
        except: 
             return "Sorry, no tenemos ese estado en la BBDD y por lo tanto no te podemos dar su id."
