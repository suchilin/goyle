from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('login',views.login_ml, name='login'),
    path('to_mercadolibre',views.to_mercadolibre, name='to_mercadolibre'),
    path('logout',views.logout, name='logout'),
    path('callback', views.callback, name='calllback')
]
