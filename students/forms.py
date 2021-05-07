from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from schoolz.users.models import Student
from teachers.models import Class, SubClass

from .models import StudentMessages, StudentModel

User = get_user_model()


class StudentMessageForm(forms.ModelForm):
    class Meta:
        model = StudentMessages
        exclude = {"teacher", "student", "updated_at", "created_at", "private", "slug"}
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "messages": forms.TextInput(attrs={"class": "form-control"}),
        }


class StudentSignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.request = kwargs.pop("request", None)
        super(StudentSignUpForm, self).__init__(*args, **kwargs)

    name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    photo = forms.ImageField(
        required=True, widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
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
            uuid=user.uuid,
            name=self.cleaned_data.get("name"),
            photo=self.cleaned_data.get("photo"),
            section=self.user.teachermodel.section,
            class_name=self.user.teachermodel.class_name,
            sub_class=self.user.teachermodel.sub_class,
            fathers_name=self.cleaned_data.get("fathers_name"),
            mothers_name=self.cleaned_data.get("mothers_name"),
            date_of_birth=self.cleaned_data.get("date_of_birth"),
            email=self.cleaned_data.get("email"),
            address=self.cleaned_data.get("address"),
            emergency_mobile_number=self.cleaned_data.get("emergency_mobile_number"),
            created_by=self.user,
            updated_by=self.user,
        )
        student.save()
        messages.success(self.request, "Student has been added.")
        return user


class StudentModelForm(forms.ModelForm):
    class Meta:
        model = StudentModel
        exclude = ["user", "created_by", "updated_by", "paid", "email"]
        widgets = {
            "date_of_birth": forms.TextInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.request = kwargs.pop("request", None)
        super(StudentModelForm, self).__init__(*args, **kwargs)
        self.fields["class_name"].queryset = Class.objects.none()
        self.fields["sub_class"].queryset = SubClass.objects.none()

        if "section" in self.data:
            try:
                section_id = int(self.data.get("section"))
                self.fields["class_name"].queryset = Class.objects.filter(
                    section=section_id
                )
            except (TypeError, ValueError):
                pass
        elif self.instance.pk:
            self.fields[
                "class_name"
            ].queryset = self.instance.section.class_name_set.order_by("class_name")

        if "class_name" in self.data:
            try:
                class_name_id = int(self.data.get("class_name"))
                self.fields["sub_class"].queryset = SubClass.objects.filter(
                    class_name=class_name_id
                )
            except (TypeError, ValueError):
                pass
        elif self.instance.pk:
            self.fields[
                "sub_class"
            ].queryset = self.instance.class_name.sub_class_set.order_by("sub_class")


# do the same for teachers
class StudentAdminSignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.request = kwargs.pop("request", None)
        super(StudentAdminSignUpForm, self).__init__(*args, **kwargs)

    class Meta(UserCreationForm.Meta):
        model = Student
        fields = UserCreationForm.Meta.fields + ("email",)

    @transaction.atomic
    def save(self):
        student_model = StudentModelForm(self.request.POST)
        student_model.is_valid()
        if student_model.cleaned_data.get("section") != self.user.adminmodel.section:
            user = super().save(commit=False)
            messages.error(self.request, "This action is not allowed.")
            return user
        else:
            user = super().save(commit=False)
            user.save()
            student = StudentModel.objects.create(
                user=user,
                uuid=user.uuid,
                name=student_model.cleaned_data.get("name"),
                photo=student_model.cleaned_data.get("photo"),
                section=student_model.cleaned_data.get("section"),
                class_name=student_model.cleaned_data.get("class_name"),
                sub_class=student_model.cleaned_data.get("sub_class"),
                fathers_name=student_model.cleaned_data.get("fathers_name"),
                mothers_name=student_model.cleaned_data.get("mothers_name"),
                date_of_birth=student_model.cleaned_data.get("date_of_birth"),
                email=self.cleaned_data.get("email"),
                address=student_model.cleaned_data.get("address"),
                emergency_mobile_number=student_model.cleaned_data.get(
                    "emergency_mobile_number"
                ),
                created_by=self.user,
                updated_by=self.user,
            )
            student.save()
            messages.success(self.request, "Student has been added.")
            return user
