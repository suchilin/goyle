from django.contrib import admin
from django.urls import path, include
from sales import views

urlpatterns = [
    path('',views.SalesList.as_view(template_name='sales_list.html')),
    path('admin/', admin.site.urls),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('auth/', include(('auth.urls', 'auth'), namespace='auth')),
    path('sales/', include(('sales.urls', 'sales'), namespace='sales')),
    path('reports/', include(('reports.urls', 'reports'), namespace='reports'))
]
