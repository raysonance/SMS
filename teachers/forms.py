from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from schoolz.users.models import Teacher

from .models import Class, TeacherModel

User = get_user_model()


class TeacherSignUpForm(UserCreationForm):
    name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    photo = forms.ImageField(
        required=True, widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
    date_of_birth = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"type": "date"})
    )
    class_name = forms.ModelChoiceField(queryset=Class.objects.all(), required=True)
    mobile = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    joining_date = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"type": "date"})
    )

    class Meta(UserCreationForm.Meta):
        model = Teacher
        fields = UserCreationForm.Meta.fields + ("email",)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.save()
        teacher = TeacherModel.objects.create(
            user=user,
            name=self.cleaned_data.get("name"),
            photo=self.cleaned_data.get("photo"),
            date_of_birth=self.cleaned_data.get("date_of_birth"),
            class_name=self.cleaned_data.get("class_name"),
            mobile=self.cleaned_data.get("mobile"),
            email=self.cleaned_data.get("email"),
            joining_date=self.cleaned_data.get("joining_date"),
        )
        teacher.save()
        return user
