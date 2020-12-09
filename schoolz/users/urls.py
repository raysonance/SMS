from django.urls import path

from .views import (
    AdminSignUpView,
    admin_dashboard,
    user_detail_view,
    user_redirect_view,
    user_update_view,
)

app_name = "users"

urlpatterns = [
    path("dashboard/", admin_dashboard, name="dash"),
    path("signup/", AdminSignUpView.as_view(), name="admin"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
