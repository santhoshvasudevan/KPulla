from django.shortcuts import render,get_object_or_404
from .models import Funds_DB,Transactions,debts
from django.contrib.auth.decorators import login_required
from djangodash.decorators import unauthenticated_user,allowed_users
from process.load_frames import debtsvalue,getSummary
from plots.dash_apps.finished_apps.board import Summaryboard,Unitsboard
from plots.dash_apps.finished_apps.returns import Summaryreturns,Unitsreturns

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def home(request):
	'''
	Make Shortnames 
	'''

	summary_df,value_dictionary = getSummary()
	shortnames = ['board_'+value_dictionary[k][1] for k in value_dictionary]
	context = {'shortnames': shortnames}
	return render(request,'plots/welcome2.html',context)

def validquery(query):
	return query != '' and query != None

def filterfunds(fund_name_query,codequery):
	qs = None
	if validquery(fund_name_query):
		qs = Funds_DB.objects.filter(FundName__startswith = fund_name_query)

	if validquery(codequery):
		qs = Funds_DB.objects.get(SchemeCode = scheme_code_query)

	return qs

@login_required(login_url='login')
def transequity(request):
	if request.method == 'POST':
		fund_name = get_object_or_404(Funds_DB, pk=request.POST.get('selected_fund'))
		#fund_name = request.POST.get('selected_fund')
		Amount= request.POST.get('amount_invested')
		date = request.POST.get('date')
		Category = request.POST.get('Category')
		#qs = filterfunds(fund_name_query,scheme_code_query)
		Identified = get_object_or_404(Funds_DB, FundName = fund_name)
		#print(Category)
		#print(Identified)
		Trans_instance = Transactions.objects.create(AMFICode = Identified,
														Date = date,
														Amount_Invested = Amount,
														category=Category)

	context = {
				'datalist': Funds_DB.objects.all(), 
				'trans': list(Transactions.objects.all().order_by('-Date'))[:5]
				}

	return render(request,'plots/transequity.html',context)


@login_required(login_url='login')
def transdebt(request):
	if request.method == 'POST':
		depositamount = request.POST.get('debt_amount')
		start_date = request.POST.get('date')
		rateofinterest = request.POST.get('rate_of_interest')
		depositduration = request.POST.get('duration')
		depositdurationtime = request.POST.get('termduration')
		compounding = request.POST.get('Compounding')
		commentname = request.POST.get('Comments')
		#print(depositamount,start_date,rateofinterest,depositduration,depositdurationtime,compounding)

	# Deposit_Amount = models.DecimalField(max_digits=15,decimal_places=2,null=False)
	# start_date = models.DateField(blank=False,null=False)
	# interest_rate = models.DecimalField(max_digits=5,decimal_places=2,null=False)
	# deposit_duration = models.IntegerField(null=False)
	# deposit_term = models.SmallIntegerField(choices = dep_terms)
	# compounding_term = models.SmallIntegerField(choices=comp_terms)
		debts.objects.create(Deposit_Amount = depositamount,
			Deposit_value = depositamount,
			start_date = start_date,
			interest_rate = rateofinterest,
			deposit_duration = depositduration,
			deposit_term = depositdurationtime,
			compounding_term=compounding,
			comments= commentname)
	else:
		debtsvalue()

	context = {
			'trans': list(debts.objects.all().order_by('-start_date'))[:5]
	}
	return render(request,'plots/transdebt.html',context)


@login_required(login_url='login')
def returns(request):
	summary_df,value_dictionary = getSummary()
	shortnames = ['returns_'+value_dictionary[k][1] for k in value_dictionary]
	#Summaryreturns()
	#Unitsreturns()
	context = {'shortnames': shortnames}
	return render(request,'plots/returns.html',context)
	

@login_required(login_url='login')
def risks(request):
	return render(request,'plots/risks.html')


@login_required(login_url='login')
def ratios(request):
	return render(request,'plots/ratios.html')


@login_required(login_url='login')
def rebalance(request):
	return render(request,'plots/rebalance.html')


def Filterview(request):
	fund_name = request.GET.get('fund_name')
	print(fund_name)
	return render(request,'plots/transequity.html',{})
