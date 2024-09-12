from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class Genero(models.Model):
    nombre = models.CharField(unique=True,max_length = 100)
    color = models.CharField(max_length = 7,null=True)
    def __str__(self):
        return self.nombre


class Cancion(models.Model):
    nombre = models.TextField(unique=True,verbose_name="Nombre")
    generos = models.ManyToManyField(Genero)
    duracion = models.IntegerField()
    oyentes = models.IntegerField(default = 0)
    link_youtube = models.URLField()
    link_spotify = models.URLField()
    def __str__(self):
        return self.nombre
    
class Album(models.Model):
    nombre = models.TextField()
    canciones = models.ManyToManyField(Cancion)
    generos = models.ManyToManyField(Genero)
    duracionTotal = models.IntegerField()
    foto = models.ImageField(verbose_name="Foto",upload_to='albums')
    def __str__(self):
        return self.nombre
    
class Artista(models.Model):
    nombre = models.TextField(verbose_name="Nombre",unique=True)
    oyentes_mensuales = models.IntegerField()
    años_activo = models.TextField()
    albums = models.ManyToManyField(Album)
    generos = models.ManyToManyField(Genero)
    def __str__(self):
        return self.nombre
    
class Usuario(models.Model):
    nombre = models.CharField(verbose_name="Nombre",max_length = 100)
    apellidos = models.CharField(verbose_name="Apellidos",max_length = 100)
    email = models.EmailField(verbose_name="Email",unique=True)
    apodo = models.TextField(verbose_name="Nombre usuario",unique=True)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    foto_perfil = models.ImageField(verbose_name="Foto de Perfil",blank=True,null=True)
    contraseña = models.CharField(max_length=255,verbose_name="Contraseña")
    followers = models.ManyToManyField('self', symmetrical=False, related_name='follower',blank=True)
    follows = models.ManyToManyField('self', symmetrical=False, related_name='follow',blank=True)
    artistas_seguidos =models.ManyToManyField(Artista,related_name='seguidores',blank=True)
    admin = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        try:
            user = Usuario.objects.get(id=self.id)
            if user.contraseña != self.contraseña:
                self.contraseña = make_password(self.contraseña)
        except Usuario.DoesNotExist:
            self.contraseña = make_password(self.contraseña)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.apodo

    
class ListaReproduccion(models.Model):
    nombre = models.TextField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='listas_reproduccion')
    canciones = models.ManyToManyField('Cancion', verbose_name="Canciones", blank=True)
    foto = models.ImageField(blank=True,null=True,upload_to='lista_reproducciones')
    visibilidad = models.BooleanField(default=True)
    def __str__(self):
        return f'Lista de reproducción {self.nombre} de {self.usuario.apodo}'
    
class Comunidad(models.Model):
    nombre = models.TextField()
    admin = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comunidades',null = True)
    generos = models.ManyToManyField(Genero)
    followers = models.ManyToManyField(Usuario)
    foto = models.ImageField(blank=True,null=True)
    def __str__(self):
        return self.nombre

class Publicacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='usuario')
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(blank=True,null=True)
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE, related_name='cancion',null=True)
    def __str__(self):
        return f'Publicación de {self.usuario.apodo} en {self.cancion.nombre} el dia {self.fecha}'

class Like(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='likes')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='likes')
    def __str__(self):
        return f'Like de {self.usuario.apodo} en {self.publicacion.cancion.nombre}'