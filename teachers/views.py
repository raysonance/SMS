from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from schoolz.users.decorators import admin_required, teacher_required
from schoolz.users.models import Teacher, TeacherModel

from .forms import TeacherSignUpForm

# Create your views here.


@method_decorator([admin_required], name="dispatch")
class TeacherSignupView(LoginRequiredMixin, CreateView):
    model = Teacher
    login_url = "account_login"
    form_class = TeacherSignUpForm
    template_name = "teachers/signup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "teachers"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        return redirect("teachers:dash")


class TeacherProfileView(LoginRequiredMixin, DetailView):
    model = Teacher
    login_url = "account_login"
    context_object_name = "teacher"
    template_name = "teachers/teacherprofile.html"


@method_decorator([teacher_required], name="dispatch")
class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = TeacherModel
    login_url = "account_login"
    template_name = "teachers/update.html"
    fields = [
        "name",
        "photo",
        "date_of_birth",
        "class_name",
        "mobile",
        "email",
        "joining_date",
    ]

    def get_success_url(self):
        return reverse_lazy("teachers:dash")


@method_decorator([login_required, teacher_required], name="dispatch")
class TeacherDashBoard(ListView):
    model = Teacher
    template_name = "teachers/teacher.html"
