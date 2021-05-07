from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    RedirectView,
    UpdateView,
)
from notifications.signals import notify

from students.models import StudentModel
from teachers.models import Class, Section, SubClass, TeacherMessages, TeacherModel

from .decorators import admin_required, superuser_required, user_is_admin
from .forms import AdminSignUpForm, TeacherMessageForm
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


@login_required
@user_passes_test(user_is_admin, login_url="home")
def admin_dashboard(request):
    # get current admin section
    request.session["section_id"] = request.user.adminmodel.section_id
    # assign other section
    if request.session["section_id"] == 1:
        section, not_section = 1, 2
    else:
        section, not_section = 2, 1

    # get other section
    spectre = Section.objects.get(id=not_section)

    section_students = StudentModel.objects.filter(section=section).values("pk", "paid")
    section_teachers = TeacherModel.objects.filter(section=section).count()
    other_students = StudentModel.objects.filter(section=not_section).values(
        "pk", "paid"
    )
    students_count, other_students_count = len(section_students), len(other_students)
    other_teachers = TeacherModel.objects.filter(section=not_section).count()

    # get number of paid students
    paid_section_students = len(
        [student for student in section_students if student["paid"]]
    )
    unpaid = students_count - paid_section_students

    paid_other_students = len(
        [student for student in other_students if student["paid"]]
    )
    unpaid_other = other_students_count - paid_other_students

    context = {
        "student": students_count,
        "teacher": section_teachers,
        "other_students": other_students_count,
        "other_teachers": other_teachers,
        "paid_students": paid_section_students,
        "unpaid": unpaid,
        "paid_other": paid_other_students,
        "unpaid_other": unpaid_other,
        "spectre": spectre.sections,
    }
    return render(request, "users/admin_dashboard.html", context)


@method_decorator([superuser_required], name="dispatch")
class AdminSignUpView(LoginRequiredMixin, CreateView):
    model = Admin
    form_class = AdminSignUpForm
    login_url = "account_login"

    template_name = "users/admin_signup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "admin"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        return redirect("users:dash")


class AdminDetailView(LoginRequiredMixin, DetailView):
    model = AdminModel
    login_url = "account_login"
    context_object_name = "admin"
    template_name = "users/admin_profile.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"


# admin list of student
@login_required
@user_passes_test(user_is_admin, login_url="home")
def show_list(request):
    class_name = Class.objects.filter(section=request.user.adminmodel.section_id)
    sub_class = SubClass.objects.all()
    if request.method == "POST":
        class_id = request.POST.get("class_name")
        sub_class_id = request.POST.get("sub_class")

        class_name = get_object_or_404(Class, pk=class_id)
        sub_class = get_object_or_404(SubClass, pk=sub_class_id)

        student = StudentModel.objects.filter(
            class_name=class_name, sub_class=sub_class
        ).select_related("class_name", "sub_class")

        context = {"student": student}

        return render(request, "student/admin_student.html", context)

    context = {"class_name": class_name, "sub_class": sub_class}

    return render(request, "teachers/admin_student.html", context)


@method_decorator([admin_required], name="dispatch")
class AdminUpdateView(LoginRequiredMixin, UpdateView):
    model = AdminModel
    login_url = "home"
    template_name = "teachers/update.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    fields = ["name", "section", "photo", "date_of_birth", "mobile", "email"]

    def get_success_url(self):
        return reverse_lazy("users:dash")


# for admin to send messages to teachers
@login_required
@user_passes_test(user_is_admin, login_url="home")
def send_messages(request):
    form = TeacherMessageForm()
    teachers = TeacherModel.objects.filter(section=request.user.adminmodel.section)
    if request.method == "POST":
        form = TeacherMessageForm(request.POST)
        teacher_id = request.POST.get("teachers")
        teacher = get_object_or_404(TeacherModel, pk=teacher_id)
        if form.is_valid():
            teacher_message = form.save(commit=False)
            teacher_message.admin = request.user.adminmodel
            teacher_message.teacher = teacher
            teacher_message.private = True
            teacher_message.save()
            notify.send(
                sender=request.user,
                recipient=teacher.user,
                verb="new private message!",
                target=teacher.user,
            )
            messages.success(request, "Message sent successfully")
            return redirect("users:message")

    context = {
        "teachers": teachers,
        "form": form,
    }

    return render(request, "users/teacher_message.html", context)


# general messages
@login_required
@user_passes_test(user_is_admin, login_url="home")
def send_general_message(request):
    form = TeacherMessageForm()
    teachers = TeacherModel.objects.filter(section=request.user.adminmodel.section)
    if request.method == "POST":
        for staff in teachers:
            teacher = get_object_or_404(TeacherModel, pk=staff.pk)
            form = TeacherMessageForm(request.POST)
            if form.is_valid():
                teacher_message = form.save(commit=False)
                teacher_message.admin = request.user.adminmodel
                teacher_message.teacher = teacher
                teacher_message.save()
                notify.send(
                    sender=request.user,
                    recipient=teacher.user,
                    verb="new general message!",
                    target=teacher.user,
                )
            else:
                messages.error(request, "Message failed to send.")
                return redirect("users:general_message")
        if staff == teachers.last():
            messages.success(request, "Message sent to all teachers successfully")
            return redirect("users:general_message")

    context = {
        "form": form,
    }

    return render(request, "teachers/send_general_message.html", context)


# for admin to view messages
@login_required
@user_passes_test(user_is_admin, login_url="home")
def view_messages(request):
    message = TeacherMessages.objects.filter(
        admin=request.user.adminmodel
    ).select_related("admin", "teacher")
    context = {"message": message}

    return render(request, "users/view_message.html", context)


# next is to add a message for students result update


# for teachers to update messages
@method_decorator([admin_required], name="dispatch")
class UpdateMessage(LoginRequiredMixin, UpdateView):
    model = TeacherMessages
    template_name = "teachers/update_message.html"
    slug_field = "slug"
    slug_url_kwarg = "slug_pk"
    login_url = "account_login"
    fields = [
        "title",
        "message",
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_at = timezone.now()
        form.save()
        notify.send(
            sender=self.object.admin.user,
            recipient=self.object.teacher.user,
            verb="updated message!",
            target=self.object.teacher.user,
        )
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Message updated successfully")
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto


@method_decorator([admin_required], name="dispatch")
class DeleteMessage(LoginRequiredMixin, DeleteView):
    model = TeacherMessages
    login_url = "account_login"
    template_name = "teachers/delete_message.html"
    context_object_name = "message"
    slug_field = "slug"
    slug_url_kwarg = "slug_pk"

    def get_success_url(self):
        messages.success(self.request, "Message deleted successfully")
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto


# implement active and non active as a way of deleting
