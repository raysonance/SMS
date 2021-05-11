from django import forms as form
from django.contrib.auth import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from teachers.models import Section, TeacherMessages

from .models import Admin, AdminModel

User = get_user_model()


class TeacherMessageForm(form.ModelForm):
    class Meta:
        model = TeacherMessages
        exclude = {"admin", "teacher", "updated_at", "created_at", "private", "slug"}
        widgets = {
            "title": form.TextInput(attrs={"class": "form-control"}),
            "messages": form.TextInput(attrs={"class": "form-control"}),
        }


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(admin_forms.UserCreationForm):
    error_message = admin_forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


# class AdminSignUpForm(forms.UserCreationForm):
#    error_message = forms.UserCreationForm.error_messages.update(
#        {"duplicate_username": _("This username has already been taken.")}
#    )
#
#    class Meta(forms.UserCreationForm.Meta):
#        model = Admin
#        fields = forms.UserCreationForm.Meta.fields + ("email",)
#
#    def clean_username(self):
#        username = self.cleaned_data["username"]
#
#        try:
#            User.objects.get(username=username)
#        except User.DoesNotExist:
#            return username
#
#        raise ValidationError(self.error_messages["duplicate_username"])


class AdminSignUpForm(UserCreationForm):
    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )
    name = form.CharField(
        max_length=150, widget=form.TextInput(attrs={"class": "form-control"})
    )
    photo = form.ImageField(
        required=True, widget=form.ClearableFileInput(attrs={"class": "form-control"})
    )
    date_of_birth = form.DateField(
        required=True, widget=form.TextInput(attrs={"type": "date"})
    )
    section = form.ModelChoiceField(queryset=Section.objects.all(), required=True)

    mobile = form.CharField(
        max_length=11,
        required=True,
        widget=form.TextInput(attrs={"class": "form-control"}),
    )

    address = form.CharField(
        max_length=500, widget=form.Textarea(attrs={"class": "form-control"})
    )

    email = form.CharField(
        max_length=255,
        required=True,
        widget=form.TextInput(attrs={"class": "form-control"}),
    )
    joining_date = form.DateField(
        required=True, widget=form.TextInput(attrs={"type": "date"})
    )

    class Meta(UserCreationForm.Meta):
        model = Admin
        fields = UserCreationForm.Meta.fields + ("email",)
        exclude = ["username"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.name = self.cleaned_data.get("name")
        user.save()
        admin = AdminModel.objects.create(
            user=user,
            uuid=user.uuid,
            name=self.cleaned_data.get("name"),
            photo=self.cleaned_data.get("photo"),
            date_of_birth=self.cleaned_data.get("date_of_birth"),
            section=self.cleaned_data.get("section"),
            mobile=self.cleaned_data.get("mobile"),
            email=self.cleaned_data.get("email"),
            address=self.cleaned_data.get("address"),
            joining_date=self.cleaned_data.get("joining_date"),
        )
        admin.save()
        return user
