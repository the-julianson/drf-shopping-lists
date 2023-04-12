import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shopping_list.models import ShoppingItem, ShoppingList
from user.tests.conftest import create_user, create_superuser, create_authenticated_client



@pytest.mark.django_db
def test_valid_shopping_list_is_created(create_user, create_authenticated_client):
    url = reverse("all-shopping-lists")
    data = {
        "name": "Groceries",
    }

    client = create_authenticated_client(create_user())
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.first().name == "Groceries"


@pytest.mark.django_db
def test_shopping_list_name_missing_returns_bad_request(create_user, create_authenticated_client):
    url = reverse("all-shopping-lists")
    data = {
        "invalid_field_name": "random",
    }

    client = create_authenticated_client(create_user())
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# LIST 

@pytest.mark.django_db
def test_client_retrieves_only_shopping_lists_they_are_member_of(create_user, create_authenticated_client, create_shopping_list):
    url = reverse("all-shopping-lists")

    user_is_member = create_user(email="is-member@mail.com")
    user_is_not_member = create_user(email="is-not-member@mail.com")
    create_shopping_list(user=user_is_member, name="Groceries")
    create_shopping_list(user=user_is_not_member, name="Books")

    client = create_authenticated_client(user_is_member)

    number_shopping_list_from_user_is_member = ShoppingList.objects.filter(members=user_is_member).count()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == number_shopping_list_from_user_is_member

    for shop_list in response.data:

        assert shop_list["name"] == ShoppingList.objects.filter(id=shop_list["id"]).first().name


# RETRIEVE 

@pytest.mark.django_db
def test_shopping_list_is_retrieved_by_id(create_shopping_list, create_user, create_authenticated_client):
    user = create_user()
    
    shopping_list = create_shopping_list(user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = create_authenticated_client(user)

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_includes_only_corresponding_items(
    create_user, create_shopping_list, create_authenticated_client, create_shopping_item
    ):

    user_1 = create_user(email="a@a.com")
    user_2 = create_user(email="b@b.com")

    shopping_list = create_shopping_list(name="Groceries")
    shopping_list.members.add(user_1)
    
    another_shopping_list = create_shopping_list(name="Books")
    another_shopping_list.members.add(user_2)

    create_shopping_item(shopping_list=shopping_list, name="Eggs", purchased=False)
    create_shopping_item(shopping_list=another_shopping_list, name="The seven sisters", purchased=False)

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = create_authenticated_client(user_1)
    response = client.get(url)

    assert len(response.data["shopping_items"]) == 1
    assert response.data["shopping_items"][0]["name"] == "Eggs"


# UPDATE

@pytest.mark.django_db
def test_shopping_list_name_is_changed(create_user, create_shopping_list, create_authenticated_client):

    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("shopping-list-detail", kwargs={"pk": shopping_list.id})

    data = {
        "name": "Food", 
    }

    client = create_authenticated_client(user)

    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data.get("name")


@pytest.mark.django_db
def test_shopping_list_not_changed_because_wrong_field_names(create_user, create_shopping_list, create_authenticated_client):

    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("shopping-list-detail", kwargs={"pk": shopping_list.id})

    data = {
        "some_random_field_name": "Food", 
    }

    client = create_authenticated_client(user)

    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_list_name_is_changed_with_partial_update(create_user, create_shopping_list, create_authenticated_client):

    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("shopping-list-detail", kwargs={"pk": shopping_list.id})

    data = {
        "name": "Food", 
    }

    client = create_authenticated_client(user)

    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data.get("name")


@pytest.mark.django_db
def test_partial_update_with_missing_name_has_no_impact(create_shopping_list, create_user, create_authenticated_client):

    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("shopping-list-detail", kwargs={"pk": shopping_list.id})

    data = {
        "some_random_field_name": "Food", 
    }

    client = create_authenticated_client(user)

    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK



@pytest.mark.django_db
def test_shopping_list_is_deleted(create_shopping_list, create_user, create_authenticated_client):
    user = create_user()

    shopping_list = create_shopping_list(user)

    url = reverse("shopping-list-detail", kwargs={"pk": shopping_list.id})

    client = create_authenticated_client(user)

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingList.objects.all()) == 0


@pytest.mark.django_db
def test_update_shopping_list_restricted_if_not_member(create_user, create_authenticated_client, create_shopping_list):
    user_not_member = create_user()
    user_member = create_user(email="usermember@email.com")

    shopping_list = create_shopping_list(user_member)
    client = create_authenticated_client(user_not_member)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    response_1 = client.put(url, data=data, format="json")
    response = client.get(url)

    assert response_1.status_code == status.HTTP_403_FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_partial_update_shopping_list_restricted_if_not_member(create_user, create_authenticated_client, create_shopping_list):
    user_not_member = create_user()
    user_member = create_user(email="usermember@email.com")

    shopping_list = create_shopping_list(user_member)
    client = create_authenticated_client(user_not_member)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_shopping_list_restricted_if_not_member(create_user, create_authenticated_client, create_shopping_list):
    user_not_member = create_user()
    user_member = create_user(email="usermember@email.com")

    shopping_list = create_shopping_list(user_member)
    client = create_authenticated_client(user_not_member)

    url = reverse("shopping-list-detail", args=[shopping_list.id])


    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_retrieve_shopping_list(create_user, create_shopping_list, admin_client):

    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    response = admin_client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK


