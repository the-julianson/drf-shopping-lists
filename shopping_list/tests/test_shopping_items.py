import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shopping_list.models import ShoppingItem, ShoppingList
from user.tests.conftest import create_user, create_authenticated_client



# CREATE 


@pytest.mark.django_db
def test_valid_shopping_item_is_created(create_shopping_list, create_user, create_authenticated_client):

    user = create_user()
    shopping_list = create_shopping_list(name="Groceries")
    shopping_list.members.add(user)

    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "noodles",
        "purchased": False,
    }

    client = create_authenticated_client(user)
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingItem.objects.first().name == data.get("name")


@pytest.mark.django_db
def test_create_shopping_item_missing_data_returns_bad_request(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list()
    shopping_list.members.add(user)

    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "Milk",
    }

    client = create_authenticated_client(user)
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# RETRIEVE 

@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(create_shopping_item, create_user, create_authenticated_client):

    user = create_user()
    name = "Pastries"

    shopping_item: ShoppingItem = create_shopping_item(user=user, name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    client = create_authenticated_client(user)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == name


# UPDATE 

@pytest.mark.django_db
def test_change_shopping_item_purchased_status(create_shopping_item, create_user, create_authenticated_client):

    name = "Pastries"
    user = create_user()

    shopping_item: ShoppingItem = create_shopping_item(user=user, name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    data = {
        "name": name,
        "purchased": True,
    }
    
    client = create_authenticated_client(user)
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["purchased"] == True


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_missing_data_returns_bad_request(
    create_shopping_item, create_user, create_authenticated_client
    ):
    user = create_user()
    name = "Pastries"

    shopping_item: ShoppingItem = create_shopping_item(user=user, name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    data = {
        "purchased": True,
    }
    
    client = create_authenticated_client(user)
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_partial_update(
    create_shopping_item, create_authenticated_client, create_user
    ):

    user = create_user()
    name = "Pastries"
    shopping_item: ShoppingItem = create_shopping_item(user=user, name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    data = {
        "purchased": True,
    }
    
    client = create_authenticated_client(user)
    response = client.patch(url, data, format="json")

    shopping_item.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert shopping_item.purchased is True


@pytest.mark.django_db
def test_shopping_item_is_deleted(create_shopping_item, create_authenticated_client, create_user):

    user = create_user()
    name = "Pastries"
    shopping_item: ShoppingItem = create_shopping_item(user=user, name=name)

    url = reverse(
        "shopping-item-detail", 
        kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id}
        )
    
    client = create_authenticated_client(user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingItem.objects.filter()) == 0


@pytest.mark.django_db
def test_not_member_of_list_can_not_add_shopping_item(create_user, create_authenticated_client, create_shopping_list):

    user_member = create_user()
    user_not_member = create_user(email="not-member@user.com")

    shopping_list: ShoppingList = create_shopping_list(user_member)

    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "noodles",
        "purchased": False,
    }

    client = create_authenticated_client(user_not_member)

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_add_shopping_items(create_user, create_shopping_list, admin_client):

    user = create_user()
    
    shopping_list: ShoppingList = create_shopping_list(user)

    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "noodles",
        "purchased": False,
    }

    response = admin_client.post(url, data, format="json")

    shopping_item = ShoppingItem.objects.first()

    assert response.status_code == status.HTTP_201_CREATED
    assert shopping_item.name == data.get("name")
    assert shopping_item.shopping_list_id == shopping_list.id



@pytest.mark.django_db
def test_shopping_item_detail_access_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):

    user_member = create_user()
    user_not_member = create_user(email="not-member@user.com")

    shopping_item: ShoppingItem = create_shopping_item(user=user_member)

    url = reverse("shopping-item-detail", args=[shopping_item.shopping_list_id, shopping_item.id])


    client = create_authenticated_client(user_not_member)

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shopping_item_update_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):

    user_member = create_user()
    user_not_member = create_user(email="not-member@user.com")

    shopping_item: ShoppingItem = create_shopping_item(user=user_member)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id})

    data = {
        "name": "SARASA",
        "purchased": True,
    }
    client = create_authenticated_client(user_not_member)

    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shopping_item_partial_update_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):

    user_member = create_user()
    user_not_member = create_user(email="not-member@user.com")

    shopping_item: ShoppingItem = create_shopping_item(user=user_member)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id})

    data = {
        "purchased": True,
    }
    client = create_authenticated_client(user_not_member)

    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shopping_item_delete_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):

    user_member = create_user()
    user_not_member = create_user(email="not-member@user.com")

    shopping_item: ShoppingItem = create_shopping_item(user=user_member)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id})

    client = create_authenticated_client(user_not_member)

    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_retrieve_single_shopping_item(create_user, admin_client, create_shopping_item):

    user_member = create_user()
    name = "Milk"

    shopping_item: ShoppingItem = create_shopping_item(user=user_member, name=name)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list_id, "item_pk": shopping_item.id})


    response = admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().name == name

