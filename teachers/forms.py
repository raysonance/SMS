from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from schoolz.users.models import Teacher

from .models import Class, Section, SubClass, TeacherModel

User = get_user_model()


class TeacherSignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.request = kwargs.pop("request", None)
        super(TeacherSignUpForm, self).__init__(*args, **kwargs)

    name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    photo = forms.ImageField(
        required=True, widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
    date_of_birth = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"type": "date"})
    )
    section = forms.ModelChoiceField(queryset=Section.objects.all(), required=True)

    class_name = forms.ModelChoiceField(queryset=Class.objects.all(), required=True)

    sub_class = forms.ModelChoiceField(queryset=SubClass.objects.all(), required=True)

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

    address = forms.CharField(
        max_length=500, widget=forms.Textarea(attrs={"class": "form-control"})
    )

    joining_date = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"type": "date"})
    )

    class Meta(UserCreationForm.Meta):
        model = Teacher
        fields = UserCreationForm.Meta.fields + ("email",)

    @transaction.atomic
    def save(self):
        print(type(self.cleaned_data.get("section")))
        if (
            self.cleaned_data.get("section") != self.user.adminmodel.section
            or self.cleaned_data.get("class_name").section
            != self.user.adminmodel.section
            or self.cleaned_data.get("sub_class").class_name
            != self.cleaned_data.get("class_name")
        ):
            user = super().save(commit=False)
            messages.error(self.request, "This action is not allowed.")
            return user
        else:
            user = super().save(commit=False)
            user.save()
            teacher = TeacherModel.objects.create(
                user=user,
                uuid=user.uuid,
                name=self.cleaned_data.get("name"),
                photo=self.cleaned_data.get("photo"),
                date_of_birth=self.cleaned_data.get("date_of_birth"),
                section=self.cleaned_data.get("section"),
                class_name=self.cleaned_data.get("class_name"),
                sub_class=self.cleaned_data.get("sub_class"),
                address=self.cleaned_data.get("address"),
                mobile=self.cleaned_data.get("mobile"),
                email=self.cleaned_data.get("email"),
                joining_date=self.cleaned_data.get("joining_date"),
            )
            teacher.save()
            messages.success(self.request, "Teacher has been added.")
            return user
