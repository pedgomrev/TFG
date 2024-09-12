from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from main.views  import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('populateDB/', populateDB, name='populateDB'),
    path('inicioSesion', inicioSesion, name='inicioSesion'),
    path('cambioContraseña', cambioContraseña, name='cambioContraseña'),
    path('buscarCancion/', buscar_canciones, name='buscar_cancion'),
    path('postear/', postear, name='postear'),
    path('registro', registro),
    path('perfil/<int:id>', perfil, name='perfil'),
    path('perfil_artista/<int:id>', perfil_artista, name='perfil_artista'),
    path('seguir/<int:id>', seguir, name='seguir'),
    path('seguir_artista/<int:id>', seguir_artista, name='seguir_artista'),
    path('index/', index, name='index'),
    path('index/explora/', explora, name='explora'),
    path('index/explora/ver_mas/<str:tipo>/', ver_mas, name='ver_mas'),
    path('index/buscar/', buscar, name='buscar'),
    path('comunidades/', comunidades, name='comunidades'),
    path('comunidades/detalles/<int:id>/', detalles_comunidad, name='detalles_comunidad'),
    path('comunidades/unirse/<int:id>/', unirse_comunidad, name='unirse_comunidad'),
    path('comunidades/editar/<int:id>/', editar_comunidad, name='editar_comunidad'),
    path('comunidades/eliminar/<int:id>/', eliminar_comunidad, name='eliminar_comunidad'),
    path('detalles/<str:tipo>/<int:id>/', detalles, name='detalles'),
    path('like/<int:publicacion_id>', like, name='like'),
    path('crear_lista/', crear_lista, name='crear_lista'),
    path('detalles_lista/<int:id>/', detalles_lista, name='detalles_lista'),
    path('index_lista/<int:id_lista>', index_lista, name='index_lista'),
    path('guardar_cancion/<int:id_lista>/<int:id_cancion>', guardar_cancion, name='agregar_cancion'),
    path('eliminar_cancion/<int:id_lista>/<int:id_cancion>', eliminar_cancion_playlist, name='eliminar_cancion'),
    path('eliminar_lista/<int:id>', eliminar_lista, name='eliminar_lista'),
    path('eliminar_usuario/<int:id>', eliminar_usuario, name='eliminar_usuario'),
    path('eliminar_publicacion/<int:id>', eliminar_publicacion, name='eliminar_publicacion'),
    path('logout', auth_views.LogoutView.as_view(next_page='inicioSesion'), name='logout'),
    path('', inicioSesion),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)