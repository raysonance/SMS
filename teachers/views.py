from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
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

# Create your views here.
from schoolz.users.decorators import admin_required, teacher_required
from schoolz.users.models import Teacher
from students.models import StudentModel

from .forms import TeacherSignUpForm
from .models import TeacherModel


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


@method_decorator([admin_required], name="dispatch")
class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    login_url = "account_login"
    template_name = "teachers/list.html"
    context_object_name = "teacher"


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


class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_delete.html"
    success_url = reverse_lazy("teachers:list")
    login_url = "account_login"
    context_object_name = "teachers"


def user_is_teacher(user):
    if user.is_teacher:
        return True


@user_passes_test(user_is_teacher, login_url="account_login")
def teacher_dashboard(request):
    total_student = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name.pk
    ).count()
    context = {
        "student": total_student,
    }
    return render(request, "teachers/teacher.html", context)
