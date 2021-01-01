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
    load_sub_class,
    promote_student,
    promote_student_process,
    send_general_message,
    send_messages,
    show_result,
    show_student_result,
    staff_add_result_save,
    teacher_dashboard,
    view_messages,
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
    path("add_result/", add_result, name="add_result"),
    path("save_result/", staff_add_result_save, name="save_result"),
    path("show_result/", show_result, name="show_result"),
    path("result/", show_student_result, name="show_student_result"),
    path("load_subclass", load_sub_class, name="load_subclass"),
    path("promote/", promote_student, name="promote"),
    path("process", promote_student_process, name="promote_student"),
    path("send_message/", send_messages, name="message"),
    path("send_general_message/", send_general_message, name="general_message"),
    path("view_messages/", view_messages, name="view_message"),
    path("<int:pk>/message_edit/", UpdateMessage.as_view(), name="message_update"),
    path("<int:pk>/message_delete/", DeleteMessage.as_view(), name="message_delete"),
]
