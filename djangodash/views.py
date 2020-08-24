from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user
from .forms import CreateUserForm

@unauthenticated_user
def registerpage(request):
	form = CreateUserForm()
	context = {'form':form}

	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')

			group = Group.objects.get(name = 'User')
			user.groups.add(group)
			messages.success(request,'%s user Created.'%username)

			return redirect('login')

	return render(request, 'djangodash/register.html',context)

@unauthenticated_user
def loginpage(request):	
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request,username=username,password=password)

		if user is not None:
			login(request,user)
			return redirect('home')
		else:
			messages.info(request,'Username OR Password is incorrect')

	context = {}
	return render(request,'djangodash/login.html',context)

def logoutuser(request):
	logout(request)
	return redirect('login')
