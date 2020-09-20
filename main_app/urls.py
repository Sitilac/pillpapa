from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('pills/', views.pills_index, name='index'),
  path('pills/<int:pill_id>/', views.pill_detail, name='detail'),
  path('pills/create/', views.PillCreate.as_view(), name='pills_create'),
  path('pills/<int:pk>/update/', views.PillUpdate.as_view(), name='pills_update'),
  path('pills/<int:pk>/delete/', views.PillDelete.as_view(), name='pills_delete'),
  path('pills/<int:pill_id>/add_dosing/', views.add_dosing, name='add_dosing'),
  path('accounts/signup/', views.signup, name='signup'),
]