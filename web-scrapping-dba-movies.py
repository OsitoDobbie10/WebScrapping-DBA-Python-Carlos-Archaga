# Librerías de Web Scraping
import requests
from bs4 import BeautifulSoup
import time
import warnings
warnings.filterwarnings('ignore')
# Librerías de Procesamiento de Datos
import pandas as pd
import numpy as np
#importar crear SQLLITE
import sqlite3

accept = "application/json"
Authorization = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMGRhODQ0OWUyNWNiYjgzNGM1NDc0ZTI0NTNjYTFkNyIsIm5iZiI6MTc3OTE2MTQzNy41NTQsInN1YiI6IjZhMGJkOTVkOGZjMzhmZjJmNzhmYWI1NiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.wWKiZ_pk9N9S9e6oSQoSB0ojcau9z1z2bxzMJQYLhPI"

def obtenerAPI_peliculas(min,max):
    lista_resultados = []
    for i in range(min,max):
        url = f"https://api.themoviedb.org/3/movie/top_rated?language=es-ES&page={i}"
        headers = {"accept": accept,"Authorization": Authorization}
        response = requests.get(url, headers=headers)
        data = response.json()
        lista_resultados.extend(data['results'])
    df = pd.DataFrame(lista_resultados)
    print(f"Total de registros: {len(df)}")
    return df

def limpiar_peliculas_DF(df):
    df_clear = df.copy()
    df_clear.drop(columns=["adult", "softcore", "video", "backdrop_path", "poster_path"],inplace=True)
    nombres = {'genre_ids':'generos_id','id':'ID','title':'Titulo','original_language':'Lenguaje_Original','original_title':'Titulo_Original','overview':'Resumen',
               'popularity':'Popularidad','release_date':'fecha_realizada','vote_average':'Promedio_voto','vote_count':'Conteo_votos'}
    df_clear = df_clear.rename(columns=nombres)
    df_clear['generos_id'] = df_clear["generos_id"].str[0].astype(int)
    def valorPelicula(value):
        resultado = None
        if value > 8.8:
            resultado = 'Altamente aceptado por la critica'
        elif value <= 8.8 and value >= 8.4:
            resultado = 'Aceptado por la critica'
        elif value <8.4:
            resultado = 'Muy buena pelicula'
        return resultado
    df_clear['Critica'] = df_clear['Promedio_voto'].apply(valorPelicula)
    return df_clear

def obtenerSeries(min,max):
    lista_resultados = []
    for i in range(min,max):
        url = f"https://api.themoviedb.org/3/tv/top_rated?language=es-ES&page={i}"
        headers = {"accept": accept,"Authorization": Authorization}
        response = requests.get(url, headers=headers)
        data = response.json()
        lista_resultados.extend(data['results'])
    df = pd.DataFrame(lista_resultados)
    print(f"Total de registros: {len(df)}")
    return df

def limpiar_series_DF(df):
    df_clear = df.copy()
    df_clear.drop(columns=["adult", "backdrop_path","poster_path","softcore"],inplace=True)
    series_objeto = {
   'genre_ids':'generos_id', 'id':'ID', 'origin_country':'Pais_Origen', 'original_language':'lenguage_original', 
   'original_name':'Nombre_Original', 'overview':'Resumen', 'popularity':'Popularidad', 'first_air_date':'Fecha_primer_estreno', 
    'name':'Nombre', 'vote_average':'Promedio_voto', 'vote_count':'Conteo_votos' }
    df_clear = df_clear.rename(columns=series_objeto)
    df_clear['generos_id'] = df_clear['generos_id'].str[0].astype(int)
    df_clear['Pais_Origen'] = df_clear['Pais_Origen'].str[0]  # Convierte lista ['US'] a string 'US'
    def valorPelicula(value):
        resultado = None
        if value > 8.8:
            resultado = 'Altamente aceptado por la critica'
        elif value <= 8.8 and value >= 8.4:
            resultado = 'Aceptado por la critica'
        elif value <8.4:
            resultado = 'Muy buena pelicula'
        return resultado
    df_clear['Critica'] = df_clear['Promedio_voto'].apply(valorPelicula)
    return df_clear

