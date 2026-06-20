

from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from .detection import detect_profile

def home(request):
    return render(request, "home.html")

# Just a wrapper for clarity and to match your URL route
def detect_instagram_profile(request):
    return detect_profile(request)


