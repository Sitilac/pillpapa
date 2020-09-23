from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
import uuid
import boto3
from .models import *
from .forms import *

S3_BASE_URL = 'https://s3.us-east-2.amazonaws.com/'
BUCKET = 'pillpapa'

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
  
def patients_index(request):
  patients = request.user.admin_profile.patients_list.all()
  return render(request, 'patients/index.html', { 'patients': patients })
  
def patient_detail(request): 
  patient = request.user.patient_profile
  ICE = EmergencyContact.objects.get(patient_id=patient.id)
  return render(request, 'patients/detail.html',{
    'patient':patient, 
    'ICE':ICE,
  })

def patients_detail(request, patient_id): 
  patient = PatientProfile.objects.get(id=patient_id)
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
  model = PatientProfile
  fields = ["first_name", "last_name", "email", 'dob', 'phone', 'room_number']
  
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user
    form.instance.patient_profile = self.request.user.patient_profile
    self.request.user.first_name = form.instance.user.first_name
    self.request.user.last_name = form.instance.user.last_name
    self.request.user.email = form.instance.user.email
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class ICECreate(CreateView):
  model = EmergencyContact
  fields = ['first_name', 'last_name', 'email', 'phone']
  
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user
    form.instance.patient = self.request.user.patient_profile
    # Let the CreateView do its job as usual
    return super().form_valid(form)
  

class PillCreate(CreateView):
  model = Pill
  fields = ['name','dosage','directions', 'prescribing_doctor','qty','refills', 'date_prescribed']

  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user
    form.instance.patient_profile = self.request.user.patient_profile
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
  patient = PatientProfileForm()
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
      Photo.objects.create(url=url, patient_id=request.user.patient_profile.id)
    except:
      print('An error occurred uploading file to S3')
  return redirect('patient_detail', kwargs={'patient_id': request.user.patient_profile.id})

@transaction.atomic
def patient_profile_view(request):
  if request.method == 'POST':
    user_form = UserForm(request.POST)
    profile_form = PatientProfileForm(request.POST)
    if user_form.is_valid() and profile_form.is_valid():
      user = user_form.save(commit=False)
      user.is_patient = True
      user.save()
      user.patient_profile.dob = profile_form.cleaned_data.get('dob')
      user.patient_profile.room_number = profile_form.cleaned_data.get('room_number')
      user.patient_profile.save()
      login(request, user)
      return redirect('ICE_create')
  else:
    user_form = UserForm()
    profile_form = PatientProfileForm()
  return render(request, 'registration/patient_profile.html', {
    'user_form': user_form,
    'profile_form': profile_form,
  })

@transaction.atomic
def admin_profile_view(request):
  if request.method == 'POST':
    user_form = UserForm(request.POST)
    profile_form = AdminProfileForm(request.POST)
    if user_form.is_valid() and profile_form.is_valid(): 
      user = user_form.save(commit=False)
      user.is_admin = True
      user.is_staff = True
      user.is_superuser = True
      user.save()
      user.admin_profile.job_title = profile_form.cleaned_data.get('job_title')
      user.admin_profile.save()
      login(request, user)
      return redirect('patients_index')
  else:
    user_form = UserForm()
    profile_form = AdminProfileForm()
  return render(request, 'registration/admin_profile.html', {
    'user_form': user_form,
    'profile_form': profile_form,
  })