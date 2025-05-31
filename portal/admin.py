from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','description', 'price', 'stock','image')  # or your fields

# Register your models here.
