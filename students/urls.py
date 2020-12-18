from django.urls import path

from .views import (
    StudentDeleteView,
    StudentListView,
    StudentProfileView,
    StudentSignupView,
    StudentUpdateView,
    show_result,
    show_student_result,
    student_dashboard,
)

app_name = "students"

urlpatterns = [
    path("list/", StudentListView.as_view(), name="list"),
    path("signup/", StudentSignupView.as_view(), name="signup"),
    path("<int:pk>/profile/", StudentProfileView.as_view(), name="profile"),
    path("<int:pk>/edit/", StudentUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", StudentDeleteView.as_view(), name="delete"),
    path("dashboard/", student_dashboard, name="dash"),
    path("show_result/", show_result, name="show_result"),
    path("show_student_result", show_student_result, name="show_student_result"),
]
