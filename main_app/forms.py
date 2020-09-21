from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Dosing, Patient, EmergencyContact

# class UserForm(UserCreationForm):
#   first_name = forms.CharField(max_length=50, required=True)
#   last_name = forms.CharField(max_length=50, required=True)
#   email = forms.CharField(max_length=50, required=True)
#   class Meta:
#     model = User
#     fields = ["username", "password1", "password2"]

class DosingForm(ModelForm):
  class Meta:
    model = Dosing
    fields = ['date', 'dose']
  
class PatientForm(ModelForm):
  class Meta:
    model = Patient
    fields = ["first_name", "last_name", "email",'dob', 'phone_num','room_number']
    
class ICEForm(ModelForm):
  class Meta:
    model = EmergencyContact
    fields = ['first_name', 'last_name','email', 'phone']
    #fields = '__all__'