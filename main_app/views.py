from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory
from django.db import transaction
from datetime import date, datetime
from tzlocal import get_localzone
from dateutil import *
from django.utils import timezone
import pytz
import uuid
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
  time = datetime.now()
  d = Dosing.objects.filter(pill_id=pill_id)
  dosing_count = d.count()
  pill.dosing_total = dosing_count
  pill.save(update_fields=['dosing_total'])
  if(pill.dose_date != date.today()):
    pill.dose_date = date.today()
    pill.doses_taken = 1
    pill.save(update_fields=['doses_taken', 'dose_date'])
  dosing_form = DosingForm()
  return render(request, 'pills/detail.html', {
     'pill': pill, 'dosing_form': dosing_form, 'dosing': d, 'time': time
  })

def dose_taken(request, pill_id):
  pill = Pill.objects.get(id=pill_id)
  dosing = Dosing.objects.filter(pill_id=pill_id)
  time = datetime.now()
  time = time.time()
  time = int(time.strftime('%H'))
  if(pill.qty != pill.qty_remaining and pill.qty_remaining > pill.qty ):
    pill.qty_remaining = pill.qty
    pill.save(update_fields=['qty_remaining'])
  idx = pill.dosing_total - pill.doses_taken
  time2 = dosing[idx].time
  time2 = int(time2.strftime('%H'))
  compare_time = time - time2
  if compare_time < 0:
    compare_time = compare_time * (-1)
  if compare_time <= 1:
    request.user.patient_profile.points += 100
  elif compare_time > 1 and compare_time < 2:
    request.user.patient_profile.points += 50
  else:
    pass
  pill.doses_taken = pill.doses_taken + 1
  pill.qty_remaining = pill.qty_remaining - dosing[idx].dose
  pill.save(update_fields=['doses_taken','qty_remaining'])
  request.user.patient_profile.save(update_fields=['points'])
  return redirect('detail', pill_id=pill_id)

def add_dosing(request, pill_id):
  DoseFormSet = formset_factory(DosingForm) 
  formset = DoseFormSet() 
  if request.method == 'GET':
    formset = DoseFormSet(request.GET or None)
  elif request.method == 'POST':
    formset = DoseFormSet(request.POST) 
    if formset.is_valid():
      for form in formset:
        if form.cleaned_data.get('time'):
          new_dosing = form.save(commit=False)
          new_dosing.pill_id = pill_id
          new_dosing.save()
      return redirect('detail', pill_id=pill_id)
  context = {
    'formset': formset,
  }
  return render(request, 'dosing/dosing.html', context)

def patients_index(request):
  patients = PatientProfile.objects.all
  admins_patients = request.user.admin_profile.patients_list.all()
  return render(request, 'patients/index.html', {
     'patients': patients,
     'admins_patients': admins_patients,
      })

def patients_admins_index(request):
  patients = request.user.admin_profile.patients_list.all()
  return render(request, 'patients/admins_index.html', { 'patients': patients })

def add_patient(request, patient_id):
  patient = PatientProfile.objects.get(id=patient_id)
  admin = request.user.admin_profile
  admin.patients_list.add(patient)
  admin.save()
  return redirect('patients_detail', patient_id=patient_id)

def patients_detail(request, patient_id): 
  patient = PatientProfile.objects.get(id=patient_id)
  ICE = EmergencyContact.objects.get(patient_id=patient.id)
  pills = Pill.objects.get(patient_id=patient.id)
  return render(request, 'patients/detail.html',{
    'patient':patient, 
    'ICE':ICE,
    'pills':pills,
  })

def patients_profile(request): 
  patient = request.user.patient_profile
  ICE = EmergencyContact.objects.get(patient_id=patient.id)
  return render(request, 'profiles/patient.html',{
    'patient':patient, 
    'ICE':ICE,
  })

def admins_profile(request): 
  admin = request.user.admin_profile
  return render(request, 'profiles/admin.html',{
    'admin':admin, 
  })

class PatientCreate(CreateView):
  model = PatientProfile
  fields = ['first_name', 'last_name', 'email', 'dob', 'phone', 'room_number']

  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.patient_profile = self.request.user.patient_profile
    self.request.user.first_name = form.instance.user.first_name
    self.request.user.last_name = form.instance.user.last_name
    self.request.user.email = form.instance.user.email
    return super().form_valid(form)

class ICECreate(CreateView):
  model = EmergencyContact
  fields = ['first_name', 'last_name', 'email', 'phone']

  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.patient = self.request.user.patient_profile
    return super().form_valid(form)

class PillCreate(CreateView):
  model = Pill
  fields = ['name', 'dosage', 'directions', 'prescribing_doctor', 'qty', 'refills', 'date_prescribed']

  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.patient = self.request.user.patient_profile
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
    form = UserCreationForm(request.POST)
    if form.is_valid(): 
      user = form.save()
      login(request, user)
      return redirect('patient_create')
    else:
      error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  patient = PatientProfileForm()
  context = {
    'form': form, 
    'error_message': error_message,
  }
  return render(request, 'registration/signup.html', context)

def add_patient_photo(request):
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      PatientPhoto.objects.create(url=url)
    except:
      print('An error occurred uploading file to S3')
  return redirect('patients_profile', kwargs={'patient_id': request.user.patient_profile.id})

def add_admin_photo(request):
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      AdminPhoto.objects.create(url=url)
    except:
      print('An error occurred uploading file to S3')
  return redirect('admins_profile', kwargs={'admin_id': request.user.admin_profile.id})

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