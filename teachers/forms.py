from django import forms
from django.contrib.auth.forms import UserCreationForm

from schoolz.users.models import User

from .models import Teacher


class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

    def save(self, commit=True):
        user = super().save()
        user.is_teach = True
        if commit:
            user.save()
        return user


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "name",
            "photo",
            "date_of_birth",
            "class_name",
            "mobile",
            "email",
            "joining_date",
        ]
        widgets = {
            "date_of_birth": forms.TextInput({"type": "date"}),
            "joining_date": forms.TextInput({"type": "date"}),
        }
