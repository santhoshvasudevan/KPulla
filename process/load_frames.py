from plots.models import Transactions,Funds_DB,debts
from django.shortcuts import get_object_or_404
from django.conf import settings
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime, timedelta,date
from dateutil import relativedelta
import quandl
from .source import *
import os
"""
Implement Offline and Online Data, just to avoid unnecessary download of data. Later that may help in offline database

"""


#location = '/Users/santhoshvasudevan/Documents/WebDev/djangodash/'

def calc_debtvalue(Amount,name,roi,term,r):
	Date,Total_Value = [],[]
	if term == 1:
		n = 1
		years = 1
		months = 0
		t = r.years
	elif term == 2:
		n = 0.5
		years = 0
		months = 6
		tot_months = r.months + (r.years*12)
		t = tot_months//6
	elif term == 3:
		n = 0.25
		years = 0
		months = 3
		tot_months = r.months + (r.years*12)
		t = tot_months//4
	elif term == 4:
		n = 1/12
		years = 0
		months = 1
		tot_months = r.months + (r.years*12)
		t = tot_months
	if t:
		instance = get_object_or_404(debts,pk=name)
		temp_amount = instance.Deposit_Amount
		temp_date = instance.start_date + relativedelta.relativedelta(years=years,months=months)
		for i in range(t):
			Date.append(temp_date)	
			interest_accrued = Amount * (roi/n)**(n)
			instance.Deposit_value = temp_amount + interest_accrued
			temp_amount = instance.Deposit_value
			Total_Value.append(temp_amount)
			instance.maturity_date = temp_date + relativedelta.relativedelta(years=years,months=months)
			temp_date = instance.maturity_date 
		instance.save()
	return Date,Total_Value


def fundsvalue():
	#Mode = 'Offline'
	Mode = 'Online'
	quandl.ApiConfig.api_key = quandlkey
	uniquecodes = Transactions.objects.values_list('AMFICode',flat = True).distinct()
	Transaction_df_list = []
	Funds_df_list = []
	value_dictionary = {}			
	for uc in uniquecodes:
		ordered = Transactions.objects.filter(AMFICode__exact=uc).order_by('Date').values()
		#print(list(ordered))
		instance = get_object_or_404(Funds_DB, SchemeCode = uc)
		Name = instance.FundName
		#short_name = Name.replace(' ', '')
		short_name = ''.join(Name.split())
		transactions_df = pd.DataFrame(list(ordered))
		transactions_df.columns = ['ID','Scheme Code','Date','Amount Invested','Category']
		transactions_df = transactions_df[['Scheme Code','Date','Amount Invested','Category']]
		transactions_df.set_index('Date',inplace= True)
		Transaction_df_list.append(transactions_df)
		quandlcode = 'AMFI/'+str(transactions_df['Scheme Code'].iloc[0])
		fname = quandlcode + '.csv'
		filepath = os.path.join(settings.BASE_DIR,fname)

		if Mode == 'Online':
			start_date = transactions_df.index[0]
			print('*************************************************************')
			print('*************************************************************')
			downloaded_df = quandl.get(quandlcode,start_date = start_date, end_date = date.today())
			downloaded_df.drop(columns = ['Repurchase Price','Sale Price'],inplace = True)
			table_df = downloaded_df.join(transactions_df)
			table_df['Amount Invested'] = table_df['Amount Invested'].fillna(0)
			table_df['Amount Invested'] = table_df['Amount Invested'].astype('float')
			#table_df['Scheme Code'] = table_df['Scheme Code'].astype('int')
			table_df['Total Investment'] = table_df['Amount Invested'].cumsum()
			table_df['Units Bought'] = round(table_df['Amount Invested']/table_df['Net Asset Value'],3)
			table_df['Total Units'] = table_df['Units Bought'].cumsum()
			table_df['Total Value'] = round(table_df['Net Asset Value']*table_df['Total Units'],2)
			table_df['Profit Loss'] = table_df['Total Value']-table_df['Total Investment']
			table_df['Profit Loss'] = round(table_df['Profit Loss'],3)
			table_df['Abs Return'] = (table_df['Profit Loss']/table_df['Total Investment'])*100
			table_df['Abs Return'] = round(table_df['Abs Return'],3)
			table_df.to_csv(filepath)
		else:
			if os.path.isfile(filepath):
				table_df = pd.read_csv(filepath)
				table_df.set_index('Date',inplace=True)
			else:
				table_df = pd.DataFrame()
		value_dictionary.update({Name:[table_df,short_name]})
		Funds_df_list.append(table_df)
	return Funds_df_list,value_dictionary


def debtsvalue():
	debttransactions = debts.objects.all()
	#debt_df = pd.DataFrame(list(debttransactions))
	
	today = datetime.today()
	debts_df_list = []
	for entry in debttransactions:
		Date,Total_Value,Total_Investment = [],[],[]
		name = entry.comments
		Amount = entry.Deposit_Amount
		date = entry.start_date
		roi = entry.interest_rate/100
		start_date = entry.start_date
		Date.append(date)
		Total_Value.append(Amount)
		r = relativedelta.relativedelta(today,start_date)
		Date1,Total_Value1 = calc_debtvalue(Amount,name,roi,entry.compounding_term,r)
		Date = Date + Date1
		Total_Value = Total_Value + Total_Value1
		debts_df = pd.DataFrame({'Date':Date,
									'Name':name,
									'Amount Invested':Amount,
									'Total Value':Total_Value,
									})
		#debts_df['Date'] = Date
		#debts_df['Name'] = name
		#debts_df['Amount Invested'] = Amount
		#debts_df['Total Value'] = Total_Value
		debts_df.set_index('Date',inplace=True)
		debts_df_list.append(debts_df)

	return debts_df_list
def getSummary():
	debts_df_list = debtsvalue()
	Funds_df_list,value_dictionary = fundsvalue()

	def Summarize(listofframes,debts_df_list):
	    x = 1
	    TI,TV,Summary = pd.DataFrame(),pd.DataFrame(),pd.DataFrame()
	    for chucko in listofframes:
	        TI = TI.join(chucko[['Total Investment']],how = 'outer',rsuffix = str(x))
	        TV = TV.join(chucko[['Total Value']],how = 'outer',rsuffix = str(x))
	        x += 1
	    for chucko in debts_df_list:
	    	TI = TI.join(chucko[['Amount Invested']],how = 'outer',rsuffix = str(x+1))
	    	TV = TV.join(chucko[['Total Value']],how = 'outer',rsuffix = str(x+1))
	    	x += 1


	    TI.fillna(0,inplace = True)
	    TV.fillna(0,inplace = True)
	    Summary = pd.DataFrame(TI.sum(axis =1)).copy()
	    Summary.columns = ['Overall Invested']
	    Summary['Portfolio Value'] = pd.DataFrame(TV.sum(axis=1))
	    Summary['Abs Return'] = round((Summary['Portfolio Value']-Summary['Overall Invested'])/Summary['Overall Invested'],3)*100
	    return Summary

	return Summarize(Funds_df_list,debts_df_list),value_dictionary

