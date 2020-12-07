from django.urls import path

from .views import (
    StudentDashBoard,
    StudentDeleteView,
    StudentListView,
    StudentProfileView,
    StudentSignupView,
    StudentUpdateView,
)

app_name = "students"

urlpatterns = [
    path("list/", StudentListView.as_view(), name="list"),
    path("signup/", StudentSignupView.as_view(), name="signup"),
    path("<int:pk>/profile/", StudentProfileView.as_view(), name="profile"),
    path("<int:pk>/edit/", StudentUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", StudentDeleteView.as_view(), name="delete"),
    path("dashboard/", StudentDashBoard.as_view(), name="dash"),
]
