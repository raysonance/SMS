from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def teacher_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="home"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_teacher,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def teacher_admin(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="home"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_teacher or u.is_superuser or u.is_admin),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def teacher_admin_student(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="home"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active
        and (u.is_teacher or u.is_superuser or u.is_admin or u.is_student),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def teacher_student(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="home"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_teacher or u.is_student or u.is_superuser),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="home"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_admin or u.is_superuser),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
