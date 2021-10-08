from django.urls import path

from .views import (
    AdminDetailView,
    AdminSignUpView,
    AdminUpdateView,
    DeleteMessage,
    UpdateMessage,
    admin_dashboard,
    create_codes,
    load_students,
    send_admin_message,
    send_general_message,
    send_messages,
    show_list,
    user_detail_view,
    user_redirect_view,
    user_update_view,
    view_codes,
    view_messages,
)

app_name = "users"

urlpatterns = [
    path("parent/", send_admin_message, name="parent"),
    path("view_codes/", view_codes, name="view_codes"),
    path("create_codes/", create_codes, name="code"),
    path("load_students/", load_students, name="load"),
    path(
        "<slug:slug_pk>/message_edit/", UpdateMessage.as_view(), name="message_update"
    ),
    path(
        "<slug:slug_pk>/message_delete/", DeleteMessage.as_view(), name="message_delete"
    ),
    path("view_messages/", view_messages, name="view_message"),
    path("send_message/", send_messages, name="message"),
    path("send_general_message/", send_general_message, name="general_message"),
    path("show_list/", show_list, name="show_list"),
    path("dashboard/", admin_dashboard, name="dash"),
    path("<slug:uuid_pk>/profile/", AdminDetailView.as_view(), name="admin_detail"),
    path("<slug:uuid_pk>/update/", AdminUpdateView.as_view(), name="admin_update"),
    path("signup/", AdminSignUpView.as_view(), name="admin"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
