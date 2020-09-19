from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('pills/', views.pills_index, name='index'),
  path('pills/<int:pill_id>/', views.pill_detail, name='detail'),
]