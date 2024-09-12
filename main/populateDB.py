#encoding:utf-8
import ssl
import os 
from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime
import time
import random
import pytz #modulo usado para cambiar la zona horaria de la noticia
#selenium 4
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time
from .models import Cancion,Album,Genero,Artista,Usuario
import os
import shutil
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

##################INICIO VARIABLES GLOBALES#################################
    
zona_horaria = pytz.timezone('Europe/Madrid')
urlbasica = 'https://www.last.fm/music'
tags_set = set()
set_artistas = set()
options = Options()
options.add_argument("--headless")
##################INICIO FUNCIONES AUXILIARES#################################

ftr = [3600,60,1] #lista auxiliar para pasar el str a segundos
def str_to_sec(str):
   return sum([a*b for a,b in zip(ftr, [int(i) for i in str.split(":")])]) 

def saveImage(url):
    nombre = url.split('/')[-1]
    urllib.request.urlretrieve(url, 'static/albums/'+nombre)
    return nombre

def rotar_proxies():
    with open("lista_proxies.txt", "r") as file:
        proxies = file.readlines()

    for proxy in proxies:
        proxy = proxy.strip()
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f'--proxy-server={proxy}')
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options, service=FirefoxService(GeckoDriverManager().install()))
            print(f"El proxy {proxy} se ha utilizado correctamente.")
        except Exception as e:
            print(f"No se pudo utilizar el proxy {proxy}: {str(e)}")
##################FIN FUNCIONES AUXILIARES#################################

##################INICIO SCRAPPING DE MUSICA#################################
def extraerMusica(driver):
    driver.get(urlbasica)
    driver.implicitly_wait(300)
    tags_principales = []
    tags_principales.extend(["https://www.last.fm/tag/reggaeton","https://www.last.fm/tag/pop","https://www.last.fm/tag/electronic"])
    time.sleep(5)
    driver.find_element(by=By.ID,value="onetrust-reject-all-handler").click()
    #Aqui se cogen las tags de la página principal y se recorren
    driver.close()
    print("TAGS PRINCIPALES: ",tags_principales)
    for tag in tags_principales:
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(60)
        extraerTodo(driver, tag)
    #llamar populates
    print("POPULATE ACABADO TODOS LOS REGISTRO INTRODUCIDOS CORRECTAMENTE")
    return 0

def extraerTodo(driver,tag):
    driver.get(tag)
    nombre = tag.split('/')[-1]
    print("-------------------- HACIENDO SCRAPPING DE LA TAG: " + nombre.upper() + " ----------------")
    print("")
    time.sleep(2)
    driver.find_element(by=By.ID,value="onetrust-reject-all-handler").click()
    time.sleep(3)
    driver.find_element(by=By.CSS_SELECTOR,value="li.navlist-item:nth-child(2) > a:nth-child(1)").click()
    #EN ESTE BUCLE FOR SE RECORREN LOS ARTISTAS, PARA CADA ARTISTA SE LLAMA AL MÉTODO EXTRAER ARTISTA QUE EXTRAE SUS CANCIONES
    i = 0
    while i < 2: 
        print("--------- ENTRANDO EN LA PAGINA DE ARTISTAS : " + str(i+1) + " ---------")
        page_content = driver.page_source
        sopa = BeautifulSoup(page_content, 'lxml')
        container = sopa.find('div', class_='container page-content')
        hrefs = ["https://www.last.fm"+artista.attrs['href'] for artista in container.find_all('a', class_='link-block-cover-link')]
        print(hrefs)
        for href in hrefs:
            sopa = BeautifulSoup(urllib.request.urlopen(href),'lxml')
            nombre_artista = sopa.find('h1',class_="header-new-title").text
            print("######## HACIENDO SCRAPPING DEL ARTISTA: " + nombre_artista.upper() + " ########")
            print("")
            if(nombre_artista in set_artistas):
                print("El artista ya ha sido introducido, se salta")
                pass
            else:
                try:
                    anyos_activo = sopa.find('dd',class_="catalogue-metadata-description").text
                except:
                    anyos_activo = "Desconocido"
                try:
                    oyentes = int(sopa.find('abbr',class_="intabbr js-abbreviated-counter")['title'].replace(',',''))
                except:
                    oyentes = 0
                try:
                    link_tags = sopa.find('div',class_="buffer-standard section-with-separator section-with-separator--xs-only").find('a',class_="tags-view-all")['href']
                    generos = extraeGeneros(link_tags)
                except:
                    generos = ["Sin generos"]
                lista_datos = extraerArtista(driver,href)
                populateArtistas(nombre_artista,oyentes,anyos_activo,generos,lista_datos)
                set_artistas.add(nombre_artista)
        try :
            driver.get("https://www.last.fm/tag/"+nombre+"/artists?page="+str(i+2))
            i+=1
            time.sleep(1)
        except :
            break
    driver.close()
    driver.quit()  # Close the driver completely
    return 0

