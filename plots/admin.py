from django.contrib import admin
from .models import Funds_DB,Transactions,debts

# Register your models here.


admin.site.register(Funds_DB)
admin.site.register(Transactions)
admin.site.register(debts)
