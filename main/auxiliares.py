from .models import *
import random
from django.db.models import Prefetch

def get_random_color():
    while True:
        color = '#%06x' % random.randint(0, 0xFFFFFF)
        if color != '#FFFFFF':  # Exclude white color
            return color

def asignar_colores(generos):
    generos_a_actualizar = []
    for genero in generos:
        if genero.color is None:
            genero.color = get_random_color()
            generos_a_actualizar.append(genero)
    Genero.objects.bulk_update(generos_a_actualizar, ['color'])
    return 0

def asigna_imagen_album(artistas):
    artistas_a_actualizar = []
    for artista in artistas:
        albumes_del_artista = artista.albums.all()
        if albumes_del_artista.exists():
            primer_album_del_artista = albumes_del_artista.first()
            # Asegúrate de que tu modelo Album tenga un campo foto_album
            artista.imagen_album = primer_album_del_artista.foto
        else:
            artista.imagen_album = None
        
        artistas_a_actualizar.append(artista)
    
    Artista.objects.bulk_update(artistas_a_actualizar, ['imagen_album'])
    return 0
