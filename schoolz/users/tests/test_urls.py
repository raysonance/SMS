import pytest
from django.test import TestCase
from django.urls import resolve, reverse

from schoolz.users.models import User

pytestmark = pytest.mark.django_db


class Testing(TestCase):
    # remove this view
    def test_detail(self):
        assert (
            reverse("users:detail", kwargs={"username": User.username})
            == f"/users/{User.username}/"
        )
        assert resolve(f"/users/{User.username}/").view_name == "users:detail"

    def test_update(self):
        assert reverse("users:update") == "/users/~update/"
        assert resolve("/users/~update/").view_name == "users:update"

    def test_redirect(self):
        assert reverse("users:redirect") == "/users/~redirect/"
        assert resolve("/users/~redirect/").view_name == "users:redirect"

    def test_signup(self):
        assert reverse("users:admin") == "/users/signup/"
        assert resolve("/users/signup/").view_name == "users:admin"

    def test_update_admin(self):
        assert reverse("users:admin_update") == "<slug:uuid_pk>/update/"
        assert resolve("<slug:uuid_pk>/update/").view_name == "users:admin_update"
