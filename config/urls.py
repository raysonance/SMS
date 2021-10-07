import notifications.urls
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token

from students.views import (
    college_classroom_post_comment,
    college_classroom_post_reply,
    college_student,
    college_student_articles,
    college_student_assignments,
    college_student_classroom_give_test,
    college_student_classroom_view_post,
    college_student_reading_materials,
    college_student_submit_assignment,
    college_student_videos,
    college_teacher_student_account,
    delete_comment_or_reply,
)
from teachers.views import (
    college_teacher_classroom,
    college_teacher_classroom_add_post,
    college_teacher_classroom_delete_test,
    college_teacher_classroom_view_test,
    view_assignments_submissions,
    view_test_performance,
    view_tests_submissions,
)

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="home/home.html", extra_context={"section": "home"}
        ),
        name="home",
    ),
    path(
        "profile/",
        TemplateView.as_view(template_name="home/profile.html"),
        name="profile",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("schoolz.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("teachers/", include("teachers.urls")),
    path("students/", include("students.urls")),
    url(
        "^inbox/notifications/", include(notifications.urls, namespace="notifications")
    ),
    path(
        "college/teacher/classroom/",
        college_teacher_classroom,
        name="college_teacher_classroom",
    ),
    path(
        "college/teacher/classroom/<int:pk>/add_post",
        college_teacher_classroom_add_post,
        name="college_teacher_classroom_add_post",
    ),
    path(
        "college/teacher/classroom/view_test/<int:pk>",
        college_teacher_classroom_view_test,
        name="college_teacher_classroom_view_test",
    ),
    path(
        "college/teacher/classroom/delete_test/<int:pk>",
        college_teacher_classroom_delete_test,
        name="college_teacher_classroom_delete_test",
    ),
    path(
        "college/teacher/classroom/view_tests_submissions/<int:class_pk>",
        view_tests_submissions,
        name="view_tests_submissions",
    ),
    path(
        "college/teacher/classroom/view_assignments_submissions/<int:class_pk>",
        view_assignments_submissions,
        name="view_assignments_submissions",
    ),
    path(
        "college/teacher/classroom/view_test_performance/<int:pk>",
        view_test_performance,
        name="view_test_performance",
    ),
    path("college/student", college_student, name="college_student"),
    path(
        "college/student/classroom/college_student_assignments",
        college_student_assignments,
        name="college_student_assignments",
    ),
    path(
        "college/student/classroom/college_student_submit_assignment/<int:pk>",
        college_student_submit_assignment,
        name="college_student_submit_assignment",
    ),
    path(
        "college/student/classroom/college_student_reading_materials",
        college_student_reading_materials,
        name="college_student_reading_materials",
    ),
    path(
        "college/student/classroom/college_student_videos",
        college_student_videos,
        name="college_student_videos",
    ),
    path(
        "college/student/classroom/college_student_articles",
        college_student_articles,
        name="college_student_articles",
    ),
    path(
        "college/student/classroom/give_test/<int:pk>",
        college_student_classroom_give_test,
        name="college_student_classroom_give_test",
    ),
    path(
        "college/classroom/view_post/<int:pk>",
        college_student_classroom_view_post,
        name="college_student_classroom_view_post",
    ),
    path(
        "college/classroom/comment",
        college_classroom_post_comment,
        name="college_classroom_post_comment",
    ),
    path(
        "college/classroom/reply",
        college_classroom_post_reply,
        name="college_classroom_post_reply",
    ),
    path(
        "college/classroom/delete_comment_or_reply/<int:pk>",
        delete_comment_or_reply,
        name="delete_comment_or_reply",
    ),
    path(
        "college/student/college_teacher_student_account",
        college_teacher_student_account,
        name="college_teacher_student_account",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
