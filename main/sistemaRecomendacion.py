from main.models import *
from math import sqrt
from scipy.stats import pearsonr


def comunidad_likes(usuario):
    usuarios_like = Like.objects.filter(usuario=usuario).values_list('publicacion__usuario', flat=True)
    usuarios = Usuario.objects.exclude(id=usuario.id).filter(id__in=usuarios_like)
    comunidades_usuarios = set(list(Comunidad.objects.filter(followers__in=usuarios)))
    return comunidades_usuarios

def recomendacion_usuario(usuario):
    # Diccionario de comunidades del usuario y sus respectivos géneros
    comunidades_recomendadas = []
    comunidades_usuario = {}

    try:
        for comunidad in usuario.comunidades.all():
            comunidades_usuario[comunidad.nombre] = [genero.id for genero in comunidad.generos.all()]
    except:
        pass
    # Diccionario de comunidades de comunidad_likes y sus géneros
    otras_comunidades = {}
    comunidades_usuarios_likes = comunidad_likes(usuario)
    for comunidad in comunidades_usuarios_likes:
        otras_comunidades[comunidad.nombre] = [genero.id for genero in comunidad.generos.all()]
    # Se eliminan las comunidades del usuario de otras_comunidades
    if comunidades_usuario != {}:
        for comunidad_usuario in comunidades_usuario.keys():
            otras_comunidades.pop(comunidad_usuario, None)
    else:
        comunidades_usuario = otras_comunidades
    # Calculo de correlación de Pearson entre los géneros de los usuarios
    comunidades_recomendadas = {}
    for comunidad_usuario, generos_usuario in comunidades_usuario.items():
        for comunidad_otra, generos_otra in otras_comunidades.items():
            # Ensure both lists are of the same length by padding with zeros
            max_length = max(len(generos_usuario), len(generos_otra))
            generos_usuario += [0] * (max_length - len(generos_usuario))
            generos_otra += [0] * (max_length - len(generos_otra))
            
            # Solo se calcula la correlación si ambos usuarios tienen al menos 2 géneros en común
            if len(generos_usuario) >= 2 and len(generos_otra) >= 2:
                correlation, _ = pearsonr(generos_usuario, generos_otra)
                # Si la correlación es positiva y mayor a la actual, se actualiza
                if correlation > 0:
                    if comunidad_otra not in comunidades_recomendadas or correlation > comunidades_recomendadas[comunidad_otra]:
                        comunidades_recomendadas[comunidad_otra] = correlation
    
    comunidades_recomendadas = sorted(comunidades_recomendadas.items(), key=lambda x: x[1], reverse=True)
    comunidades_recomendadas_nombres = [comunidad[0] for comunidad in comunidades_recomendadas]
    return comunidades_recomendadas_nombres


