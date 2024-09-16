from django.shortcuts import render

def dashboard(request):
    return render(request, 'coal/dashboard.html', 
    {'title':'Dashboard'})