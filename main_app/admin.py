from django.contrib import admin
from .models import *

admin.site.register(Pill)
admin.site.register(Dosing)
admin.site.register(EmergencyContact)
admin.site.register(PatientProfile)
admin.site.register(AdminProfile)
admin.site.register(User)
admin.site.register(PatientPhoto)
admin.site.register(AdminPhoto)