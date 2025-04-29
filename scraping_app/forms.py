# scraping_app/forms.py
from django import forms

class UrlForm(forms.Form):
    url = forms.URLField(label='URL de la publicación de Facebook', max_length=500)
