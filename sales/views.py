from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import meli
from meli.rest import ApiException
from pprint import pprint
import json
import os
from auth.models import MLToken
from django.contrib.auth.models import User
from .models import Sale, Buyer, ProductSale, Shipping
from products.models import Product, Category
import requests
from django.views.generic import ListView

# Create your views here.
class SalesList(ListView):
    model = Sale
    context_object_name = 'sales'
    paginate_by = 100

    def get_queryset(self):
        filter_val = self.request.GET.get('filter', '')
        if filter_val:
            new_context = Sale.objects.filter(
                ml_id__icontains=filter_val,
            )
            return new_context
        return Sale.objects.all()

    def get_context_data(self, **kwargs):
        context = super(SalesList, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', '')
        return context

@csrf_exempt
def webhook(request):
    if request.method != 'POST':
        return JsonResponse({'status': 405, 'message': 'Method not allowed'}, status=405)

    print("POST PARAMETERS: ", json.loads(request.body))
    payload = json.loads(request.body)
    user_id = payload.get("user_id")
    resource = payload.get("resource")
    topic = payload.get("topic")

    try:
        ml_token = MLToken.objects.get(ml_user_id=user_id)
        print("TOKEN ", ml_token.access_token)
        with meli.ApiClient() as api_client:
            api_instance = meli.OAuth20Api(api_client)
            grant_type = 'refresh_token'
            client_id = os.environ.get('ML_APP_ID')
            client_secret = os.environ.get('ML_APP_SECRET')
            redirect_uri = "http://localhost:8000/auth/callback"
            code = ''
            refresh_token = ml_token.refresh_token
            api_response = api_instance.get_token(
                grant_type=grant_type,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=code,
                refresh_token=refresh_token
            )
        access_token = api_response["access_token"]
        refresh_token = api_response["refresh_token"]
        ml_user_id = api_response["user_id"]
        ml_token.ml_user_id = ml_user_id
        ml_token.access_token = access_token
        ml_token.refresh_token = refresh_token
        ml_token.save()
        api_instance = meli.RestClientApi(api_client)
        print("TOPIC: ", topic)
        if topic == "shipments":
            shipping_response = api_instance.resource_get(resource, access_token)
            order_id = shipping_response.get('order_id', '-')
            print("ORDER ID", order_id)
            order_response = api_instance.resource_get(
                "/orders/%s" % order_id, access_token)
            order_items = order_response.get("order_items", None)
            buyer_from_response = order_response.get("buyer", {})
            buyer, created = Buyer.objects.get_or_create(
                ml_id=buyer_from_response["id"], user=ml_token.user)
            if created:
                buyer.nickname = buyer_from_response["nickname"]
                buyer.first_name = buyer_from_response["first_name"]
                buyer.last_name = buyer_from_response["last_name"]
            buyer.email = buyer_from_response["email"]
            buyer.save()
            sale, created = Sale.objects.get_or_create(
                user=ml_token.user, ml_id=order_id, buyer=buyer)
            sale.total_amount = order_response.get("total_amount", 0)
            sale.status = order_response["status"]
            sale.save()
            if shipping_response:
                shipping,created = Shipping.objects.get_or_create(ml_id=shipping_response["id"], sale=sale)
                shipping.mode=shipping_response.get("mode")
                shipping.status=shipping_response.get("status")
                shipping.delivery_date = shipping_response.get(
                    'status_history', {}).get('date_delivered', '')
                shipping.logistic = shipping_response.get(
                    'logistic_type', 'No especificado')
                shipping.save()
            if order_items:
                for item_ in order_items:
                    item = item_.get("item", {})
                    item_id = item.get("id")
                    variation_id = item.get("variation_id", "-")
                    category_id = item.get("category_id", None)
                    new_category, created = Category.objects.get_or_create(
                        ml_id=category_id)
                    if created:
                        category_response = api_instance.resource_get(
                            "/categories/%s" % category_id, access_token)
                        print("CATEGORY", category_response)
                        new_category.ml_id = category_id
                        new_category.title = category_response.get("name")
                        new_category.save()
                    product_response = api_instance.resource_get("/items/%s" % item_id,access_token)
                    available_quantity = product_response.get("available_quantity", 0)
                    print("available_quantity", available_quantity)
                    variations = product_response.get("variations",[])
                    if len(variations)>0:
                        for variation in variations:
                            if variation["id"]==variation_id:
                                print("VARIATION",variation)
                                available_quantity=variation["available_quantity"]
                    new_product, created = Product.objects.get_or_create(
                        ml_id=item_id, variation_id=variation_id, category=new_category, user=ml_token.user)
                    new_product.title = item.get("title")
                    new_product.available_quantity = available_quantity
                    new_product.save()
                    print("ITEM:", item_)
                    psale = ProductSale(sale=sale, product=new_product)
                    psale.quantity = item_.get("quantity", 0)
                    psale.full_unit_price = item_.get("full_unit_price", 0)
                    psale.save()
                    print("CATEGORY ID: ", category_id)
            #  print(order_response)
            #  if Sale.objects.filter(ml_id=order_id).exists():
            #      print("API RESPONSE ", api_response)
            #  else:
            #      print("ORDERN DOSN'T EXIST")
    except ApiException as e:
        print("Exception when calling OAuth20Api->get_token: %s\n" % e)
    except Exception as e:
        print("ERROR ", e)
    return JsonResponse({"message": "ok"})
