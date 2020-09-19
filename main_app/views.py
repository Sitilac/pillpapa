from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
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

class PillCreate(CreateView):
  model = Pill
  fields = '__all__'

class PillUpdate(UpdateView):
  model = Pill
  fields = '__all__'

class PillDelete(DeleteView):
  model = Pill
  success_url = '/pills/'

