from django.db import models
from django.urls import reverse
from datetime import date
from dateutil.relativedelta import relativedelta, MO
from sortedm2m.fields import SortedManyToManyField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Create your models here.

DOSE = (
  ('M', 'Morning'),
  ('A', 'Afternoon'),
  ('N', 'Night')
)
class Patient(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  phone_num= models.CharField(max_length=25)
  room_number = models.CharField(max_length=5, blank=True)
  points = models.IntegerField(default=0)

# def create_user_profile(sender, instance, created, **kwargs):
#   if created:
#     Patient.objects.create(userName=instance)

# post_save.connect(create_user_profile, sender=User)
  
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Patient.objects.create(user=instance)


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
  patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('detail', kwargs={'pill_id': self.id})


  
class EmergencyContact(models.Model):
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  phone = models.CharField(max_length=25)
  email = models.CharField(max_length=50)
  # patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
  
  @property
  def name(self):
    return "%s %s" % ( self.first_name, self.last_name )
  
  def __str__(self):
    return self.name
  

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
  