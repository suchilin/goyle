from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductList.as_view(template_name='list.html'), name='index')
]
