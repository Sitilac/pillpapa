from django.db import models
from django.urls import reverse
from datetime import date
from dateutil.relativedelta import relativedelta, MO
from sortedm2m.fields import SortedManyToManyField
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Create your models here.

DOSE = (
  ('M', 'Morning'),
  ('A', 'Afternoon'),
  ('N', 'Night')
)

class User(AbstractUser):
  first_name = models.CharField(max_length=25)
  last_name = models.CharField(max_length=25)
  email = models.CharField(max_length=25)
  phone = models.CharField(max_length=25)
  is_patient = models.BooleanField(default=False)
  is_admin = models.BooleanField(default=False)

  @property
  def name(self):
    return "%s %s" % ( self.first_name, self.last_name )
  
  def __str__(self):
    return self.name  


class PatientProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='patient_profile')
  room_number = models.CharField(max_length=5, blank=True)
  dob = models.DateField(null=True)
  points = models.IntegerField(default=0)
  
  @property
  def name(self):
    return "%s %s" % ( self.user.first_name, self.user.last_name )
  
  def __str__(self):
    return self.name
  
  # def get_absolute_url(self):
  #   return reverse('ICE_create')
  
class AdminProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='admin_profile')
  job_title = models.CharField(max_length=50)
  patients_list = models.ManyToManyField(PatientProfile, blank=True)
  
  @property
  def name(self):
    return "%s %s" % ( self.user.first_name, self.user.last_name )
  
  def __str__(self):
    return self.name
  
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if instance.is_patient:
    PatientProfile.objects.get_or_create(user=instance)
  else:
    AdminProfile.objects.get_or_create(user=instance)
    
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  if instance.is_patient:
    instance.patient_profile.save()
  else:
    AdminProfile.objects.get_or_create(user=instance)
    
    


class Pill(models.Model):
  name = models.CharField(max_length=75)
  dosage = models.CharField(max_length=50)
  directions = models.TextField(max_length=250)
  prescribing_doctor = models.CharField(max_length=50)
  qty = models.IntegerField()  
  refills = models.IntegerField()  
  date_prescribed = models.DateField()
  # qty_remaining = qty
  
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('detail', kwargs={'pill_id': self.id})


  
class EmergencyContact(models.Model):
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  phone = models.CharField(max_length=25)
  email = models.CharField(max_length=50)
  patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True)
  
  @property
  def name(self):
    return "%s %s" % ( self.first_name, self.last_name )
  
  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('patient_detail', kwargs={'patient_id': self.user.patient_profile.id})
  

class Dosing(models.Model):
  date = models.DateField()
  dose = models.CharField(
    max_length=1,
    choices= DOSE,
    default=DOSE[0][0]
  )
  pill = models.ForeignKey(Pill, on_delete=models.CASCADE)
  def __str__(self):
    return f"{self.get_dose_display()} on {self.date}"
  class Meta:
    ordering = ['-date']

# class Admin(models.Model):
#   admin_user = models.ForeignKey(settings.AUTH_USER_MODEL)
#   users_list = models.ManyToManyField(User)
  
class Photo(models.Model):
  url = models.CharField(max_length=200)
  patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
  
  def __str__(self):
    return f"Photo for patient: @{self.url}"