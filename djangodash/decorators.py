from django.http import HttpResponse
from django.shortcuts import redirect

from process.load_frames import getSummary
from plots.dash_apps.finished_apps.board import Summaryboard,Unitsboard
from plots.dash_apps.finished_apps.returns import Summaryreturns,Unitsreturns


def unauthenticated_user(view_func):
	def wrapper_func(request,*args,**kwargs):
		if request.user.is_authenticated:
			return redirect('home')
		else:
			return view_func(request,*args,**kwargs)

	return wrapper_func

def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		def wrapper_func(request,*args,**kwargs):
			group = None
			if request.user.groups.exists():
				group = request.user.groups.all()[0].name
				print('Inside decorator: ',request.user.groups.all())
			if group in allowed_roles:
				summary_df,value_dictionary = getSummary()
				Summaryboard(summary_df)
				Unitsboard(value_dictionary)
				return view_func(request,*args,**kwargs)
			else:
				return HttpResponse('You are not authenticated to view this page')
			return view_func(request,*args,**kwargs)
		return wrapper_func
	return decorator
