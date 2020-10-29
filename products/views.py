from django.shortcuts import render
from django.views.generic import ListView
from .models import Product

# Create your views here.
class ProductList(ListView):
    model = Product
    context_object_name = 'products'
    paginate_by = 100

    def get_queryset(self):
        filter_val = self.request.GET.get('filter', '')
        if filter_val:
            new_context = Product.objects.filter(
                name__icontains=filter_val,
            )
            return new_context
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', '')
        return context
