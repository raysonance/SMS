from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, RedirectView, UpdateView

from students.models import StudentModel
from teachers.models import TeacherModel

from .decorators import superuser_required, user_is_admin
from .forms import AdminSignUpForm
from .models import Admin, AdminModel

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        if self.request.user.is_teacher:
            return reverse("teachers:dash")
        elif self.request.user.is_student:
            return reverse("students:dash")
        elif self.request.user.is_admin:
            return reverse("users:dash")
        else:
            return reverse("home")


user_redirect_view = UserRedirectView.as_view()


@user_passes_test(user_is_admin, login_url="home")
def admin_dashboard(request):
    total_student = StudentModel.objects.filter(
        section=request.user.adminmodel.section
    ).count()
    teacher = TeacherModel.objects.filter(
        section=request.user.adminmodel.section
    ).count()
    context = {"student": total_student, "teacher": teacher}
    return render(request, "users/admin_dashboard.html", context)


@method_decorator([superuser_required], name="dispatch")
class AdminSignUpView(CreateView):
    model = Admin
    form_class = AdminSignUpForm
    template_name = "users/admin_signup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "admin"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        return redirect("users:dash")


class AdminDetailView(LoginRequiredMixin, DetailView):
    model = AdminModel
    login_url = "home"
    context_object_name = "admin"
    template_name = "users/admin_profile.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"