def extraerArtista(driver,href):
    lista_datos = []
    driver.get(href)
    driver.find_element(by=By.CSS_SELECTOR,value="#top-albums > div:nth-child(2) > p:nth-child(2) > a:nth-child(1)").click()
    sopa = BeautifulSoup(driver.page_source, 'lxml')
    try:
        paginacion = int(sopa.find('ul',class_="pagination-list").find_all('li')[-2].text)
    except:
        paginacion = 1
    driver.implicitly_wait(60)
    i = 0
    while i < paginacion:#paginacion
        print("######## ENTRANDO EN LA PAGINA DE ALBUMS : " + str(i+1) + " ########")
        start_time = time.time()
        try:
            sopa = BeautifulSoup(driver.page_source, 'lxml')
            nombre_albums = sopa.find('section',id ="artist-albums-section").find('ol').find_all('li',{"itemtype":"http://schema.org/MusicAlbum"})
            hrefs_albums = ["https://www.last.fm"+album.find('a',class_="link-block-target").attrs['href'] for album in nombre_albums]
            detalles = extraerDetalles(hrefs_albums)
            lista_datos.append(detalles[0])
            if(detalles[1] == 1):
                break
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("Tiempo transcurrido en la página ", i+1, " :", elapsed_time, "seconds")
            print("")
            try:
                i+=1
                next = driver.find_element(by=By.CSS_SELECTOR,value=".pagination-next > a:nth-child(1)")
                next.click()
                time.sleep(1)
            except:
                break
        except Exception as e:
            print("Error en extraer artista:", str(e))
            break
    return lista_datos

def extraerDetalles(hrefs_albums):
    lista_albums = []
    abortado = 0
    for href in hrefs_albums:
        try:
            set_generos = set()
            sopa = BeautifulSoup(urllib.request.urlopen(href),'lxml')
            lista_canciones = []
            nombre_album = sopa.find('h1',class_="header-new-title").text
            print("-------------------- HACIENDO SCRAPPING DEL ALBUM: " + nombre_album.upper() + "------------------")
            oyentes = int(sopa.find('abbr',class_="intabbr js-abbreviated-counter")['title'].replace(',',''))
            print("         NUMERO DE OYENTES: " + str(oyentes))
            if(oyentes < 10000):
                abortado = 1
                print("El album no tiene suficientes oyentes, se salta")
                break
            try:
                duracion_total = sopa.find('div',class_="col-main upper-overview buffer-standard buffer-reset@sm").find('div',class_="metadata-column hidden-xs").find('dd',class_="catalogue-metadata-description").text.strip().split(',')[1].replace('\n','').strip()
            except:
                duracion_total = "00:00"
            try:
                imagen_album = saveImage(sopa.find('a',class_="cover-art").find('img')['src'])
            except:
                imagen_album = ""
            enlace_cancion = [nombre.find('a')['href'] for nombre in sopa.find_all('td', class_="chartlist-name")]
            print("         NUMERO DE CANCIONES: " + str(len(enlace_cancion)))
            print("")
            for cancion in enlace_cancion:
                detalle_cancion = extraerDetallesCancion(cancion)
                lista_canciones.append(detalle_cancion)
                for genero in detalle_cancion[1]:
                    set_generos.add(genero)
            id_album = populateAlbum(nombre_album,duracion_total,set_generos,imagen_album,lista_canciones)
            lista_albums.append([id_album,lista_canciones])
        except:
            continue
    return lista_albums,abortado

        

def extraerDetallesCancion(cancion):
    try:
        sopa = BeautifulSoup(urllib.request.urlopen("https://www.last.fm"+cancion),"lxml")
    except:
        nombre_cancion = "Cancion no encontrada"
        generos = ["Sin generos"]
        duracion = "00:00"
        oyentes = 0
        link_youtube = ""
        link_spotify = ""
        return nombre_cancion,generos,duracion,oyentes,link_youtube,link_spotify
    nombre_cancion = sopa.find('h1',class_="header-new-title").text
    try:
        duracion = sopa.find('dt',class_="catalogue-metadata-heading")
        if(duracion.text == "Length"):
            duracion = duracion.find_next('dd').text.strip().replace('\n','')
        else:
            duracion = "00:00"
    except:
        duracion = "00:00"
    try:
        oyentes = int(sopa.find('abbr',class_="intabbr js-abbreviated-counter")['title'].replace(',',''))

    except:
        oyentes = 0
    try:
        link_youtube = sopa.find('a',{"data-playlink-affiliate":"youtube"})['href']
        link_spotify = sopa.find('a',class_="hidden-xs play-this-track-playlink play-this-track-playlink--spotify")['href']
    except:
        link_spotify = ""
        link_youtube = ""
    try:
        link_tags = sopa.find('div',class_="row buffer-3 buffer-4@sm").find('a',class_="tags-view-all")['href']
        generos = extraeGeneros(link_tags)
    except:
        generos = ["Sin genero"]
    id_cancion = populateCancion(nombre_cancion,generos,duracion,oyentes,link_youtube,link_spotify)
    return id_cancion,generos

