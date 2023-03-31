from django.contrib import admin

# Register your models here.
from shopping_list.models import ShoppingItem

admin.site.register(ShoppingItem)
