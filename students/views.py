from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from schoolz.users.decorators import multiple_required, teacher_required
from schoolz.users.models import Student, StudentModel

from .forms import StudentSignUpForm


@method_decorator([teacher_required], name="dispatch")
class StudentSignupView(LoginRequiredMixin, CreateView):
    model = Student
    login_url = "account_login"
    form_class = StudentSignUpForm
    template_name = "student/signup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "students"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        return redirect("teachers:dash")


class StudentProfileView(LoginRequiredMixin, DetailView):
    model = Student
    login_url = "account_login"
    context_object_name = "student"
    template_name = "student/studentprofile.html"


@method_decorator([multiple_required], name="dispatch")
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
        return reverse_lazy("teachers:dash")


@method_decorator([multiple_required], name="dispatch")
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    login_url = "account_login"
    template_name = "student/list.html"
    context_object_name = "student"


class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Student
    template_name = "student/student_delete.html"
    success_url = reverse_lazy("students:list")
    login_url = "account_login"
    context_object_name = "students"

    def test_func(self):
        obj = self.get_object()
        return obj.studentmodel.class_name == self.request.user.teachermodel.class_name


@method_decorator([login_required, teacher_required], name="dispatch")
class StudentDashBoard(ListView):
    model = Student
    template_name = "teachers/student.html"
