from django.core.management.base import BaseCommand, CommandError
import meli
from asgiref.sync import sync_to_async
import os
from datetime import date, timedelta, datetime
import mercadopago
import asyncio
import requests
import json
import math
import aiohttp
from dateutil import parser
#  from polls.models import Question as Poll
from auth.models import MLToken
from django.contrib.auth.models import User
from sales.models import Sale, Buyer, ProductSale, Shipping
from products.models import Product, Category


class Command(BaseCommand):
    help = 'load products from productos.csv'

    def __init__(self):
        client_id = os.environ["GOYLE_ID"]
        client_secret = os.environ["GOYLE_SECRET"]
        self.ayer = str(date.today()-timedelta(days=30))
        self.hoy = str(date.today())
        self.mp = mercadopago.MP(client_id, client_secret)
        self.access_token = self.mp.get_access_token()
        self.user_id = "177416286"

    async def fetch(self, session, url):
        async with session.get(url) as response:
            response = await response.text()
            return json.loads(response)

    def get_root_url(self, inicio, fin):
        url = 'https://api.mercadolibre.com/orders/search?seller=%s&access_token=%s' % (
            self.user_id, self.access_token)
        url = url+'&order.date_created.from='+inicio+'T00:00:00.000-00:00'
        return url+'&order.date_created.to='+fin+'T00:00:00.000-00:00'

    def get_item_details(self, item_id):
        item_details_url = 'https://api.mercadolibre.com/items/' + \
            str(item_id)+'?access_token='+self.access_token
        item_details = requests.get(item_details_url)
        return json.loads(item_details.text)

    def get_category_details(self, category_id):
        item_details_url = 'https://api.mercadolibre.com/categories/' + \
            str(category_id)+'?access_token='+self.access_token
        item_details = requests.get(item_details_url)
        return json.loads(item_details.text)

    def get_total_pages(self, inicio, fin):
        url = self.get_root_url(inicio, fin)
        ventasResponse = requests.get(url)
        ventas = json.loads(ventasResponse.text)
        return int(math.ceil(ventas['paging']['total']/50))

    async def get_ventas(self, inicio, fin, page):
        ventas_ = []
        urlfinal = self.get_root_url(inicio, fin)+'&offset='+str(page*50)
        async with aiohttp.ClientSession() as session:
            ventasResponse = await self.fetch(session, urlfinal)
            #  ventasResponse = requests.get(urlfinal)
            ventas = ventasResponse.get('results', [])
            tasks = []
            for venta in ventas:
                try:
                    shipping_id = venta['shipping']['id']
                    shipping_details_url = 'https://api.mercadolibre.com/shipments/' + \
                        str(shipping_id)+'?access_token='+self.access_token
                    task = asyncio.ensure_future(
                        self.fetch(session, shipping_details_url))
                    tasks.append(task)
                except Exception as e:
                    print("ERROR:", e)
                    continue

            responses = await asyncio.gather(*tasks)
            i=0
            for venta, shipping_details in zip(ventas, responses):
                i+=1
                buyer = venta.get("buyer", {})
                sale = {}
                sale["id"] = venta.get("id")
                sale["total_amount"] = venta.get("total_amount", 0)
                sale["status"] = venta.get("status")
                sale["date_created"] = venta.get("date_created")
                sale["buyer"] = buyer
                shipping = {}
                shipping_id = shipping_details.get("id",None)
                if shipping_id:
                    shipping["id"] = shipping_id
                    shipping["mode"] = shipping_details["mode"]
                    shipping["status"] = shipping_details.get(
                        'status', 'Sin status')
                    shipping["delivery_date"] = shipping_details.get(
                        'status_history', {}).get('date_delivered', '')
                    shipping["logistic"] = shipping_details.get(
                        'logistic_type', 'No especificado')
                sale["shipping"] = shipping
                items = []
                for item in venta['order_items']:
                    item_details = self.get_item_details(item['item']['id'])
                    product = {}
                    product["id"] = item['item']['id']
                    variation_id = item["item"]["variation_id"]
                    variation_attributes = None
                    if variation_id is None:
                        product["variation_id"] = None
                        product["inventory_id"] = item_details["inventory_id"]
                        product["available_quantity"] = item_details["available_quantity"]
                    else:
                        product["variation_id"] = item["item"]["variation_id"]
                        variation = None
                        for v in item_details["variations"]:
                            if v["id"] == variation_id:
                                variation = v
                        product["inventory_id"] = variation["inventory_id"] if variation else None
                        product["available_quantity"] = variation["available_quantity"] if variation else 0
                        variation_attributes = item.get(
                            'item', {}).get('variation_attributes')
                    product["attributes"] = variation_attributes if variation_attributes else None
                    product["title"] = item["item"]["title"]
                    product["quantity_saled"] = item["quantity"]
                    product["full_unit_price"] = item["full_unit_price"]
                    category_id = item["item"]["category_id"]
                    category_details = self.get_category_details(category_id)
                    #  print("CATEGORY DETAILS",category_details)
                    product["category_id"] = category_id
                    product["category_title"] = category_details["name"]

                    items.append(product)
                sale["products"] = items
                ventas_.append(sale)

            return ventas_

    @sync_to_async
    def save_products(self, sales):
        goyle = User.objects.get(username="goyle")
        for sale in sales:
            json_sale = json.dumps(sale, indent=2)
            buyer, created = Buyer.objects.get_or_create(
                ml_id=sale["buyer"]["id"], user=goyle)
            if created:
                buyer.nickname = sale["buyer"]["nickname"]
                buyer.first_name = sale["buyer"]["first_name"]
                buyer.last_name = sale["buyer"]["last_name"]
            buyer.email = sale["buyer"]["email"]
            buyer.save()
            venta, created = Sale.objects.get_or_create(
                user=goyle, ml_id=sale["id"], buyer=buyer)
            venta.date_created = sale.get("date_created")
            venta.total_amount = sale.get("total_amount", 0)
            venta.status = sale["status"]
            venta.save()
            if sale["shipping"]:
                shipping_id = sale["shipping"].get("id")
                if shipping_id:
                    shipping, created = Shipping.objects.get_or_create(
                        ml_id=sale["shipping"]["id"], sale=venta)
                    shipping.mode = sale["shipping"].get("mode")
                    shipping.status = sale["shipping"].get("status")
                    shipping.delivery_date = sale["shipping"].get("delivery_date")
                    shipping.logistic = sale["shipping"].get('logistic')
                    shipping.save()
            for product in sale["products"]:
                category, created = Category.objects.get_or_create(
                    ml_id=product["category_id"])
                if created:
                    category.title = product.get("category_title")
                    category.save()
                new_product, created = Product.objects.get_or_create(
                    ml_id=product["id"], variation_id=product["variation_id"], category=category, user=goyle)
                new_product.title = product.get("title")
                new_product.available_quantity = product["available_quantity"]
                new_product.attributes = product["attributes"]
                new_product.save()
                psale, created = ProductSale.objects.get_or_create(
                    sale=venta, product=new_product)
                if created:
                    psale.quantity = product.get("quantity_saled", 0)
                    psale.full_unit_price = product.get("full_unit_price", 0)
                    psale.save()
            #  print(json_sale)

    async def main(self):
        total_pages = self.get_total_pages(self.ayer, self.hoy)
        logfile=open("goyle.log",'a')
        logfile.write("HOY: %s\n" % self.hoy)
        logfile.write("AYER %s\n" % self.ayer)
        logfile.write("TOTAL PAGES %s\n" % total_pages)
        logfile.close()
        #  if total_pages > 0:

        ventas = []
        for page in range(total_pages):
            ventas = await self.get_ventas(self.ayer, self.hoy, page)
            logfile=open("goyle.log",'a')
            if not ventas:
                logfile.write("No hay ventas\n", ventas)
                continue
            logfile.write("Page %s de %s\n" % (page+1, total_pages))
            await self.save_products(ventas)
            logfile.close()
            #  await self.save_products(ventas)
            #  for venta in ventas:
            #      print("ITEM ID:",venta["ml_id"])

    def handle(self, *args, **options):
        asyncio.run(self.main())
