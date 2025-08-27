from django.shortcuts import render

# Create your views here.

def home(request):
    """Landing page for Zach Churchill's vibe coding projects"""
    return render(request, 'home/home.html')
