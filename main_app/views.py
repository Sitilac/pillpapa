from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from celery import Celery
from celery.schedules import crontab
import boto3
from .models import *
from .forms import *

S3_BASE_URL = 'https://s3.us-east-2.amazonaws.com/'
BUCKET = 'pillpapa'

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
  
def patient_detail(request): 
  patient = request.user.patient
  ICE = EmergencyContact.objects.get(patient_id=patient.id)
  return render(request, 'patients/detail.html',{
    'patient':patient, 
    'ICE':ICE,
  })

def add_dosing(request, pill_id):
  form = DosingForm(request.POST)
  if form.is_valid():
    new_dosing = form.save(commit=False)
    new_dosing.pill_id = pill_id
    new_dosing.save()
  return redirect('detail', pill_id=pill_id)

class PatientCreate(CreateView):
  model = Patient
  fields = ["first_name", "last_name", "email", 'dob', 'phone_num', 'room_number']
  
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user
    form.instance.patient = self.request.user.patient
    self.request.user.first_name = form.instance.user.first_name
    self.request.user.last_name = form.instance.user.last_name
    self.request.user.email = form.instance.user.email
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class ICECreate(CreateView):
  model = EmergencyContact
  fields = ['first_name', 'last_name','email', 'phone']
  
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user
    form.instance.patient = self.request.user.patient
    # Let the CreateView do its job as usual
    return super().form_valid(form)
  

class PillCreate(CreateView):
  model = Pill
  fields = ['name','dosage','directions', 'prescribing_doctor','qty','refills', 'date_prescribed']

  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user
    form.instance.patient = self.request.user.patient
    # Let the CreateView do its job as usual
    return super().form_valid(form)
  

class PillUpdate(UpdateView):
  model = Pill
  fields = ['name', 'dosage', 'directions', 'prescribing_doctor', 'qty', 'refills', 'date_prescribed']

class PillDelete(DeleteView):
  model = Pill
  success_url = '/pills/'
  
def signup(request):
  error_message = ''
  flag = 0
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid(): 
      user = form.save()
      # This will add the user to the database
      # This is how we log a user in via code
      login(request, user)
      return redirect('patient_create')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  patient = PatientForm()
  #emergency_contact = ICEForm()
  context = {
    'form': form, 
    'error_message': error_message,
  }
  return render(request, 'registration/signup.html', context)

def add_photo(request):
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      Photo.objects.create(url=url, patient_id=request.user.patient.id)
    except:
      print('An error occurred uploading file to S3')
  return redirect('patient_detail')