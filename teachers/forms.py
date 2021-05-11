from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from schoolz.users.models import Teacher

from .models import Class, SubClass, TeacherModel

User = get_user_model()


class TeacherModelForm(forms.ModelForm):
    class Meta:
        model = TeacherModel
        exclude = ["user", "created_by", "updated_by", "email"]
        widgets = {
            "date_of_birth": forms.TextInput(attrs={"type": "date"}),
            "joining_date": forms.TextInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.request = kwargs.pop("request", None)
        super(TeacherModelForm, self).__init__(*args, **kwargs)
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


class TeacherSignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.request = kwargs.pop("request", None)
        super(TeacherSignUpForm, self).__init__(*args, **kwargs)

    class Meta(UserCreationForm.Meta):
        model = Teacher
        fields = UserCreationForm.Meta.fields + ("email",)
        exclude = ["username"]

    @transaction.atomic
    def save(self):
        teacher_model = TeacherModelForm(self.request.POST, self.request.FILES)
        if teacher_model.is_valid():
            if (
                teacher_model.cleaned_data.get("section")
                != self.user.adminmodel.section
            ):
                user = super().save(commit=False)
                messages.error(self.request, "This action is not allowed.")
                return user
            else:
                user = super().save(commit=False)
                user.name = teacher_model.cleaned_data.get("name")
                user.save()
                teacher = TeacherModel.objects.create(
                    user=user,
                    uuid=user.uuid,
                    name=teacher_model.cleaned_data.get("name"),
                    photo=teacher_model.cleaned_data.get("photo"),
                    date_of_birth=teacher_model.cleaned_data.get("date_of_birth"),
                    section=teacher_model.cleaned_data.get("section"),
                    class_name=teacher_model.cleaned_data.get("class_name"),
                    sub_class=teacher_model.cleaned_data.get("sub_class"),
                    address=teacher_model.cleaned_data.get("address"),
                    mobile=teacher_model.cleaned_data.get("mobile"),
                    email=self.cleaned_data.get("email"),
                    joining_date=teacher_model.cleaned_data.get("joining_date"),
                )
                teacher.save()
                messages.success(self.request, "Teacher has been added.")
                return user
        else:
            user = super().save(commit=False)
            messages.success(self.request, "Form is invalid.")
            return user


class TeacherUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(TeacherUpdateForm, self).__init__(*args, **kwargs)
        self.fields["class_name"].queryset = Class.objects.filter(
            section=self.user.section
        )
        self.fields["sub_class"].queryset = SubClass.objects.filter(
            class_name__section=self.user.section
        )

    class Meta:
        model = TeacherModel
        fields = [
            "section",
            "class_name",
            "sub_class",
        ]
