from django.urls import path

from .views import (
    StudentAdminSignupView,
    StudentDeleteView,
    StudentProfileView,
    StudentSignupView,
    StudentTeacherUpdateView,
    StudentUpdateView,
    load_sub_class,
    search_student,
    show_result,
    student_dashboard,
    student_list,
    student_teacher_list,
    view_general_messages,
    view_messages,
)

app_name = "students"

urlpatterns = [
    path("signup/", StudentSignupView.as_view(), name="signup"),
    path("student_signup/", StudentAdminSignupView.as_view(), name="student_signup"),
    path("<slug:uuid_pk>/profile/", StudentProfileView.as_view(), name="profile"),
    path("<slug:uuid_pk>/edit/", StudentUpdateView.as_view(), name="update"),
    path("<slug:uuid_pk>/update/", StudentTeacherUpdateView.as_view(), name="updates"),
    path("<slug:uuid_pk>/delete/", StudentDeleteView.as_view(), name="delete"),
    path("dashboard/", student_dashboard, name="dash"),
    path("student_list/", student_teacher_list, name="student_teacher_list"),
    path("students_list/", student_list, name="student_list"),
    path("show_result/", show_result, name="show_result"),
    path("load_subclass/", load_sub_class, name="load_subclass"),
    path("view_message/", view_messages, name="message"),
    path("general_message/", view_general_messages, name="general_message"),
    path("searches/", search_student, name="search_student"),
]
