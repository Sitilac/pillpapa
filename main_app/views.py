from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import *

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
  fields = ['name','dosage','directions', 'prescribing_doctor','qty','refills', 'date_prescribed']

  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user 
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class PillUpdate(UpdateView):
  model = Pill
  fields = '__all__'

class PillDelete(DeleteView):
  model = Pill
  success_url = '/pills/'
  
def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserForm(request.POST,)
    patient = PatientForm(request.POST)
    #emergency_contact = ICEForm(request.POST)
    print(f'form:{form.is_valid()} patient: {patient.is_valid()} ')
    print(f'form:{form} patient: {patient} ')
    if form.is_valid(): #and patient.is_valid()
      # This will add the user to the database
      patient.save()
      #emergency_contact.save()
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserForm()
  patient = PatientForm()
  #emergency_contact = ICEForm()
  context = {
    'form': form, 
    'error_message': error_message,
    'patient':patient,
  }
  return render(request, 'registration/signup.html', context)

