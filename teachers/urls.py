from django.urls import path

from .views import (
    TeacherDashBoard,
    TeacherProfileView,
    TeacherSignupView,
    TeacherUpdateView,
)

app_name = "teachers"

urlpatterns = [
    path("signup/", TeacherSignupView.as_view(), name="signup"),
    path("<int:pk>/edit/", TeacherUpdateView.as_view(), name="update"),
    path("<int:pk>/profile/", TeacherProfileView.as_view(), name="profile"),
    path("dashboard/", TeacherDashBoard.as_view(), name="dash"),
]
