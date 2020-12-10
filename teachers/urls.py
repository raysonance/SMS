from django.urls import path

from .views import (
    AdminTeacherUpdateView,
    TeacherDeleteView,
    TeacherListView,
    TeacherProfileView,
    TeacherSignupView,
    TeacherUpdateView,
    teacher_dashboard,
)

app_name = "teachers"

urlpatterns = [
    path("list/", TeacherListView.as_view(), name="list"),
    path("signup/", TeacherSignupView.as_view(), name="signup"),
    path("<int:pk>/edit/", TeacherUpdateView.as_view(), name="update"),
    path("<int:pk>/admin_edit/", AdminTeacherUpdateView.as_view(), name="admin_update"),
    path("<int:pk>/profile/", TeacherProfileView.as_view(), name="profile"),
    path("<int:pk>/delete/", TeacherDeleteView.as_view(), name="delete"),
    path("dashboard/", teacher_dashboard, name="dash"),
]
