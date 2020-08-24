import requests
import re
from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import render,get_object_or_404
from plots.models import Funds_DB,Transactions
'''
Funds_Transac_Info is dictionary with numeric order keys, with dictionary value containing Scheme_Code etc., as below
'''
Funds_Transac_Info = {
	1 : {'Scheme_Code': 122639,
			'Purchases': [('2019-8-9',100000),('2019-7-9',100000),('2019-10-9',100000),('2019-11-11',100000),('2019-12-9',100000),('2020-1-23',100000),('2020-3-2',100000),
			('2019-2-3',100000),('2019-4-7',100000),('2019-5-4',100000),('2019-6-9',100000),('2019-7-6',100000),('2019-8-4',100000)]},
}
class Command(BaseCommand):
	help = 'Latest available information of funds are refreshed'
	
    # def add_arguments(self, parser):
    #     parser.add_argument('textfile', nargs='+', type=str)
	def handle(self, *args, **options):
		tuplesoffunds = []
		try:
			self.stdout.write(self.style.SUCCESS('Loading Funds from AMFI database...'))
			response = requests.get('https://www.amfiindia.com/spages/NAVAll.txt?')
			textdata = response.text
		except:
			raise CommandError('AMFI url cannot be reached')
		regex = re.compile(r"(^\d{5,7});[INA-Z0-9]*;.*;([A-Za-z\d\s-]*);([-+]?\d*\.\d+|\d+);.*",re.MULTILINE)
		
		for matches in regex.finditer(textdata):
			SchemeCode = matches.group(1)
			FundName = matches.group(2)
			tuplesoffunds.append((SchemeCode,FundName))

		tuplesoffunds.sort(key=lambda tup: tup[1])
			# SchemeCode = Funds_DB.objects.get_or_create(
			# 			SchemeCode = matches.group(1)
			# 		)
			# FundName = Funds_DB.objects.get_or_create(
			# 			FundName = matches.group(2)
			# 	)
			
		for entries in tuplesoffunds:
			entry = Funds_DB(
				FundName = entries[1],
				SchemeCode = entries[0]
				)

			entry.save()
		self.stdout.write(self.style.SUCCESS('Funds Successfully Imported'))
		self.stdout.write(self.style.SUCCESS('Adding available transactions...'))
		for key in Funds_Transac_Info:
			instance = get_object_or_404(Funds_DB, SchemeCode = Funds_Transac_Info[key]['Scheme_Code'])
			for dt,amnt in Funds_Transac_Info[key]['Purchases']:
				Transactions.objects.create(AMFICode = instance,
											Date = dt,
											Amount_Invested = amnt)
		self.stdout.write(self.style.SUCCESS('Basic Transactions added!!'))