def extraeGeneros(href):
    sopa = BeautifulSoup(urllib.request.urlopen("https://www.last.fm"+href),'lxml')
    section = sopa.find('div',class_="col-main").find('section')
    generos = []
    for genero in section.find_all('h3',class_="big-tags-item-name"):
        texto = genero.find('a').text   
        generos.append(texto)
        if Genero.objects.filter(nombre=texto).exists():
            continue
        else:
            try:
                Genero.objects.create(nombre=texto)
            except Exception as e:
                print("Error en populate generos:", str(e))
                break
    return generos
##################FIN SCRAPPING DE MUSICA#################################

##################INICIO POPULATE DB############################

def populateCancion(nombre_cancion,generos,duracion,oyentes,link_youtube,link_spotify):
    try:
        if Cancion.objects.filter(nombre=nombre_cancion).exists():
            print("La cancion ya ha sido introducida, se salta")
            id = Cancion.objects.get(nombre=nombre_cancion).id
            return id
        else:
            objecto = Cancion.objects.create(nombre=nombre_cancion,duracion=str_to_sec(duracion),oyentes=oyentes,link_youtube=link_youtube,link_spotify=link_spotify)
            lista_generos = [Genero.objects.get(nombre=genero) for genero in generos]
            objecto.generos.set(lista_generos)
            id = objecto.id
            print(nombre_cancion.upper() + " INTRODUCIDO CORRECTAMENTE\n")
    except Exception as e:
        print("Error en populate cancion:", str(e),lista_generos)
    return id

def populateAlbum(nombre_album,duracion_total,set_generos,imagen_album,lista_canciones):
    try:
        objecto = Album.objects.create(nombre=nombre_album,duracionTotal=str_to_sec(duracion_total),foto=imagen_album)
        lista_canciones = [Cancion.objects.get(id=cancion[0]) for cancion in lista_canciones]
        lista_generos = [Genero.objects.get(nombre=genero) for genero in set_generos]
        objecto.generos.set(lista_generos)
        objecto.canciones.set(lista_canciones)
        print(nombre_album.upper() + " INTRODUCIDO CORRECTAMENTE\n")
        id = objecto.id
    except Exception as e:
        print("Error en populate album:", str(e))
    return id
def populateArtistas(nombre_artista,oyentes,anyos_activo,generos,lista_datos):
    try:
        objeto = Artista.objects.create(nombre=nombre_artista,oyentes_mensuales=oyentes,años_activo=anyos_activo)
        lista_generos = [Genero.objects.get(nombre=genero) for genero in generos]
        for lista_album in lista_datos:
            lista_albums = [Album.objects.get(id=album[0]) for album in lista_album]
        objeto.generos.set(lista_generos)
        objeto.albums.set(lista_albums)
        print(nombre_artista.upper() + " INTRODUCIDO CORRECTAMENTE\n")
    except Exception as e:
        print("Error en populate artistas:", str(e))
    return 0



#if __name__ == "__main__":   
     
def populate():
    inicio = time.time()
    print("INICIO DE POPULATE")
    driver = webdriver.Firefox(options=options)
    # Remove the contents of the static folder
    Artista.objects.all().delete()
    print("TABLA ARTISTA BORRADA")
    Cancion.objects.all().delete()
    print("TABLA CANCION BORRADA")
    Album.objects.all().delete()
    print("TABLA ALBUM BORRADA")
    Genero.objects.all().delete()
    print("TABLA GENERO BORRADA")
    folder = 'static/albums'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("CARPETA DE IMAGENES BORRADA")
    Genero.objects.create(nombre = "Sin generos")
    extraerMusica(driver)
    shutil.rmtree('publicaciones')
    schema = Schema(id_publicacion=ID(stored=True),texto=TEXT(stored = True))
    ix = create_in("publicaciones", schema)
    final = time.time()
    tiempo_transcurrido = final - inicio
    # Convertir tiempo_transcurrido a horas, minutos y segundos
    horas = int(tiempo_transcurrido / 3600)
    minutos = int((tiempo_transcurrido % 3600) / 60)
    segundos = int(tiempo_transcurrido % 60)
# Imprimir el tiempo transcurrido
    print("Tiempo transcurrido:", horas, "horas,", minutos, "minutos y", segundos, "segundos")
    print("terminado el test")
    return 0