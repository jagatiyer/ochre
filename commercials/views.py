from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def commercials_index(request):
    return render(request, "commercials/index.html")
