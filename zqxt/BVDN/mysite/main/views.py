from django.shortcuts import render
import json
# Create your views here.

def index(request):
    return render(request, 'basemain.html')

def accounts_profile(request):
    if request.method == 'POST':
        a = json.loads(request.body.decode('utf-8'))
        print(a)
    return render(request, 'accounts_profile.html')