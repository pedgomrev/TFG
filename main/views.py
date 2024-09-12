from django.shortcuts import render
from django.urls import reverse
from main.models import *
from main.sistemaRecomendacion import *
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from main.populateDB import populate
from django.http import HttpResponse
from datetime import datetime
import re
from django.contrib.auth.hashers import check_password
from main.auxiliares import *
from django.core.paginator import Paginator
from main.forms import *
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.forms.models import model_to_dict
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in,open_dir
from whoosh.qparser import QueryParser
from whoosh.query import Regex

def populateDB(request):
    populate()
    usuario_sesion = Usuario.objects.get(id=request.session.get('user_id'))
    canciones = Cancion.objects.count()
    albumes = Album.objects.count()
    artistas = Artista.objects.count()
    generos = Genero.objects.count()
    contexto = {
        'canciones': canciones,
        'albumes': albumes,
        'artistas': artistas,
        'generos': generos,
        'id_usuario': int(usuario_sesion.id),
    }
    return render(request, 'populate.html', {'STATIC_URL':settings.STATIC_URL,'contexto':contexto})
###############################################################################################################################################
#                                                                                                                                             #
#                                       Funciones para apartado registro e inicio sesion                                                      #
###############################################################################################################################################
def inicioSesion(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('index')
    formulario = AuthenticationForm()
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        usuario = request.POST['username']
        contraseña = request.POST['password']
        if usuario is not None:
            if contraseña is not None:
                user = Usuario.objects.get(apodo=usuario)
                if check_password(contraseña, user.contraseña):
                    print("Usuario autenticado")
                    request.session['user_id'] = user.id
                    return HttpResponseRedirect('index')
            else:
                return render(request, 'login.html', {'form':formulario,'error': "Contraseña incorrecta"})
        else:
            return render(request, 'login.html', {'form':formulario,'error': "Usuario incorrecto"})
    return render(request,'login.html',{'form':formulario})
def cambioContraseña(request):
    errors = []
    if request.method == 'POST':
        try:
            apodo = request.POST.get('usuario')
            usuario = Usuario.objects.get(apodo = apodo)
        except:
            errors.append("No se ha encontrado el usuario")
            return render(request, 'cambioContraseña.html', {'error': errors})
        nueva_contraseña = request.POST.get('nueva_contraseña')
        confirmar_contraseña = request.POST.get('password-confirm')
        if nueva_contraseña != confirmar_contraseña:
            errors.append('Las contraseñas no coinciden')
            return render(request, 'cambioContraseña.html', {'error': errors})
        else:
            usuario.contraseña = nueva_contraseña
            usuario.save()
            print(f"Contraseña cambiada correctamente a {nueva_contraseña}")
            request.session['user_id'] = usuario.id
            return HttpResponseRedirect('index')
    return render(request, 'cambioContraseña.html')
        
def registro(request):
    errors = []
    if request.method == "POST":
            try:
                nombre = request.POST.get('nombre')
            except Exception as e:
                errors.append("Nombre :" + str(e))
                return render(request, 'registro.html', {'error': errors})
            try:
                apellidos = request.POST.get('apellidos')
            except Exception as e:
                errors.append("Apellidos :" + str(e))
                return render(request, 'registro.html', {'error': errors})

            try:
                correo = request.POST.get('email')
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo):
                    errors.append('El correo electrónico no es válido.')
                if Usuario.objects.filter(email=correo).exists():
                    errors.append('El correo electrónico ya está en uso.')
            except Exception as e:
                errors.append("Correo :" + str(e))
                return render(request, 'registro.html', {'error': errors})

            try:
                usuario = request.POST.get('username')
                if Usuario.objects.filter(apodo=usuario).exists():
                    errors.append('El nombre de usuario ya está en uso.')
            except Exception as e:
                errors.append("Usuario :" + str(e))
                return render(request, 'registro.html', {'error': errors})

            try:
                fecha_nacimiento = request.POST.get('fecha_nacimiento')
                fecha_actual = datetime.now().date()
                fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()  # Convertir a objeto datetime
                fecha_nacimiento = datetime.strptime(fecha_nacimiento.strftime('%d/%m/%Y'),'%d/%m/%Y').date()  # Convertir a formato 'dd/mm/yyyy'
                edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
                if edad < 16:
                    errors.append('Debes tener al menos 16 años para registrarte.')
            except Exception as e:
                errors.append("Fecha Nacimiento" + str(e))
                return render(request, 'registro.html', {'error': errors})

            try:
                contraseña = request.POST.get('password')
            except Exception as e:
                errors.append("Contraseña : " + str(e))
                return render(request, 'registro.html', {'error': errors})

            try:
                confirm_contraseña = request.POST.get('password-confirm')
                if contraseña != confirm_contraseña:
                    errors.append('Las contraseñas no coinciden.')
            except Exception as e:
                errors.append("Confirmar Contraseña : " + str(e))
                return render(request, 'registro.html', {'error': errors})
            if not all([nombre, apellidos, correo, usuario, fecha_nacimiento, contraseña, confirm_contraseña]):
                errors.append('Todos los campos son obligatorios. faltan: ' + ', '.join([campo for campo in ['Nombre', 'Apellidos', 'Correo electrónico', 'Nombre de usuario', 'Fecha de nacimiento', 'Contraseña', 'Confirmar contraseña'] if not eval(campo.lower())]))
            if errors:
                return render(request, 'registro.html', {'error': errors})

            user = Usuario.objects.create(nombre = nombre,apellidos = apellidos,fecha_nacimiento = fecha_nacimiento,apodo=usuario, email=correo, contraseña=contraseña)   
            user.save()       
            return HttpResponseRedirect('inicioSesion')
    else:
        return render(request, 'registro.html')

