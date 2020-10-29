from django.db import models
from django.contrib.auth.models import User
from products.models import Product

# Create your models here.


class Buyer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ml_id = models.BigIntegerField(default=0)
    nickname = models.CharField(max_length=255, default="-")
    first_name = models.CharField(max_length=255, default="-")
    last_name = models.CharField(max_length=255, default="-")
    email = models.EmailField(max_length=255, default="-")
    phone = models.CharField(max_length=20, default="-")

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ml_id = models.BigIntegerField(default=0)
    total_amount = models.FloatField(default=0)
    buyer = models.ForeignKey(Buyer, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=20, default="-")
    date_created = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Buyer: %s total: %s" % (self.buyer, self.total_amount)


class Shipping(models.Model):
    ml_id = models.CharField(max_length=20)
    sale = models.OneToOneField(
        Sale, on_delete=models.CASCADE
    )
    mode = models.CharField(max_length=20, default="")
    status = models.CharField(max_length=100, default="-")
    delivered_date = models.DateTimeField(null=True, blank=True)
    logistic = models.CharField(max_length=50, default="No especificado")


class ProductSale(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=0)
    full_unit_price = models.FloatField(default=0)
