import pytest


from shopping_list.models import ShoppingItem, ShoppingList


@pytest.fixture(scope="session")
def create_shopping_list():

    def _create_shopping_list(name: str = "Groceries"):

        shopping_list = ShoppingList.objects.create(name=name)
        return shopping_list
    
    return _create_shopping_list


@pytest.fixture(scope="session")
def create_shopping_item():

    def _create_shopping_item(name: str = "Noodles", shopping_list: ShoppingList = None):

        if not shopping_list:
            shopping_list = ShoppingList.objects.create(name="Groceries")
        shopping_item = ShoppingItem.objects.create(name=name, purchased=False, shopping_list=shopping_list)

        return shopping_item
    
    return _create_shopping_item