def index(request):
    user_id = request.session.get('user_id')
    usuario = Usuario.objects.get(id=user_id)
    vista_tipo = request.GET.get('vista')
    if vista_tipo == 'siguiendo':
        publicaciones = Publicacion.objects.filter(usuario__in=usuario.follows.all()).order_by('-fecha')
    else:
        publicaciones = Publicacion.objects.order_by('-fecha').all()
    likes = Like.objects.filter(usuario=usuario).values_list('publicacion_id', flat=True)
    comunidades_recomendadas = Comunidad.objects.filter(nombre__in = recomendacion_usuario(usuario))
    paginatorRecomendadas = Paginator(comunidades_recomendadas, 1)  # Muestra 5 géneros por página
    page_numberRecomendadas = request.GET.get('pageComunidades_recomendadas')
    comunidades_recomendadas = paginatorRecomendadas.get_page(page_numberRecomendadas)
    for publicacion in publicaciones:
        publicacion.ya_dio_like = publicacion.id in likes
    contexto = {
        'nombre': usuario.apodo,
        'usuario': usuario,
        'id_usuario': int(usuario.id),
        'usuario_sesion': usuario,
        'publicaciones': publicaciones,
        'likes': likes,
        'comunidades_recomendadas': comunidades_recomendadas,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        partial = request.GET.get('partial')
        if partial == 'comunidades_recomendadas':
            return render(request, 'partials/comunidades_recomendadas_list_partial.html', {'contexto': contexto})
    return render(request,'index.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

###############################################################################################################################################
#                                                                                                                                             #
#                                       Funciones para apartado perfil y manejo de perfiles                                                   #
###############################################################################################################################################
def perfil(request,id):
    usuario = Usuario.objects.get(id=id)
    usuario_sesion = Usuario.objects.get(id=request.session.get('user_id'))
    if request.method == 'POST':
        try:
            apodo = request.POST.get('apodo')
            if apodo != usuario.apodo:
                usuario.apodo = apodo
            else:
                print("No se ha cambiado el apodo")
        except Exception as e:
            pass
        try:
            foto_perfil = request.FILES.get('input_imagen')
            if foto_perfil:  # Verificar si se ha cargado una nueva imagen
                static_folder = os.path.join(settings.BASE_DIR, 'static')
                new_image_path = os.path.join(static_folder, 'fotos_perfil', foto_perfil.name)
                with open(new_image_path, 'wb') as file:
                    file.write(foto_perfil.read())
                
                if usuario.foto_perfil:  # Verificar si ya existe una imagen de perfil
                    actual_image_path = os.path.join(static_folder,usuario.foto_perfil.name)
                    if os.path.exists(actual_image_path):
                        os.remove(actual_image_path)
                
                usuario.foto_perfil = 'fotos_perfil/' + foto_perfil.name
                print("Se ha cambiado la imagen")
            else:
                print("No se ha cargado una nueva imagen")
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
            
        usuario.save()  # Guardar el usuario una sola vez después de procesar todas las modificaciones
    lista_comunidades = Comunidad.objects.filter(followers__in=[usuario.id])
    paginatorComunidad = Paginator(lista_comunidades, 5)  # Muestra 5 géneros por página
    page_numberComunidad = request.GET.get('pageComunidad')
    comunidades = paginatorComunidad.get_page(page_numberComunidad)
    posts = Publicacion.objects.filter(usuario=usuario).order_by('-fecha')
    paginatorPost = Paginator(posts, 1)  # Muestra 1 post por página
    page_numberPost = request.GET.get('pagePublicacion')
    posts = paginatorPost.get_page(page_numberPost)
    listas_reproduccion_bd = ListaReproduccion.objects.filter(usuario=usuario)
    paginatorLista = Paginator(listas_reproduccion_bd, 5)  # Muestra 5 listas por página
    page_numberLista = request.GET.get('pageLista')
    listas_reproduccion = paginatorLista.get_page(page_numberLista)
    likes = Like.objects.filter(usuario=usuario_sesion).values_list('publicacion_id', flat=True)
    for publicacion in posts:
        publicacion.ya_dio_like = publicacion.id in likes
    contexto = {
        'nombre': usuario.apodo,
        'foto_perfil': usuario.foto_perfil,
        'seguidores': usuario.followers.count(),
        'lista_seguidores': usuario.followers.all(),
        'seguidos': usuario.follows.count(),
        'lista_seguidos': usuario.follows.all(),
        'id_usuario': int(usuario.id),
        'usuario_sesion': usuario_sesion,
        'ya_sigue': usuario_sesion in usuario.followers.all(),
        'comunidades': comunidades,
        'publicaciones': posts,
        'listas_reproduccion': listas_reproduccion,
        'numero_listas': listas_reproduccion_bd.count(),
        'artistas_seguidos': usuario.artistas_seguidos.count(),
        'lista_artistas_seguidos': usuario.artistas_seguidos.all(),
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        partial = request.GET.get('partial')
        if partial == 'comunidad':
            return render(request, 'partials/comunidades_list_partial.html', {'contexto': contexto})
        elif partial == 'publicacion':
            return render(request, 'partials/publicaciones_list_partial.html', {'contexto': contexto})
        elif partial == 'lista':
            return render(request, 'partials/lista_list_partial.html', {'contexto': contexto})
    return render(request,'perfil_personal.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

def perfil_artista(request,id):
    artista = Artista.objects.get(id=id)
    usuario_sesion = Usuario.objects.get(id=request.session.get('user_id'))
    album_fondo = Album.objects.filter(artista=artista).first().foto
    albums = artista.albums.all()
    paginatorAlbum = Paginator(albums, 5)  # Muestra 5 albums por página
    page_numberAlbum = request.GET.get('pageAlbum')
    albums = paginatorAlbum.get_page(page_numberAlbum)
    generos = artista.generos.all()
    paginatorGenero = Paginator(generos, 5)  # Muestra 5 géneros por página
    page_numberGenero = request.GET.get('pageGenero')
    generos = paginatorGenero.get_page(page_numberGenero)
    contexto = {
        'nombre': artista.nombre.upper(),
        'artista': artista,
        'album_fondo': album_fondo,
        'usuario_sesion': usuario_sesion,
        'albums': albums,
        'generos': generos,
        'ya_sigue': artista in usuario_sesion.artistas_seguidos.all(),
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        partial = request.GET.get('partial')
        if partial == 'album':
            return render(request, 'partials/albums_list_partial.html', {'contexto': contexto})
        elif partial == 'genero':
            return render(request, 'partials/generos_list_partial.html', {'contexto': contexto})
    return render(request,'perfil_artista.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

def seguir(request, id):
    # Verificar si el usuario está autenticado
    if 'user_id' not in request.session:
        # Manejar el caso en que el usuario no está autenticado
        return HttpResponseRedirect('/inicioSesion')
   
    # Obtener el usuario actual
    usuario_sesion = get_object_or_404(Usuario, id=request.session['user_id'])

    # Obtener el usuario a seguir o manejar el caso si no existe
    usuario_seguir = get_object_or_404(Usuario, id=id)

    # Verificar si el usuario ya sigue al usuario a seguir
    if usuario_sesion in usuario_seguir.followers.all():
        # Manejar el caso en que el usuario ya sigue al usuario a seguir
        usuario_seguir.followers.remove(usuario_sesion)
        usuario_sesion.follows.remove(usuario_seguir)
        return redirect(request.META.get('HTTP_REFERER', 'default_if_none'))

    # Verificar que los usuarios se obtuvieron correctamente
    if usuario_sesion and usuario_seguir:
        # Seguir al usuario
        usuario_seguir.followers.add(usuario_sesion)
        usuario_sesion.follows.add(usuario_seguir)

        # Guardar los cambios
        usuario_sesion.save()
        usuario_seguir.save()

    # Redirigir a la página de perfil del usuario seguido
        return redirect(request.META.get('HTTP_REFERER', 'default_if_none'))


def seguir_artista(request, id):
    # Verificar si el usuario está autenticado
    if 'user_id' not in request.session:
        # Manejar el caso en que el usuario no está autenticado
        return HttpResponseRedirect('/inicioSesion')
   
    # Obtener el usuario actual
    usuario_sesion = get_object_or_404(Usuario, id=request.session['user_id'])

    # Obtener el artista a seguir o manejar el caso si no existe
    artista_seguir = get_object_or_404(Artista, id=id)
    # Verificar si el usuario ya sigue al artista a seguir
    if artista_seguir in usuario_sesion.artistas_seguidos.all():
        # Manejar el caso en que el usuario ya sigue al artista a seguir
        usuario_sesion.artistas_seguidos.remove(artista_seguir)
        return redirect(request.META.get('HTTP_REFERER', 'default_if_none'))
    else:
        # Seguir al artista
        usuario_sesion.artistas_seguidos.add(artista_seguir)
        # Guardar los cambios
        usuario_sesion.save()
        # Redirigir a la página de perfil del artista seguido
        return redirect(request.META.get('HTTP_REFERER', 'default_if_none'))

###############################################################################################################################################
#                                                                                                                                             #
#                                       Funciones para apartado explora y manejo de búsquedas                                                 #
###############################################################################################################################################
def explora(request):
    usuario_sesion = Usuario.objects.get(id=request.session.get('user_id'))

    lista_generos = Genero.objects.all()
    asignar_colores(lista_generos)
    paginatorGenero = Paginator(lista_generos, 5)  # Muestra 5 géneros por página
    page_numberGenero = request.GET.get('pageGenero')
    generos = paginatorGenero.get_page(page_numberGenero)

    lista_albums = Album.objects.all()
    paginatorAlbum = Paginator(lista_albums, 5)  # Muestra 5 géneros por página
    page_numberAlbum = request.GET.get('pageAlbum')
    albums = paginatorAlbum.get_page(page_numberAlbum)

    lista_artistas = Artista.objects.all()
    paginatorArtista = Paginator(lista_artistas, 5)  # Muestra 5 géneros por página
    page_numberArtista = request.GET.get('pageArtista')
    artistas = paginatorArtista.get_page(page_numberArtista)

    lista_usuarios = Usuario.objects.all()
    lista_usuarios = lista_usuarios.exclude(id=request.session.get('user_id'))
    lista_usuarios = lista_usuarios.exclude(id__in=usuario_sesion.follows.all())
    paginatorUsuario = Paginator(lista_usuarios, 5)  # Muestra 5 géneros por página
    page_numberUsuario = request.GET.get('pageUsuario')
    usuarios = paginatorUsuario.get_page(page_numberUsuario)
    lista_comunidades = Comunidad.objects.all()
    paginatorComunidad = Paginator(lista_comunidades, 5)  # Muestra 5 géneros por página
    page_numberComunidad = request.GET.get('pageComunidad')
    comunidades = paginatorComunidad.get_page(page_numberComunidad)


    contexto = {
        'comunidades': comunidades,
        'generos': generos,
        'albums': albums,
        'artistas': artistas,
        'usuarios': usuarios,
        'usuario_sesion': usuario_sesion,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        partial = request.GET.get('partial')
        if partial == 'genero':
            return render(request, 'partials/generos_list_partial.html', {'contexto': contexto})
        elif partial == 'album':
            return render(request, 'partials/albums_list_partial.html', {'contexto': contexto})
        elif partial == 'artista':
            return render(request, 'partials/artistas_list_partial.html', {'contexto': contexto})
        elif partial == 'usuario':
            return render(request, 'partials/usuarios_list_partial.html', {'contexto': contexto})
        elif partial == 'comunidad':
            return render(request, 'partials/comunidades_list_partial.html', {'contexto': contexto})
    else:
        return render(request, 'explora.html', {'STATIC_URL': settings.STATIC_URL, 'contexto': contexto})
    

def ver_mas(request, tipo):
    usuario_sesion = Usuario.objects.get(id=request.session.get('user_id'))
    if tipo == 'comunidades':
        contexto = {
            'contenido': Comunidad.objects.all(),
            'usuario_sesion': usuario_sesion,
            'conteo': Comunidad.objects.count(),
            'tipo': 'comunidades',
        }
        # Buscar y pasar datos de comunidades
    elif tipo == 'generos':
        contexto = {
            'contenido': Genero.objects.all(),
            'conteo': Genero.objects.count(),
            'tipo': 'generos',
            'usuario_sesion': usuario_sesion,

        }
        # Buscar y pasar datos de géneros
    elif tipo == 'artistas':
        contexto = {
            'contenido': Artista.objects.all(),
            'conteo': Artista.objects.count(),
            'usuario_sesion': usuario_sesion,
            'tipo': 'artistas',
        }
        # Manejar caso en que el tipo no es válido
    elif tipo == 'albums':
        contexto = {
            'contenido': Album.objects.all(),
            'conteo': Album.objects.count(),
            'tipo': 'albums',
            'usuario_sesion': usuario_sesion,
        }
    elif tipo == 'usuarios':
        contexto = {
            'contenido': Usuario.objects.all(),
            'conteo': Usuario.objects.count(),
            'tipo': 'usuarios',
            'usuario_sesion': usuario_sesion,
        }
    return render(request,'ver_mas.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

def detalles(request,tipo,id):
    usuario = Usuario.objects.get(id=request.session.get('user_id'))
    if tipo == 'genero':
        objeto = Genero.objects.get(id=id)
        contexto = {
            'nombre': objeto.nombre,
            'genero': objeto,
            'usuario_sesion': usuario,
        }
        lista_artistas = Artista.objects.filter(generos__in=[objeto])
        if len(lista_artistas) != 0:
            paginatorArtista = Paginator(lista_artistas, 5)  # Muestra 5 géneros por página
            page_number = request.GET.get('pageArtista')
            artistas = paginatorArtista.get_page(page_number)
            contexto['artistas'] = artistas

        lista_albums = Album.objects.filter(generos__in=[objeto])
        if len(lista_albums) != 0:
            paginatorAlbums = Paginator(lista_albums, 5)  # Muestra 5 géneros por página
            page_number = request.GET.get('pageAlbum')
            albums = paginatorAlbums.get_page(page_number)
            contexto['albums'] = albums
        lista_comunidades = Comunidad.objects.filter(generos__in=[objeto])
        if len(lista_comunidades) != 0:
            paginatorComunidad = Paginator(lista_comunidades, 5)
            page_number = request.GET.get('pageComunidad')
            comunidades = paginatorComunidad.get_page(page_number)
            contexto['comunidades'] = comunidades

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            partial = request.GET.get('partial')
            if partial == 'album':
                return render(request, 'partials/albums_list_partial.html', {'contexto': contexto})
            elif partial == 'comunidad':
                return render(request, 'partials/comunidades_list_partial.html', {'contexto': contexto})
            elif partial == 'artista':
                return render(request, 'partials/artistas_list_partial.html', {'contexto': contexto})
        return render(request,'detalles_genero.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})
    
    elif tipo == 'album':
        objeto = Album.objects.get(id=id)
        canciones = Cancion.objects.filter(album=objeto)
        artistas = Artista.objects.filter(albums__in=[objeto])
        duracionTotal = sum([cancion.duracion for cancion in canciones])
        duracionTotal = f"{duracionTotal // 3600} min {(duracionTotal % 3600) // 60} s"
        contexto = {
            'nombre': objeto.nombre,
            'album': objeto,
            'canciones': canciones,
            'artistas' : artistas,
            'duracionTotal': duracionTotal,
            'usuario_sesion': usuario,
        }
        return render(request,'detalles_album.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})
    
def buscar(request):
    query = request.GET.get('q', '')
    contexto = {}
    ix = open_dir("publicaciones")
    usuarios_list = Usuario.objects.filter(Q(apodo__icontains=query) | Q(nombre__icontains=query)).distinct()
    if(len(usuarios_list) != 0):
        paginatorUsuario = Paginator(usuarios_list, 5)
        page_numberUsuario = request.GET.get('pageUsuario')
        usuarios = paginatorUsuario.get_page(page_numberUsuario)
        contexto['usuarios'] = usuarios

    comunidades_list = Comunidad.objects.filter(Q(nombre__icontains=query) | Q(generos__nombre__icontains=query)).distinct()
    if(len(comunidades_list) != 0):
        paginatorComunidad = Paginator(comunidades_list, 5)
        page_numberComunidad = request.GET.get('pageComunidad')
        comunidades = paginatorComunidad.get_page(page_numberComunidad)
        contexto['comunidades'] = comunidades
    generos_list = Genero.objects.filter(nombre__icontains=query).distinct()
    if(len(generos_list) != 0):
        paginatorGenero = Paginator(generos_list, 5)
        page_numberGenero = request.GET.get('pageGenero')
        generos = paginatorGenero.get_page(page_numberGenero)
        contexto['generos'] = generos

    artistas_list = Artista.objects.filter(Q(nombre__icontains=query) | Q(generos__nombre__icontains=query) |  Q(albums__nombre__icontains=query)).distinct()
    if(len(artistas_list) != 0):
        paginatorArtista = Paginator(artistas_list, 5)
        page_numberArtista = request.GET.get('pageArtista')
        artistas = paginatorArtista.get_page(page_numberArtista)
        contexto['artistas'] = artistas

    canciones_list = Cancion.objects.filter(Q(nombre__icontains=query) | Q(generos__nombre__icontains=query)).distinct()
    if(len(canciones_list) != 0):
        paginatorCancion = Paginator(canciones_list, 5)  
        page_numberCancion = request.GET.get('pageCancion')
        canciones = paginatorCancion.get_page(page_numberCancion)
        contexto['canciones'] = canciones

    albums_list = Album.objects.filter(Q(nombre__icontains=query) | Q(generos__nombre__icontains=query) | Q(canciones__nombre__icontains=query)).distinct()
    if(len(albums_list) != 0):
        paginatorAlbum = Paginator(albums_list, 5)  
        page_numberAlbum = request.GET.get('pageAlbum')
        albums = paginatorAlbum.get_page(page_numberAlbum)
        contexto['albums'] = albums
    usuario_sesion = Usuario.objects.get(id = request.session.get('user_id'))
    with ix.searcher() as searcher:
        # Crea una consulta Regex para buscar cualquier ocurrencia del término en el texto
        regex_query = Regex("texto", f".*{query}.*")
        results = searcher.search(regex_query)
        
        # Obtener los IDs de las publicaciones de los resultados
        idResultados = [int(result['id_publicacion']) for result in results]
        
        # Filtrar las publicaciones en Django usando los IDs obtenidos
        publicaciones = Publicacion.objects.filter(id__in=idResultados)
        
        # Paginar las publicaciones
        paginatorPublicacion = Paginator(publicaciones, 1)  
        page_numberPublicacion = request.GET.get('pagePublicacion')
        publicaciones = paginatorPublicacion.get_page(page_numberPublicacion)
        
        # Pasar las publicaciones al contexto
        contexto['publicaciones'] = publicaciones

    ix.close()

    contexto['usuario_sesion'] = usuario_sesion
    contexto['query'] = query
    likes = Like.objects.filter(usuario=usuario_sesion).values_list('publicacion_id', flat=True)
    for publicacion in publicaciones:
        publicacion.ya_dio_like = publicacion.id in likes
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        partial = request.GET.get('partial')
        if partial == 'usuario':
            return render(request, 'partials/usuarios_list_partial.html', {'contexto': contexto})
        elif partial == 'comunidade':
            return render(request, 'partials/comunidades_list_partial.html', {'contexto': contexto})
        elif partial == 'genero':
            return render(request, 'partials/generos_list_partial.html', {'contexto': contexto})
        elif partial == 'artista':
            return render(request, 'partials/artistas_list_partial.html', {'contexto': contexto})
        elif partial == 'cancion':
            return render(request, 'partials/canciones_list_partial.html', {'contexto': contexto})
        elif partial == 'album':
            return render(request, 'partials/albums_list_partial.html', {'contexto': contexto})
        elif partial == 'publicacion':
            return render(request, 'partials/publicaciones_list_partial.html', {'contexto': contexto})
    return render(request, 'busqueda.html', {'STATIC_URL':settings.STATIC_URL, 'contexto':contexto})


###############################################################################################################################################
#                                                                                                                                             #
#                                       Funciones para la creación de comunidades y manejo de comunidades                                     #
###############################################################################################################################################

def comunidades(request):
    usuario_sesion = Usuario.objects.get(id = request.session.get('user_id'))
    comunidades_recomendadas = Comunidad.objects.filter(nombre__in = recomendacion_usuario(usuario_sesion))
    paginatorRecomendadas = Paginator(comunidades_recomendadas, 1)  # Muestra 5 géneros por página
    page_numberRecomendadas = request.GET.get('pageComunidades_recomendadas')
    comunidades_recomendadas = paginatorRecomendadas.get_page(page_numberRecomendadas)
    if request.method == "POST":
        formulario = request.POST
        errors = crear_comunidad(request,formulario)
        if(errors != []):
            contexto['error'] = errors
    lista_comunidades = Comunidad.objects.all()
    lista_generos = Genero.objects.all()
    vista_tipo = request.GET.get('vista')
    if vista_tipo == 'siguiendo':
        publicaciones = Publicacion.objects.filter(usuario__in=usuario_sesion.follows.all()).order_by('-fecha')
    else:
        publicaciones = Publicacion.objects.order_by('-fecha').all()
    likes = Like.objects.filter(usuario=usuario_sesion).values_list('publicacion_id', flat=True)
    for publicacion in publicaciones:
        publicacion.ya_dio_like = publicacion.id in likes
    contexto = {
        'comunidades': lista_comunidades,
        'usuario_sesion': usuario_sesion,
        'generos': lista_generos,
        'publicaciones': publicaciones,
        'comunidades_recomendadas': comunidades_recomendadas,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        partial = request.GET.get('partial')
        if partial == 'comunidades_recomendadas':
            return render(request, 'partials/comunidades_recomendadas_list_partial.html', {'contexto': contexto})
    return render(request,'comunidades.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

def detalles_comunidad(request,id):
    usuario_sesion = Usuario.objects.get(id = request.session.get('user_id'))
    if request.method == "POST":
        formulario = request.POST
        errors = crear_comunidad(request,formulario)
        if(errors != []):
            contexto['error'] = errors
    comunidad = Comunidad.objects.get(id=id)
    lista_comunidades = Comunidad.objects.all()
    lista_generos = Genero.objects.all()
    generos_comunidad = comunidad.generos.all()
    followers = comunidad.followers.all()
    publicaciones = Publicacion.objects.filter(Q(usuario__in=followers) & Q(cancion__generos__in = generos_comunidad)).distinct().order_by('-fecha')
    likes = Like.objects.filter(usuario=usuario_sesion).values_list('publicacion_id', flat=True)
    for publicacion in publicaciones:
        publicacion.ya_dio_like = publicacion.id in likes
    contexto = {
        'comunidades': lista_comunidades,
        'usuario_sesion': usuario_sesion,
        'generos': lista_generos,
        'comunidad': comunidad,
        'generos_comunidad': generos_comunidad,
        'followers': followers,
        'ya_sigue': usuario_sesion in followers,
        'publicaciones': publicaciones,
    }
    return render(request,'detalles_comunidad.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

def crear_comunidad(request,formulario):
    error = []
    try:
        nombre = formulario.get('nombre')
    except Exception as e:
        error.append("Nombre :" + str(e))
    try:
        generos = formulario.getlist('generos')
    except Exception as e:
        error.append("Generos :" + str(e))
    try:
        foto_perfil = request.FILES.get('input_imagen')
        if foto_perfil:  # Verificar si se ha cargado una nueva imagen
            static_folder = os.path.join(settings.BASE_DIR, 'static')
            new_image_path = os.path.join(static_folder, 'comunidades', foto_perfil.name)
            with open(new_image_path, 'wb') as file:
                file.write(foto_perfil.read())
            foto_perfil = 'comunidades/' + foto_perfil.name
    except:
        error.append("No se ha seleccionado una imagen")
    admin = Usuario.objects.get(id=request.session.get('user_id'))
    generos_bd = [Genero.objects.get(nombre=genero) for genero in generos]
    comunidad = Comunidad.objects.create(nombre=nombre,foto=foto_perfil,admin = admin)
    comunidad.generos.set(generos_bd)
    comunidad.save()
    unirse_comunidad(request,comunidad.id)
    return error

def unirse_comunidad(request,id):
    usuario_sesion = Usuario.objects.get(id = request.session.get('user_id'))
    comunidad = Comunidad.objects.get(id=id)
    if usuario_sesion in comunidad.followers.all():
        comunidad.followers.remove(usuario_sesion)
        return HttpResponseRedirect(f'/comunidades/detalles/{id}')
    comunidad.followers.add(usuario_sesion)
    return HttpResponseRedirect(f'/comunidades/detalles/{id}')

def editar_comunidad(request,id):
    comunidad = Comunidad.objects.get(id=id)
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nuevo_nombre')  # Usar paréntesis en lugar de corchetes
            if nombre != comunidad.nombre:
                comunidad.nombre = nombre
            else:
                print("No se ha cambiado el nombre")
        except Exception as e:
            pass
        try:
            foto_perfil = request.FILES.get('input_imagen_comunidad')
            if foto_perfil:  # Verificar si se ha cargado una nueva imagen
                static_folder = os.path.join(settings.BASE_DIR, 'static')
                new_image_path = os.path.join(static_folder, 'comunidades', foto_perfil.name)
                with open(new_image_path, 'wb') as file:
                    file.write(foto_perfil.read())
                
                if comunidad.foto:  # Verificar si ya existe una imagen de perfil
                    actual_image_path = os.path.join(static_folder,comunidad.foto.name)
                    if os.path.exists(actual_image_path):
                        os.remove(actual_image_path)
                comunidad.foto = 'comunidades/' + foto_perfil.name
                print("Se ha cambiado la imagen")
            else:
                print("No se ha cargado una nueva imagen")
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")         
        comunidad.save()
    return HttpResponseRedirect(f'/comunidades/detalles/{id}')

def eliminar_comunidad(request,id):
    comunidad = Comunidad.objects.get(id=id)
    comunidad.delete()
    return HttpResponseRedirect('/comunidades')
###############################################################################################################################################
#                                                                                                                                             #
#                                       Funciones para la creación de post y manejo de estos                                                  #
###############################################################################################################################################
def buscar_canciones(request):
    if request.GET.get('id', ''):  # Verificar si se ha enviado un ID
        query = request.GET.get('id', '')
        cancion = Cancion.objects.get(id=query)
        cancion = model_to_dict(cancion)
        cancion['generos'] = [str(genero) for genero in cancion['generos']]  # Convertir cada objeto Genero a una cadena
        return JsonResponse({'cancion': cancion})
    elif request.GET.get('canciones', ''): # Verificar si se ha enviado un nombre
        print("Se ha enviado una cancion")
        query = request.GET.get('canciones', '')
        canciones_list = list(Cancion.objects.filter(Q(nombre__icontains=query) | Q(generos__nombre__icontains=query) |  Q(album__artista__nombre__icontains=query)  |Q(album__nombre__icontains=query)).distinct().values())
        for cancion in canciones_list:
            albums_asociados = Album.objects.filter(canciones__nombre=cancion['nombre'])
            if albums_asociados.exists():
                cancion['album'] = str(random.choice(albums_asociados).foto)
            else:
                cancion['album'] = None
        if(len(canciones_list) != 0):
            return JsonResponse({'canciones': canciones_list})
        else:
            return JsonResponse({'canciones': 'No se encontraron canciones'})
        

def guardar_cancion(request,id_lista,id_cancion):
    playlist = ListaReproduccion.objects.get(id=id_lista)
    cancion = Cancion.objects.get(id=id_cancion)
    playlist.canciones.add(cancion)
    return JsonResponse({'cancion': cancion.nombre})


def postear(request):
    comentario = request.POST.get('comentario')
    foto = request.POST.get('imagen_cancion')
    cancion_id = request.POST.get('id_cancion')
    usuario_id = request.session.get('user_id')
    comunidad_id = request.POST.get('id_comunidad')
    fecha = datetime.now()
    # Intenta obtener el usuario y la canción
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        cancion = Cancion.objects.get(id=cancion_id)
        if comunidad_id:
            comunidad = Comunidad.objects.get(id=comunidad_id)
    except Usuario.DoesNotExist:
        return HttpResponse("Error: No se encontró el usuario.", status=400)
    except Cancion.DoesNotExist:
        return HttpResponse("Error: No se encontró la canción.", status=400)
    except Comunidad.DoesNotExist:
        return HttpResponse("Error: No se encontró la comunidad.", status=400)

    # Crea la publicación
    try:
        if comunidad_id:
            publicacion = Publicacion.objects.create(
                fecha=fecha,
                texto=comentario,
                foto=foto,
                cancion=cancion,
                usuario=usuario,
                comunidad=comunidad
            )
        else:
            publicacion = Publicacion.objects.create(
                fecha=fecha,
                texto=comentario,
                foto=foto,
                cancion=cancion,
                usuario=usuario
            )
        ix = open_dir("publicaciones")
        writer = ix.writer()
        writer.add_document(id_publicacion = str(publicacion.id),texto = comentario)
        writer.commit()
        return HttpResponse("¡El posteo se ha completado correctamente!")
    except Exception as e:
        return HttpResponse(f"Error al completar el posteo: {str(e)}", status=500)
    
def like(request,publicacion_id):
    usuario = Usuario.objects.get(id=request.session.get('user_id'))
    publicacion = Publicacion.objects.get(id=publicacion_id)
    try:
        like = Like.objects.get(usuario=usuario,publicacion=publicacion)
        like.delete()
    except:
        Like.objects.create(usuario=usuario,publicacion=publicacion)
    return redirect(request.META.get('HTTP_REFERER', 'default_if_none'))

def crear_lista(request):
    usuario = Usuario.objects.get(id=request.session.get('user_id'))
    lista = ListaReproduccion.objects.create(usuario=usuario,nombre="Nueva lista")
    id = int(lista.id)
    return HttpResponseRedirect(f'/index_lista/{id}')

def detalles_lista(request,id):
    usuario = Usuario.objects.get(id=request.session.get('user_id'))
    lista = ListaReproduccion.objects.get(id=id)
    canciones = lista.canciones.all()
    duracionTotal = sum([cancion.duracion for cancion in canciones])
    duracionTotal = f"{duracionTotal // 3600} min {(duracionTotal % 3600) // 60} s"
    contexto = {
        'usuario_sesion': usuario,
        'lista': lista,
        'canciones': canciones,
        'duracionTotal': duracionTotal,
    }
    return render(request,'detalles_lista.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

def eliminar_cancion_playlist(request,id_lista,id_cancion):
    playlist = ListaReproduccion.objects.get(id=id_lista)
    cancion = Cancion.objects.get(id=id_cancion)
    playlist.canciones.remove(cancion)
    return HttpResponseRedirect(f'/index_lista/{id_lista}')


def index_lista(request,id_lista):
    usuario = Usuario.objects.get(id=request.session.get('user_id'))
    lista = ListaReproduccion.objects.get(id=id_lista)
    if request.method == 'POST':
        formulario = request.POST
        try:
            nombre = formulario.get('nombre')
            lista.nombre = nombre
        except Exception as e:
            print("Error al obtener el nombre de la lista: ", e)
        try:
            foto_perfil = request.FILES.get('input_imagen')
            if foto_perfil:  # Verificar si se ha cargado una nueva imagen
                static_folder = os.path.join(settings.BASE_DIR, 'static')
                new_image_path = os.path.join(static_folder, 'lista_reproducciones', foto_perfil.name)
                with open(new_image_path, 'wb') as file:
                    file.write(foto_perfil.read())
                if lista.foto:  # Verificar si ya existe una imagen de perfil
                    actual_image_path = os.path.join(static_folder,lista.foto.name)
                    if os.path.exists(actual_image_path):
                        os.remove(actual_image_path)
                
                lista.foto = 'lista_reproducciones/' + foto_perfil.name
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
        try:
            visibilidad = visibilidad = True if formulario.get('visibilidad') == 'on' else False
            lista.visibilidad = visibilidad

        except Exception as e:
            print("Error al obtener la visibilidad de la lista: ", e)
        lista.save()
        return redirect(request.META.get('HTTP_REFERER', 'default_if_none'))
    numero_listas = ListaReproduccion.objects.filter(usuario=usuario).count()
    contexto = {
        'usuario_sesion': usuario,
        'numero_listas': numero_listas,
        'lista': lista,
    }
    return render(request,'crear_lista.html',{'STATIC_URL':settings.STATIC_URL,'contexto':contexto})

def eliminar_lista(request,id):
    lista = ListaReproduccion.objects.get(id=id)
    lista.delete()
    return HttpResponseRedirect('/index')

def eliminar_publicacion(request,id):
    publicacion = Publicacion.objects.get(id=id)
    publicacion.delete()
    return HttpResponseRedirect('/index')

def eliminar_usuario(request,id):
    usuario = Usuario.objects.get(id=id)
    usuario.delete()
    return HttpResponseRedirect('/inicioSesion')