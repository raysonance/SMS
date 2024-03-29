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

from students.models import Code, StudentModel
from teachers.models import Class, Section, SubClass, TeacherMessages, TeacherModel

from .decorators import admin_required, superuser_required, user_is_admin
from .forms import AdminSignUpForm, TeacherMessageForm
from .models import Admin, AdminMessages, AdminModel

User = get_user_model()


# todo: make head teacher comment field


def load_students(request):
    if request.method == "GET":
        # get class and subclass id
        class_id = request.GET.get("class_name")
        sub_class_id = request.GET.get("sub_class")
        if class_id and sub_class_id:
            # get class and subclass
            class_name = get_object_or_404(Class, pk=class_id)
            sub_class = get_object_or_404(SubClass, pk=sub_class_id)
            # get students
            student = StudentModel.objects.filter(
                class_name=class_name, sub_class=sub_class
            ).select_related("class_name", "sub_class")
        else:
            student = {}
        context = {"student": student}
        return render(request, "others/student_list.html", context)


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
    section_id = request.user.adminmodel.section_id
    # assign other section
    if section_id == 1:
        sections, not_sections = 1, 2
    else:
        sections, not_sections = 2, 1

    # get other section
    not_section = Section.objects.get(id=not_sections)
    section = Section.objects.get(id=sections)

    students_count = StudentModel.objects.filter(section=sections).count()
    section_teachers = TeacherModel.objects.filter(section=sections).count()
    other_students_count = StudentModel.objects.filter(section=not_sections).count()
    other_teachers = TeacherModel.objects.filter(section=not_sections).count()
    # get number of paid students
    paid_section_students = StudentModel.objects.filter(
        section=sections, paid=True
    ).count()
    unpaid = students_count - paid_section_students

    paid_other_students = StudentModel.objects.filter(
        section=not_sections, paid=True
    ).count()
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
        "spectre": not_section.sections,
        "section": section.sections,
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
    model = Admin
    login_url = "account_login"
    context_object_name = "admin"
    template_name = "users/admin_profile.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    def get_queryset(self):
        # a very useful feature that reduces number of queries from 22 to 6
        admin = Admin.objects.all().select_related(
            "adminmodel__section",
        )
        return admin


# admin list of student
@login_required
@user_passes_test(user_is_admin, login_url="home")
def show_list(request):
    class_name = Class.objects.filter(section=request.user.adminmodel.section_id)
    sub_class = SubClass.objects.filter(
        class_name__section=request.user.adminmodel.section_id
    ).select_related("class_name")

    context = {"class_name": class_name, "sub_class": sub_class}

    return render(request, "student/admin_student.html", context)


@method_decorator([admin_required], name="dispatch")
class AdminUpdateView(LoginRequiredMixin, UpdateView):
    model = AdminModel
    login_url = "home"
    template_name = "teachers/update.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    fields = ["name", "photo", "date_of_birth", "mobile", "email"]

    def get_success_url(self):
        messages.success(self.request, "Updated!")
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

    return render(request, "teachers/send_message.html", context)


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


def delete_codes(request):
    codes = Code.objects.filter(section=request.user.adminmodel.section_id)
    try:
        codes.delete()
    except Exception as err:
        messages.error(request, f"Cannot delete codes contact the web developer. {err}")


@login_required
@user_passes_test(user_is_admin, login_url="home")
def create_codes(request):
    student_number = (
        StudentModel.objects.filter(section=request.user.adminmodel.section_id).count()
        + 10
    )
    delete_codes(request)
    section = Section.objects.get(pk=request.user.adminmodel.section_id)
    try:
        for i in range(student_number):
            Code.objects.create(number=i, section=section)
        messages.success(request, "Codes have been generated successfully.")
        return view_codes(request)
    except Exception as err:
        messages.error(
            request, f"Cannot generate codes contact the web developer. {err}"
        )
        return view_codes(request)


@login_required
@user_passes_test(user_is_admin, login_url="home")
def view_codes(request):
    codes = Code.objects.filter(section=request.user.adminmodel.section_id)
    return render(request, "users/codes.html", {"codes": codes})


# general messages
def send_admin_message(request):
    admins = AdminModel.objects.all()
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        user_email = request.POST.get("user_email")
        subject = request.POST.get("subject")
        message = request.POST.get("msg")
        for admin in admins:
            Admin = get_object_or_404(AdminModel, pk=admin.pk)
            try:
                admin_message = AdminMessages(
                    admin=Admin,
                    sender_name=user_name,
                    sender_email=user_email,
                    title=subject,
                    message=message,
                )
                admin_message.save()
                notify.send(
                    sender=Admin.user,
                    recipient=Admin.user,
                    verb="new message!",
                    target=Admin.user,
                )
            except Exception as err:
                messages.error(request, f"{err}")
                return render(request, "others/message.html")
        messages.success(request, "Sent!")
        return render(request, "others/message.html")
    else:
        return render(request, "403.html")
