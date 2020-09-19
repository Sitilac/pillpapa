from django.db import models
from django.urls import reverse
from datetime import date
from dateutil.relativedelta import relativedelta, MO
from sortedm2m.fields import SortedManyToManyField
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Pill(models.Model):
  name = models.CharField(max_length=75)
  dosage = models.CharField(max_length=50)
  directions = models.TextField(max_length=250)
  prescribing_doctor = models.CharField(max_length=50)
  qty = models.IntegerField()  
  refills = models.IntegerField()  
  date_prescribed = models.DateField()
  # qty_remaining = qty

  def __str__(self):
    return self.name
  
class EmergencyContact(models.Model):
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  phone = models.CharField(max_length=25)
  email = models.CharField(max_length=50)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  
  @property
  def name(self):
    return "%s %s" % ( self.first_name, self.last_name )
  
  def __str__(self):
    return self.name
  
# class Admin(models.Model):
#   admin_user = models.ForeignKey(settings.AUTH_USER_MODEL)
#   users_list = models.ManyToManyField(User)
  