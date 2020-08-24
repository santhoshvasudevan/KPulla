from ajax_select import register, LookupChannel
from .models import Funds_DB

@register('funds_DB')

class FundsLookup(LookupChannel):

    model = Funds_DB

    def get_query(self, q, request):
        return self.model.objects.filter(FundName__startswith=q).order_by('FundName')[0:50]