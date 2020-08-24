from django.db import models

# Create your models here.
class Funds_DB(models.Model):
	FundName = models.CharField(max_length = 125,null = True)
	SchemeCode = models.IntegerField(primary_key=True)

	def __str__(self):
		return str(self.FundName)

class Transactions(models.Model):
	AMFICode = models.ForeignKey(Funds_DB, null = True ,on_delete=models.CASCADE)
	Date = models.DateField(blank = False, null = False)
	Amount_Invested = models.DecimalField(max_digits=15,decimal_places=2)
	category = models.CharField(max_length=10,default="equity")

	def __str__(self):
		return str(self.Date)+'_'+str(self.AMFICode.FundName)[:5].strip()+'_'+str(int(self.Amount_Invested))

class debts(models.Model):
	dep_terms = (
				(1,"Years"),
				(2,"Months"),
				(3,"Days"),		
				)
	comp_terms = (
				(1,"Yearly"),
				(2,"Half Yearly"),
				(3,"Quarterly"),
				(4,"Monthly"),
				)

	Deposit_Amount = models.DecimalField(max_digits=15,decimal_places=2,null=False)
	start_date = models.DateField(blank=False,null=False)
	interest_rate = models.DecimalField(max_digits=5,decimal_places=2,null=False)
	Deposit_value = models.DecimalField(max_digits=15,decimal_places=2, null = True,blank=True)
	maturity_date = models.DateField(blank=True,null=True)
	compounding_term = models.SmallIntegerField(choices=comp_terms)
	comments = models.CharField(max_length=25,primary_key=True)


	def __str__(self):
		return str(self.comments)+'_'+str(self.start_date)