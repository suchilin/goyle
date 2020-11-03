from django.shortcuts import render
from sales.models import ProductSale
from django.db.models import Count
from django.db.models.functions import TruncDate
import json
from django.db.models.expressions import RawSQL

# Create your views here.
def sales_report(request):
    productss=ProductSale.objects.annotate(
        only_date=TruncDate('sale__date_created'),
        attribute=RawSQL("attributes->0->'value_name'::varchar",'')
    ).all().order_by("-only_date","product__title")
    start = request.GET.get("start")
    end = request.GET.get("end")
    #  print("START: ",start, "END: ",end)
    if start:
        productss = productss.filter(sale__date_created__gte=start)
    if end:
        end_=end+"T23:59:59"
        productss = productss.filter(sale__date_created__lte=end_)
    report = productss.values(
        "product__title",
        "full_unit_price",
        "attribute",
        "product__available_quantity").annotate(c=Count("product__id"))
    return render(request, "sales_report.html", {"report":report, "start":start, "end":end})
