import pytest

from user.models import CustomUser
from shopping_list.models import ShoppingItem, ShoppingList


@pytest.fixture(scope="session")
def create_shopping_list():

    def _create_shopping_list(user: CustomUser = None, name: str = "Groceries"):

        shopping_list = ShoppingList.objects.create(name=name)
        shopping_list.members.add(user)
        return shopping_list
    
    return _create_shopping_list


@pytest.fixture(scope="session")
def create_shopping_item():

    def _create_shopping_item(
            user: CustomUser = None, name: str = "Noodles", shopping_list: ShoppingList = None, purchased: bool = False
            ):

        if not shopping_list:
            shopping_list = ShoppingList.objects.create(name="Groceries")
        

        if user and user not in shopping_list.members.all():
            shopping_list.members.add(user)

        shopping_item = ShoppingItem.objects.create(name=name, purchased=purchased, shopping_list=shopping_list)

        return shopping_item
    
    return _create_shopping_item
