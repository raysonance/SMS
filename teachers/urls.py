from django.urls import path

from .views import (
    AdminTeacherUpdateView,
    DeleteMessage,
    TeacherDeleteView,
    TeacherListView,
    TeacherProfileView,
    TeacherSignupView,
    TeacherUpdateView,
    UpdateMessage,
    add_result,
    load_class,
    load_sub_class,
    promote_student,
    promote_student_process,
    send_general_message,
    send_messages,
    show_result,
    teacher_dashboard,
    view_admin_messages,
    view_general_messages,
    view_messages,
)

app_name = "teachers"

urlpatterns = [
    path("list/", TeacherListView.as_view(), name="list"),
    path("signup/", TeacherSignupView.as_view(), name="signup"),
    path("<slug:uuid_pk>/edit/", TeacherUpdateView.as_view(), name="update"),
    path(
        "<slug:uuid_pk>/admin_edit/",
        AdminTeacherUpdateView.as_view(),
        name="admin_update",
    ),
    path("<slug:uuid_pk>/profile/", TeacherProfileView.as_view(), name="profile"),
    path("<slug:uuid_pk>/delete/", TeacherDeleteView.as_view(), name="delete"),
    path("dashboard/", teacher_dashboard, name="dash"),
    path("add_result/", add_result, name="add_result"),
    path("show_result/", show_result, name="show_result"),
    path("load_subclass", load_sub_class, name="load_subclass"),
    path("load_class", load_class, name="load_class"),
    path("promote/", promote_student, name="promote"),
    path("process/", promote_student_process, name="promote_student"),
    path("send_message/", send_messages, name="message"),
    path("send_general_message/", send_general_message, name="general_message"),
    path("view_messages/", view_messages, name="view_message"),
    path("view_admin_messages/", view_admin_messages, name="view_admin_message"),
    path("view_general_messages/", view_general_messages, name="view_general_message"),
    path(
        "<slug:slug_pk>/message_edit/", UpdateMessage.as_view(), name="message_update"
    ),
    path(
        "<slug:slug_pk>/message_delete/", DeleteMessage.as_view(), name="message_delete"
    ),
]
