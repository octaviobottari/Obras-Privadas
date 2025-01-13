# main/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def register_ciudadano(request):
    return render(request, 'register_ciudadano.html')
