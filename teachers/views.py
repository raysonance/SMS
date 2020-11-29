from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from schoolz.users.decorators import teacher_required
from schoolz.users.models import User

from .forms import TeacherForm, TeacherSignUpForm
from .models import Teacher

# Create your views here.

# @method_decorator([user_passes_test(test_func=User.is_staff)], name='dispatch')


class TeacherSignupView(LoginRequiredMixin, CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = "teachers/signup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "teachers"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        return redirect("account_logout")


@method_decorator([login_required, teacher_required], name="dispatch")
class TeacherFillForm(CreateView):
    model = Teacher
    template_name = "teachers/teacherinfo.html"
    form_class = TeacherForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        super().form_valid(form)
        return redirect("account_logout")
