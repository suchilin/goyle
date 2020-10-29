from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    ml_id = models.CharField(max_length=20, default="-")
    title = models.CharField(max_length=255, default="-")
    name = models.CharField(max_length=255, default="-")

    def __str__(self):
        if self.name == "-":
            return self.title
        return self.name


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ml_id = models.CharField(max_length=20, default="-")
    variation_id = models.BigIntegerField(null=True, blank=True)
    inventory_id = models.BigIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, default="-")
    name = models.CharField(max_length=255, default="-")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    available_quantity = models.IntegerField(default=0)
    attributes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title


class ProductAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
