from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import *
from .forms import DosingForm
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
  dosing_form = DosingForm()
  return render(request, 'pills/detail.html', {
     'pill': pill, 'dosing_form':dosing_form
  })

def add_dosing(request, pill_id):
  form = DosingForm(request.POST)
  if form.is_valid():
    new_dosing = form.save(commit=False)
    new_dosing.pill_id = pill_id
    new_dosing.save()
  return redirect('detail', pill_id=pill_id)

class PillCreate(CreateView):
  model = Pill
  fields = '__all__'

class PillUpdate(UpdateView):
  model = Pill
  fields = '__all__'

class PillDelete(DeleteView):
  model = Pill
  success_url = '/pills/'

