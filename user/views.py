from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import check_password
from .models import *
from django.contrib import messages

def login_(request):
    if request.method == 'POST':
        if UserInfo.objects.filter(phone=request.POST.get('username')).exists():
            user = UserInfo.objects.get(phone=request.POST.get('username'))
            if check_password(request.POST.get('password'), user.password):
                if user.type == "superadmin" or user.type == "admin" or user.type == "employee":
                    if user.block:
                        messages.error(request,"User blocked")  
                        return redirect('login')
                    login(request,user)
                    return redirect('super_dash') if user.type == "superadmin" else redirect('dash') if user.type == "admin" else redirect('home')
        messages.error(request,"Invalid credentials")  
        return redirect('login')
    return render(request,'login.html')

def logout_(request):
    logout(request)
    return redirect('login')

def block(request,id):
    user = UserInfo.objects.get(id = id)
    user.block = False if user.block else True
    user.save()
    return redirect('super_dash') if request.user.type == "superadmin" else redirect('dash') if request.user.type == "admin" else redirect('login')