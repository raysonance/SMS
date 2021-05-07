from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from schoolz.users.decorators import (
    admin_required,
    teacher_admin_student,
    teacher_required,
    user_is_student,
)
from schoolz.users.models import Student
from teachers.models import Class, Session, SubClass, TeacherModel
from teachers.views import user_is_teacher

from .forms import StudentAdminSignUpForm, StudentModelForm, StudentSignUpForm
from .models import StudentMessages, StudentModel, Subject, SubjectResult


# for loading sub_class according to equivalent Class using jquery
def load_sub_class(request):
    class_id = request.GET.get("class")
    sub_class = SubClass.objects.filter(class_name=class_id).order_by("sub_class")

    context = {"sub_class": sub_class}
    return render(request, "others/subclass_dropdown_list_options.html", context)


# fast
# signup of students for teachers
@method_decorator([teacher_required], name="dispatch")
class StudentSignupView(LoginRequiredMixin, CreateView):
    model = Student
    login_url = "account_login"
    form_class = StudentSignUpForm
    template_name = "student/signup.html"

    def get_form_kwargs(self):
        kwargs = super(StudentSignupView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        kwargs.update({"request": self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "students"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.POST.get("more") == "on":
            return redirect("students:signup")
        else:
            return redirect("teachers:dash")


# slow
# signup of students for admin
@method_decorator([admin_required], name="dispatch")
class StudentAdminSignupView(LoginRequiredMixin, CreateView):
    model = Student
    login_url = "account_login"
    form_class = StudentAdminSignUpForm
    form2 = StudentModelForm
    template_name = "student/signup.html"

    def get_form_kwargs(self):
        kwargs = super(StudentAdminSignupView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        kwargs.update({"request": self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "students"
        kwargs["forms"] = self.form2
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.POST.get("more") == "on":
            return redirect("students:student_signup")
        else:
            return redirect("users:dash")


# display profile of students
@method_decorator([teacher_admin_student], name="dispatch")
class StudentProfileView(LoginRequiredMixin, DetailView):
    model = Student
    login_url = "account_login"
    context_object_name = "student"
    template_name = "student/studentprofile.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    def get_queryset(self):
        # a vey useful feature that reduces number of queries from 22 to 6
        # i have added the foreign keys i would use in the html to be
        # preloaded so they wouldnt to called continually
        # instead they would be cached
        student = Student.objects.all().select_related(
            "studentmodel__class_name",
            "studentmodel__sub_class",
            "studentmodel__created_by",
            "studentmodel__updated_by",
        )
        return student


# update view of student for admin
@method_decorator([admin_required], name="dispatch")
class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = StudentModel
    login_url = "account_login"
    template_name = "student/update.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"
    fields = [
        "name",
        "photo",
        "section",
        "class_name",
        "sub_class",
        "fathers_name",
        "mothers_name",
        "date_of_birth",
        "email",
        "address",
        "emergency_mobile_number",
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.class_name.section != self.object.section:
            messages.error(self.request, "The section does not fit the class")
            return super().form_invalid(form)
        elif self.object.sub_class.class_name != self.object.class_name:
            messages.error(self.request, "The sub_class does not fit the class")
            return super().form_invalid(form)
        else:
            self.object.updated_by = self.request.user
            form.save()
            messages.success(self.request, "Student has been updated")
            return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("users:dash")


# update view of student for teacher and student
@method_decorator([teacher_admin_student], name="dispatch")
class StudentTeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = StudentModel
    login_url = "account_login"
    template_name = "student/update.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"
    fields = [
        "name",
        "photo",
        "fathers_name",
        "mothers_name",
        "date_of_birth",
        "email",
        "address",
        "emergency_mobile_number",
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_student:
            messages.success(self.request, "Updated!")
            return reverse_lazy("students:dash")
        else:
            messages.success(self.request, "Student has been updated")
            return reverse_lazy("students:student_teacher_list")


def payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        primary_key = request.POST.get("primary_key")
        value = request.POST.get("value")
        student = get_object_or_404(StudentModel, pk=primary_key)
        try:
            if value != "False":
                student.paid = True
                student.save()
                messages.success(request, f"{name} has Paid")
                return render(request, "others/message.html")
            else:
                student.paid = False
                student.save()
                messages.error(request, f"{name} has not Paid")
                return render(request, "others/message.html")

        except Exception as err:
            messages.error(request, f"{err}")
            return render(request, "others/message.html")


# student list for teachers
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def student_teacher_list(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    ).values("pk", "name", "emergency_mobile_number", "uuid", "paid")

    context = {"students": students}

    return render(request, "student/student_list.html", context)


# student list for students
@login_required
@user_passes_test(user_is_student, login_url="home")
def student_list(request):
    students = StudentModel.objects.filter(
        class_name=request.user.studentmodel.class_name_id,
        sub_class=request.user.studentmodel.sub_class_id,
    ).select_related("class_name", "sub_class")

    context = {"students": students}

    return render(request, "student/students_list.html", context)


# delete student
@method_decorator([admin_required], name="dispatch")
class StudentDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Student
    template_name = "student/student_delete.html"
    success_url = reverse_lazy("students:list")
    login_url = "account_login"
    context_object_name = "students"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"
    success_message = "Student has been deleted."


# student dashboard
@login_required
@user_passes_test(user_is_student, login_url="home")
def student_dashboard(request):
    class_name = request.user.studentmodel.class_name_id
    sub_class = request.user.studentmodel.sub_class_id
    total_student = StudentModel.objects.filter(
        class_name=class_name,
        sub_class=sub_class,
    )
    teachers = TeacherModel.objects.filter(
        class_name=class_name,
        sub_class=sub_class,
    )
    courses = Subject.objects.filter(
        class_name=class_name,
    )

    three_message = StudentMessages.objects.filter(student=request.user.studentmodel)[
        :3
    ].select_related("teacher", "student")

    context = {
        "student": len(total_student),
        "teachers": teachers,
        "courses": len(courses),
        "message": three_message,
    }
    return render(request, "student/student_dashboard.html", context)


# result checking for students
@login_required
@user_passes_test(user_is_student, login_url="home")
def show_result(request):
    class_name = Class.objects.all()
    session = Session.objects.all()
    if request.method == "POST":
        class_id = request.POST.get("class_name")
        session_id = request.POST.get("session")

        class_name = get_object_or_404(Class, pk=class_id)
        session = get_object_or_404(Session, id=session_id)

        student_result = SubjectResult.objects.filter(
            student=request.user.pk, session=session, class_name=class_name
        ).select_related("subject")
        if student_result:
            first = student_result[0].session.session_name
            # checks either to be promoted to next session or next class
            if student_result[0].session != Session.objects.last():
                promote_session = get_object_or_404(
                    Session, pk=student_result[0].session.id + 1
                ).session_name
            else:
                promote_session = get_object_or_404(
                    Class, pk=student_result.class_name.pk + 1
                ).class_name
            # calculates the total percentage
            normal_total, student_total = 0, 0
            for result in student_result:
                normal_total += 100
                student_total += result.total_score
            percentage = (student_total / normal_total) * 100

            for comments in student_result:
                if comments.teachers_comment:
                    comment = comments.teachers_comment
                    break
                else:
                    comment = "No comment has been inputed for this student."

            context = {
                "student_result": student_result,
                "first": first,
                "next": promote_session,
                "percentage": percentage,
                "total": student_total,
                "comment": comment,
            }
            return render(request, "student/student_result.html", context)
        else:
            # checks only for class and student and not session
            if SubjectResult.objects.filter(
                student=request.user.pk, class_name=class_name
            ):
                messages.error(request, "No result found for this session")
                return redirect("students:show_result")
            else:
                messages.error(request, "No result found for this category")
                return redirect("students:show_result")

    context = {
        "classes": class_name,
        "sessions": session,
    }

    return render(request, "student/show_result.html", context)


# view messages for students
@login_required
@user_passes_test(user_is_student, login_url="home")
def view_messages(request):
    message = StudentMessages.objects.filter(
        student=request.user.studentmodel, private=True
    ).select_related("teacher", "student")

    context = {"message": message}

    return render(request, "student/view_message.html", context)


# message checking for students
@login_required
@user_passes_test(user_is_student, login_url="home")
def view_general_messages(request):
    message = StudentMessages.objects.filter(
        student=request.user.studentmodel, private=False
    ).select_related("teacher", "student")

    context = {"message": message}

    return render(request, "student/view_message.html", context)


# search student for teacher and admin
@login_required
@user_passes_test(teacher_admin_student, login_url="home")
def search_all(request):
    if request.method == "GET":
        query = request.GET.get("q")
        student = StudentModel.objects.filter(
            Q(name__icontains=query) | Q(class_name__class_name__icontains=query)
        ).select_related("class_name", "sub_class")
        teacher = TeacherModel.objects.filter(
            Q(name__icontains=query) | Q(class_name__class_name__icontains=query)
        ).select_related("class_name", "sub_class")
        context = {"students": student, "teachers": teacher}
        return render(request, "student/search_all.html", context)
