from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
  return HttpResponse('<h1>Hello, welcome to Pill Papa, the Papa who reminds you to Pop your Pills!</h1>')

def about(request):
  return render(request, 'about.html')