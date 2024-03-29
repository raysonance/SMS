from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from schoolz.users.forms import UserChangeForm, UserCreationForm

from .models import Admin, AdminMessages, AdminModel, College, Plan, Student, Teacher

User = get_user_model()


@admin.register(User)
@admin.register(Teacher)
@admin.register(Student)
@admin.register(Admin)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name",)}),) + tuple(
        auth_admin.UserAdmin.fieldsets
    )
    list_display = [
        "username",
        "name",
        "is_staff",
        "is_superuser",
        "is_teacher",
        "is_admin",
        "is_student",
    ]
    search_fields = ["name"]


admin.site.register(AdminModel)
admin.site.register(AdminMessages)
admin.site.register(Plan)
admin.site.register(College)
