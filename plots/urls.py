from django.urls import path
from . import views


urlpatterns = [
		path('',views.home,name = 'home'),
		path('transequity',views.transequity,name='transequity'),
		path('transdebt',views.transdebt,name='transdebt'),
		path('returns',views.returns,name='returns'),
		path('risks',views.risks,name='risks'),
		path('ratios',views.ratios,name='ratios'),
		path('rebalance',views.rebalance,name='rebalance'),
]