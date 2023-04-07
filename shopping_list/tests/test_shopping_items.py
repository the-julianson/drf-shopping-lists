import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shopping_list.models import ShoppingItem, ShoppingList



# CREATE 


@pytest.mark.django_db
def test_valid_shopping_item_is_created(create_shopping_list):

    shopping_list = create_shopping_list(name="Groceries")


    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "noodles",
        "purchased": False,
    }

    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingItem.objects.first().name == data.get("name")


@pytest.mark.django_db
def test_create_shopping_item_missing_data_returns_bad_request(create_shopping_list):
    shopping_list = create_shopping_list()


    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "Milk",
    }

    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# RETRIEVE 

@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(create_shopping_item):

    name = "Pastries"

    shopping_item: ShoppingItem = create_shopping_item(name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == name


# UPDATE 

@pytest.mark.django_db
def test_change_shopping_item_purchased_status(create_shopping_item):

    name = "Pastries"

    shopping_item: ShoppingItem = create_shopping_item(name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    data = {
        "name": name,
        "purchased": True,
    }
    
    client = APIClient()
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["purchased"] == True


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_missing_data_returns_bad_request(create_shopping_item):
    name = "Pastries"

    shopping_item: ShoppingItem = create_shopping_item(name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    data = {
        "purchased": True,
    }
    
    client = APIClient()
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_partial_update(create_shopping_item):

    name = "Pastries"
    shopping_item: ShoppingItem = create_shopping_item(name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    data = {
        "purchased": True,
    }
    
    client = APIClient()
    response = client.patch(url, data, format="json")

    shopping_item.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert shopping_item.purchased is True


@pytest.mark.django_db
def test_shopping_item_is_deleted(create_shopping_item):

    name = "Pastries"
    shopping_item: ShoppingItem = create_shopping_item(name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    client = APIClient()
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingItem.objects.filter()) == 0