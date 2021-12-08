from plots.models import Transactions,Funds_DB,debts
from django.shortcuts import get_object_or_404
from django.conf import settings
import pandas as pd
import requests, json
from dataclasses import dataclass, field
from datetime import datetime, timedelta,date
from dateutil import relativedelta
import quandl
from .source import *
import os
import pdb
"""
Implement Offline and Online Data, just to avoid unnecessary download of data. Later that may help in offline database

"""
source = 'mfapi'
#source = 'quandl'

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


def fundsvalue(mode='Online'):
	#Mode = 'Offline'
	#Mode = 'Online'
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
		mfapilink = 'https://api.mfapi.in/mf/'+str(transactions_df['Scheme Code'].iloc[0])
		fname = quandlcode + '.csv'
		filepath = os.path.join(settings.BASE_DIR,fname)

		if mode == 'Online':
			start_date = pd.to_datetime(transactions_df.index[0])
			print('*************************************************************')
			
			if source == 'quandl':
				downloaded_df = quandl.get(quandlcode,start_date = start_date, end_date = date.today())
				downloaded_df.drop(columns = ['Repurchase Price','Sale Price'],inplace = True)
			elif source == 'mfapi':

				end_date = pd.to_datetime('today')
				webresponse = requests.get(mfapilink)
				tmp = json.loads(webresponse.text)
				req_data = pd.DataFrame.from_dict(tmp['data'])
				req_data.columns = ['Date', 'Net Asset Value']
				req_data['Date'] = pd.to_datetime(req_data['Date'],format='%d-%m-%Y')
				req_data['Net Asset Value'] = req_data['Net Asset Value'].astype(float)
				print('*************************************************************')
				#print(type(end_date),type(start_date))
				
				downloaded_df = req_data[(req_data['Date']>=start_date) & (req_data['Date']<end_date)]
				downloaded_df.sort_values(by='Date')
				downloaded_df.set_index('Date',inplace= True)

			table_df = downloaded_df.join(transactions_df)
			table_df.sort_index(inplace=True)
			#pdb.set_trace()
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
				table_df['Date'] = pd.to_datetime(table_df['Date'],format='%Y-%m-%d')
				table_df.set_index('Date',inplace=True)
			else:
				table_df = pd.DataFrame()
		value_dictionary.update({Name:[table_df,short_name]})
		Funds_df_list.append(table_df)
		#pdb.set_trace()
	return Funds_df_list,value_dictionary


def debtsvalue(mode='Online'):
	debttransactions = debts.objects.all()
	#debt_df = pd.DataFrame(list(debttransactions))
	
	today = datetime.today()
	debts_df_list = []
	for entry in debttransactions:
		Date,Total_Value,Total_Investment = [],[],[]
		name = entry.comments
		Amount = entry.Deposit_Amount
		date = pd.to_datetime(entry.start_date,format='%Y-%m-%d')
		roi = entry.interest_rate/100
		start_date = pd.to_datetime(entry.start_date,format='%Y-%m-%d')
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
		#debts_df['Date'] = pd.to_datetime(debts_df['Date'],format='%d-%m-%Y')
		debts_df.set_index('Date',inplace=True)
		debts_df.sort_index(inplace=True)
		#pdb.set_trace()
		debts_df_list.append(debts_df)

	return debts_df_list
def getSummary(mode='Online'):
	debts_df_list = debtsvalue(mode)
	Funds_df_list,value_dictionary = fundsvalue(mode)

	def Summarize(listofframes,debts_df_list):
	    x = 1
	    TI,TV,Summary = pd.DataFrame(),pd.DataFrame(),pd.DataFrame()
	    for chucko in listofframes:
	        TI = TI.join(chucko[['Total Investment']],how = 'outer',rsuffix = str(x))
	        TV = TV.join(chucko[['Total Value']],how = 'outer',rsuffix = str(x))
	        x += 1
	    for chucko in debts_df_list:
	    	TI = TI.join(chucko[['Amount Invested']],how = 'outer',rsuffix = str(x+1))
	    	TI[TI.columns[-1]] = TI[TI.columns[-1]].astype(float)
	    	TV = TV.join(chucko[['Total Value']],how = 'outer',rsuffix = str(x+1))
	    	TV[TV.columns[-1]] = TV[TV.columns[-1]].astype(float)
	    	x += 1
	    #pdb.set_trace()
	    TI.sort_index(inplace=True)
	    TV.sort_index(inplace=True)
	    TI.ffill(inplace=True)
	    TV.ffill(inplace=True)
	    TI.fillna(0,inplace = True)
	    TV.fillna(0,inplace = True)
	    TI.to_csv(os.path.join(settings.BASE_DIR,'TI_'+str(x)+'.csv'))
	    TV.to_csv(os.path.join(settings.BASE_DIR,'TV_'+str(x)+'.csv'))
	    Summary = pd.DataFrame(TI.sum(axis =1,numeric_only=True)).copy()
	    Summary.columns = ['Overall Invested']
	    Summary['Portfolio Value'] = pd.DataFrame(TV.sum(axis=1,numeric_only=True))
	    lowval = min(Summary['Overall Invested'].min(),Summary['Portfolio Value'].min())
	    highval = max(Summary['Overall Invested'].max(),Summary['Portfolio Value'].max())
	    Summary['OI_Norm'] = (Summary['Overall Invested'] - lowval)/ (highval - lowval)
	    Summary['PV_Norm'] = (Summary['Portfolio Value'] - lowval)/(highval - lowval)
	    Summary['Abs Return'] = round((Summary['Portfolio Value']-Summary['Overall Invested'])/Summary['Overall Invested'],3)*100
	    #pdb.set_trace()
	    return Summary

	return Summarize(Funds_df_list,debts_df_list),value_dictionary

