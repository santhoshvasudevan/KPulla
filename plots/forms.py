from django.forms import ModelForm
from .models import Funds_DB, Transactions


class TransactionsForm(ModelForm):
	class Meta:
		model = Transactions
		fields = ['AMFICode','Date','Amount_Invested']
