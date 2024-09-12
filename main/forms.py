from django import forms
import re
from main.models import *

class EditarPerfilForm(forms.Form):
    apodo = forms.CharField(required=False)
    foto_perfil = forms.ImageField(required=False)