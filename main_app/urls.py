from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('pills/', views.pills_index, name='index'),
  path('pills/<int:pill_id>/', views.pill_detail, name='detail'),
  path('patients/index', views.patients_index, name='patients_index'),
  path('patients/create/', views.PatientCreate.as_view(), name='patient_create'),
  path('patients/add_photo/', views.add_photo, name='add_photo'),
  path('patients/', views.patient_detail, name='patient_detail'),
  path('patients/<int:patient_id>', views.patients_detail, name='patients_detail'),
  path('emergency_contact/', views.ICECreate.as_view(), name = 'ICE_create'),
  path('pills/create/', views.PillCreate.as_view(), name='pills_create'),
  path('pills/<int:pk>/update/', views.PillUpdate.as_view(), name='pills_update'),
  path('pills/<int:pk>/delete/', views.PillDelete.as_view(), name='pills_delete'),
  path('pills/<int:pill_id>/add_dosing/', views.add_dosing, name='add_dosing'),
  path('accounts/signup/', views.signup, name='signup'),
  path('accounts/signup/patient/', views.patient_profile_view, name='patient_profile'),
  path('accounts/signup/admin/', views.admin_profile_view, name='admin_profile'),
]