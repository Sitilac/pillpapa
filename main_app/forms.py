from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import formset_factory
from datetime import datetime, time
from .models import *


class DosingForm(ModelForm):
  class Meta:
    model = Dosing
    fields = ['time', 'dose']

DoseFormSet = formset_factory(DosingForm)
    
class UserForm(forms.ModelForm):
  password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
  password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
  class Meta:
    model = User
    fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone']
    
  def clean_password2(self):
    password1 = self.cleaned_data.get("password1")
    password2 = self.cleaned_data.get("password2")
    if password1 and password2 and password1 != password2:
      raise forms.ValidationError("Passwords don't match")
    return password2

  def save(self, commit=True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data["password1"])
    if commit:
        user.save()
    return user
    
class PatientProfileForm(forms.ModelForm):
  class Meta:
    model = PatientProfile
    fields = ['dob', 'room_number']

class AdminProfileForm(forms.ModelForm):
  class Meta:
    model = AdminProfile
    fields = ['job_title']
    
class ICEForm(ModelForm):
  class Meta:
    model = EmergencyContact
    fields = ['first_name', 'last_name','email', 'phone']
    #fields = '__all__'