from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Pill)
admin.site.register(Dosing)
admin.site.register(EmergencyContact)
admin.site.register(Patient)
admin.site.register(Photo)