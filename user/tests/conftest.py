import pytest

from rest_framework.test import APIClient

from user.models import CustomUser


@pytest.fixture(scope="session")
def create_user():
    def _create_user(email: str = "a@a.com"):
        return CustomUser.objects.create_user(email, password="testpass123")
    
    return _create_user

@pytest.fixture(scope="session")
def create_superuser():
    def _create_user(**kwargs):
        return CustomUser.objects.create_superuser(email="a@a.com", password="testpass123")
    
    return _create_user


@pytest.fixture(scope="session")
def create_authenticated_client():
    def _create_authenticated_client(user):

        client = APIClient()
        client.force_login(user)

        return client
    
    return _create_authenticated_client

