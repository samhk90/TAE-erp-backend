from django.shortcuts import render

def admindashboard(request):
    return render(request,'admin.html')