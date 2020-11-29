from django.urls import path

from .views import TeacherFillForm, TeacherSignupView

app_name = "teachers"

urlpatterns = [
    path("signup/", TeacherSignupView.as_view(), name="signup"),
    path("fill/", TeacherFillForm.as_view(), name="form"),
]
