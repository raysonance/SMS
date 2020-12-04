from django.urls import path

from .views import TeacherDashBoard, TeacherSignupView

app_name = "teachers"

urlpatterns = [
    path("signup/", TeacherSignupView.as_view(), name="signup"),
    path("dashboard/", TeacherDashBoard.as_view(), name="dash"),
]
