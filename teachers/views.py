from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView

from schoolz.users.decorators import admin_required
from schoolz.users.models import Teacher, Teachers

from .forms import TeacherSignUpForm

# Create your views here.


@method_decorator([login_required, admin_required], name="dispatch")
class TeacherSignupView(LoginRequiredMixin, CreateView):
    model = Teachers
    form_class = TeacherSignUpForm
    template_name = "teachers/signup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "teachers"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        return redirect("home")


class TeacherDashBoard(ListView):
    model = Teacher
    template_name = "teachers/teacher.html"
