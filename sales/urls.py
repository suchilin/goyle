from django.urls import path
from . import views

urlpatterns = [
    path('webhook', views.webhook, name='webhook'),
    path('', views.SalesList.as_view(template_name='sales_list.html'), name='index')
]
