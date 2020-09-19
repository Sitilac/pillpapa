from django.shortcuts import render
from django.http import HttpResponse
from .models import *

# Create your views here.

def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

def pills_index(request):
  pills = Pill.objects.all()
  return render(request, 'pills/index.html', { 'pills': pills })

def pill_detail(request, pill_id):
  pill = Pill.objects.get(id=pill_id)
  return render(request, 'pills/detail.html', { 'pill': pill })