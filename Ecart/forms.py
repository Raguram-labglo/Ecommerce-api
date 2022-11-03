from email.policy import default
from unittest.util import _MAX_LENGTH
from attr import field
from django import forms
from Ecart.models import *

class Prodect_form(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'





