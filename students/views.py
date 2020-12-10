from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from schoolz.users.decorators import teacher_admin, teacher_admin_student
from schoolz.users.models import Student, Teacher

from .forms import StudentSignUpForm
from .models import StudentModel


@method_decorator([teacher_admin], name="dispatch")
class StudentSignupView(LoginRequiredMixin, CreateView):
    model = Student
    login_url = "account_login"
    form_class = StudentSignUpForm
    template_name = "student/signup.html"

    def get_form_kwargs(self):
        kwargs = super(StudentSignupView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "students"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        super().form_valid(form)
        if self.request.user.is_teacher:
            return redirect("teachers:dash")
        if self.request.user.is_admin:
            return redirect("users:dash")


class StudentProfileView(LoginRequiredMixin, DetailView):
    model = Student
    login_url = "account_login"
    context_object_name = "student"
    template_name = "student/studentprofile.html"


@method_decorator([teacher_admin_student], name="dispatch")
class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = StudentModel
    login_url = "account_login"
    template_name = "student/update.html"
    fields = [
        "name",
        "photo",
        "class_name",
        "fathers_name",
        "mothers_name",
        "date_of_birth",
        "email",
        "address",
        "emergency_mobile_number",
    ]

    def get_success_url(self):
        if self.request.user.is_teacher:
            return reverse_lazy("teachers:dash")
        if self.request.user.is_admin:
            return reverse_lazy("users:dash")


@method_decorator([teacher_admin_student], name="dispatch")
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    login_url = "account_login"
    template_name = "student/list.html"
    context_object_name = "student"


@method_decorator([teacher_admin], name="dispatch")
class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Student
    template_name = "student/student_delete.html"
    success_url = reverse_lazy("students:list")
    login_url = "account_login"
    context_object_name = "students"

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_teacher:
            return (
                obj.studentmodel.class_name == self.request.user.teachermodel.class_name
            )
        elif self.request.user.is_admin:
            return True


def user_is_student(user):
    return user.is_student


@user_passes_test(user_is_student, login_url="home")
def student_dashboard(request):
    total_student = StudentModel.objects.filter(
        class_name=request.user.studentmodel.class_name.pk
    ).count()
    teacher = Teacher.objects.all()
    context = {
        "teacher": teacher,
        "student": total_student,
    }
    return render(request, "student/student_dashboard.html", context)