def exportarCSV(df,nombre):
     df.to_csv(f'{nombre}.csv', encoding='utf-8-sig', index=False)
     print(f"✅ CSV guardado: '{nombre}.csv'")


def SQL(dba,dfpeliculas,dfseries):
    dba = f'{dba}.db'
    dfpeliculas_obj = dfpeliculas.to_dict(orient='records')
    dfseries_obj = dfseries.to_dict(orient='records')
    conect = sqlite3.connect(dba)
    print(f"🔌 Conectado a base de datos: {conect}")
    cursor = conect.cursor()
    cursor.execute('DROP TABLE IF EXISTS Peliculas')
    cursor.execute('DROP TABLE IF EXISTS Series')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Peliculas (
                ID INTEGER PRIMARY KEY,
                generos_id INTEGER,
                Titulo TEXT,
                Lenguaje_Original TEXT,
                Titulo_Original TEXT,
                Resumen TEXT,
                Popularidad REAL,
                fecha_realizada TEXT,
                Promedio_voto REAL,
                Conteo_votos INTEGER,
                Critica TEXT)
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Series (
                ID INTEGER PRIMARY KEY,
                generos_id INTEGER,
                Pais_Origen TEXT,
                Lenguaje_Original TEXT,
                Nombre_Original TEXT,
                Resumen TEXT,
                Popularidad REAL,
                Fecha_primer_estreno TEXT,
                Nombre TEXT,
                Promedio_voto REAL,
                Conteo_votos INTEGER,
                Critica TEXT
            )
        ''')

    conect.commit()
    print("✅ Tablas creadas/verificadas")

    for prop in dfpeliculas_obj:
        cursor.execute('''
            INSERT OR REPLACE INTO Peliculas
            (ID, generos_id, Titulo, Lenguaje_Original, Titulo_Original,
             Resumen, Popularidad, fecha_realizada, Promedio_voto, Conteo_votos, Critica)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prop['ID'], prop['generos_id'], prop['Titulo'],
            prop['Lenguaje_Original'], prop['Titulo_Original'],
            prop['Resumen'], prop['Popularidad'],
            prop['fecha_realizada'], prop['Promedio_voto'], prop['Conteo_votos'],
            prop['Critica']
        ))
    conect.commit()

    for prop in dfseries_obj:
        cursor.execute('''
            INSERT OR REPLACE INTO Series
            (ID, generos_id, Pais_Origen, Lenguaje_Original, Nombre_Original,
             Resumen, Popularidad, Fecha_primer_estreno, Nombre, Promedio_voto, Conteo_votos, Critica)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prop['ID'], prop['generos_id'], prop['Pais_Origen'],
            prop['lenguage_original'], prop['Nombre_Original'],
            prop['Resumen'], prop['Popularidad'],
            prop['Fecha_primer_estreno'], prop['Nombre'], prop['Promedio_voto'],
            prop['Conteo_votos'], prop['Critica']
        ))
    conect.commit()
    print(f"💾 {len(dfpeliculas_obj)} peliculas guardadas en la base de datos")
    print(f"💾 {len(dfseries_obj)} series guardadas en la base de datos")
    cursor.close()
    conect.close()
    print("🔌 Conexión a base de datos cerrada")

def main():
     peliculas = obtenerAPI_peliculas(1,13)
     df_peliculas_clean = limpiar_peliculas_DF(peliculas)
     series = obtenerSeries(1,13)
     df_series_clean = limpiar_series_DF(series)
     exportarCSV(df_peliculas_clean,'peliculas_dba_api')
     exportarCSV(df_series_clean,'series_dba_api')
     SQL('AP-DBA',df_peliculas_clean,df_series_clean)

if __name__ == "__main__":
    main()