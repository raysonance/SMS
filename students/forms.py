from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from schoolz.users.models import Student, StudentModel
from teachers.models import Class

User = get_user_model()


class StudentSignUpForm(UserCreationForm):
    name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    photo = forms.ImageField(
        required=True, widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
    class_name = forms.ModelChoiceField(queryset=Class.objects.all(), required=True)
    fathers_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    mothers_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    date_of_birth = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"type": "date"})
    )
    email = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    address = forms.CharField(
        max_length=500, widget=forms.Textarea(attrs={"class": "form-control"})
    )

    emergency_mobile_number = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta(UserCreationForm.Meta):
        model = Student
        fields = UserCreationForm.Meta.fields + ("email",)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.save()
        student = StudentModel.objects.create(
            user=user,
            name=self.cleaned_data.get("name"),
            photo=self.cleaned_data.get("photo"),
            class_name=self.cleaned_data.get("class_name"),
            fathers_name=self.cleaned_data.get("fathers_name"),
            mothers_name=self.cleaned_data.get("mothers_name"),
            date_of_birth=self.cleaned_data.get("date_of_birth"),
            email=self.cleaned_data.get("email"),
            address=self.cleaned_data.get("address"),
            emergency_mobile_number=self.cleaned_data.get("emergency_mobile_number"),
        )
        student.save()
        return user