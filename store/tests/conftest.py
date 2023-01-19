#fixtures are reuseable components are defined here are automatically load by pytest without having to explicitly load them.
#used to remove duplication
from django.contrib.auth.models import User
from rest_framework.test import APIClient
import pytest

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        #intialize and by default is_staff is false
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate
