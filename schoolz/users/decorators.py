from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def superuser_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="home"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


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


def admin_student(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="home"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_student or u.is_admin or u.is_superuser),
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


# test for functions


def user_is_superuser(user):
    return user.is_superuser


def user_is_teacher(user):
    return user.is_teacher


def user_is_admin(user):
    return user.is_admin


def user_is_student(user):
    return user.is_student


def student_admin(user):
    return user.is_student or user.is_admin


def teacher_admin_func(user):
    return user.is_teacher or user.is_admin
