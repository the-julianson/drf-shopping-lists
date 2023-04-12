import uuid

from django.db import models
from django.conf import settings


class ShoppingList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name


class ShoppingItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    purchased = models.BooleanField()
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name="shopping_items")

    def __str__(self):
        return f"{self.name}"
