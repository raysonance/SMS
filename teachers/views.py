from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from notifications.signals import notify

# Create your views here.
from schoolz.users.decorators import (
    admin_required,
    teacher_admin,
    teacher_required,
    user_is_teacher,
)
from schoolz.users.models import Teacher
from students.forms import StudentMessageForm
from students.models import StudentMessages, StudentModel, Subject, SubjectResult

from .forms import TeacherModelForm, TeacherSignUpForm, TeacherUpdateForm
from .models import Class, Section, Session, SubClass, TeacherMessages, TeacherModel

# todo: add protection to new functions


def load_sub_class(request):
    class_id = request.GET.get("class")
    sub_class = SubClass.objects.filter(class_name=class_id)

    context = {"sub_class": sub_class}
    return render(request, "others/subclass_dropdown_list_options.html", context)


def load_class(request):
    section_id = request.GET.get("section")
    class_name = Class.objects.filter(section=section_id)

    context = {"class_name": class_name}
    return render(request, "others/class_dropdown_list_option.html", context)


def show_teachers_comment(request):
    try:
        student_id = request.GET.get("student")
        session_id = request.GET.get("session")
        student_result = SubjectResult.objects.filter(
            student=student_id,
            session=session_id,
        ).select_related("student")

        context = {"result": student_result}
        return render(request, "others/comment.html", context)

    except Exception:
        messages.error(request, "Cannot load teacher comments, contact administrator.")
        return render(request, "teachers/add_result.html", context)


def load_student_result(request):
    if request.method == "GET":
        student_id = request.GET.get("students")
        session_id = request.GET.get("session")

        student = get_object_or_404(StudentModel, pk=student_id)
        session = get_object_or_404(Session, id=session_id)

        student_result = SubjectResult.objects.filter(student=student, session=session)

        context = {"student_result": student_result, "student": student.name}

        if student_result:
            return render(request, "others/student_result.html", context)
        else:
            return render(request, "others/student_result.html", context)


# teacher signup
@method_decorator([admin_required], name="dispatch")
class TeacherSignupView(LoginRequiredMixin, CreateView):
    model = Teacher
    login_url = "account_login"
    form_class = TeacherSignUpForm
    form2 = TeacherModelForm
    template_name = "teachers/signup.html"

    def get_form_kwargs(self):
        kwargs = super(TeacherSignupView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        kwargs.update({"request": self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "teachers"
        kwargs["form2"] = self.form2
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.POST.get("more") == "on":
            return redirect("teachers:signup")
        else:
            return redirect("users:dash")


# list for student and admin
def teacher_list(request, section):
    if section == "Primary":
        get_section = get_object_or_404(Section, pk=1)
        teachers = TeacherModel.objects.filter(section=get_section).select_related(
            "class_name",
            "sub_class",
        )
        context = {"teachers": teachers, "section": get_section}
        return render(request, "teachers/list.html", context)
    else:
        get_section = get_object_or_404(Section, pk=2)
        teachers = TeacherModel.objects.filter(section=get_section).select_related(
            "class_name",
            "sub_class",
        )
        context = {"teachers": teachers, "section": get_section}
        return render(request, "teachers/list.html", context)


class TeacherProfileView(LoginRequiredMixin, DetailView):
    model = TeacherModel
    login_url = "account_login"
    context_object_name = "teacher"
    template_name = "teachers/teacherprofile.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    def get_queryset(self):
        # a very useful feature that reduces number of queries from 22 to 6
        teacher = TeacherModel.objects.all().select_related(
            "class_name",
            "sub_class",
        )
        return teacher


# Teacher update view for teachers only
@method_decorator([teacher_required], name="dispatch")
class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = TeacherModel
    login_url = "account_login"
    template_name = "teachers/update.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"
    fields = [
        "name",
        "photo",
        "date_of_birth",
        "mobile",
        "joining_date",
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if "name" in form.changed_data:
            try:
                teacher = Teacher.objects.get(pk=self.object.pk)
                teacher.name = self.object.name
                teacher.save()
            except Exception as err:
                messages.error(self.request, f"{err}")
                return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, "Updated!")
        return reverse_lazy("teachers:dash")


# Teacher update view for admin
@method_decorator([admin_required], name="dispatch")
class AdminTeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = TeacherModel
    login_url = "account_login"
    template_name = "teachers/update.html"
    form_class = TeacherUpdateForm
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    def get_form_kwargs(self):
        kwargs = super(AdminTeacherUpdateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user.adminmodel
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.section != self.request.user.adminmodel.section:
            messages.error(self.request, "Can not assign teacher to this section!")
            return super().form_invalid(form)
        elif self.object.class_name.section != self.request.user.adminmodel.section:
            messages.error(self.request, "The section does not fit the class")
            return super().form_invalid(form)
        elif self.object.sub_class.class_name != self.object.class_name:
            messages.error(self.request, "The sub_class does not fit the class")
            return super().form_invalid(form)
        else:
            # this changes the value in the user model
            if "email" in form.changed_data:
                try:
                    teacher = Teacher.objects.get(pk=self.object.pk)
                    # this just adds a new email address but doesn't delete the old one
                    teacher.email = self.object.email
                    teacher.save()
                except Exception as err:
                    messages.error(self.request, f"{err}")
                    return super().form_invalid(form)
            if "name" in form.changed_data:
                try:
                    teacher = Teacher.objects.get(pk=self.object.pk)
                    teacher.name = self.object.name
                    teacher.save()
                except Exception as err:
                    messages.error(self.request, f"{err}")
                    return super().form_invalid(form)
            form.save()
            messages.success(self.request, "Teacher has been updated!")
            return super().form_valid(form)

    def get_success_url(self):
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto


# admin only
@method_decorator([admin_required], name="dispatch")
class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_delete.html"
    login_url = "account_login"
    context_object_name = "teachers"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    def get_success_url(self):
        messages.success(self.request, "Teacher has been deleted!")
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def teacher_dashboard(request):
    total_student = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    ).values("pk", "paid", "class_name__class_name", "sub_class__sub_class")
    sub_class = SubClass.objects.filter(
        id=request.user.teachermodel.sub_class_id,
    ).values("class_name__class_name", "sub_class")
    total_student_count = len(total_student)
    three_message = [
        x
        for x in TeacherMessages.objects.filter(
            teacher=request.user.teachermodel
        ).select_related("admin")[:3]
        if x.was_published_recently()
    ]

    paid_students = len([student for student in total_student if student["paid"]])
    unpaid = total_student_count - paid_students

    context = {
        "student": total_student_count,
        "paid_students": paid_students,
        "message": three_message,
        "unpaid": unpaid,
        "sub_class": sub_class,
    }
    return render(request, "teachers/teacher.html", context)


# for teachers to add student result
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def add_result(request):
    if request.method == "POST":
        student_id = request.POST.get("students")
        subject_id = request.POST.get("subject")
        session_id = request.POST.get("session")
        first_test = request.POST.get("first_test")
        second_test = request.POST.get("second_test")
        third_test = request.POST.get("third_test")
        fourth_test = request.POST.get("fourth_test")
        exam_score = request.POST.get("exam_score")
        total_score = request.POST.get("total_score")
        grade = request.POST.get("grade")
        remark = request.POST.get("remark")

        if student_id and subject_id and session_id:
            student_obj = get_object_or_404(StudentModel, pk=student_id)
            subject_obj = get_object_or_404(Subject, id=subject_id)
            session_obj = get_object_or_404(Session, id=session_id)
        else:
            messages.error(request, "Failed to Add Result!")
            return redirect("teachers:add_result")

        try:
            # Check if Students Result Already Exists or not
            check_exist = SubjectResult.objects.filter(
                subject=subject_obj, student=student_obj, session=session_obj
            ).exists()
            if check_exist:
                result = SubjectResult.objects.get(
                    subject=subject_obj, student=student_obj, session=session_obj
                )
                result.session = session_obj
                result.first_test = first_test
                result.second_test = second_test
                result.third_test = third_test
                result.fourth_test = fourth_test
                result.exam_score = exam_score
                result.total_score = total_score
                result.grade = grade
                result.remark = remark
                result.save()
                messages.success(request, "Result updated successfully!")
                return redirect("teachers:add_result")
            else:
                result = SubjectResult(
                    student=student_obj,
                    subject=subject_obj,
                    session=session_obj,
                    class_name=request.user.teachermodel.class_name,
                    first_test=first_test,
                    second_test=second_test,
                    third_test=third_test,
                    fourth_test=fourth_test,
                    exam_score=exam_score,
                    total_score=total_score,
                    grade=grade,
                    remark=remark,
                )
                result.save()
                messages.success(request, "Result added successfully!")
                return redirect("teachers:add_result")

        except Exception as err:
            messages.error(request, f"{err}")
            return redirect("teachers:add_result")

    # using _id at the end of a request method can reduce the query by one
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    ).values("pk", "name")
    session = Session.objects.all().values("id", "session_name")
    subjects = Subject.objects.filter(
        class_name=request.user.teachermodel.class_name_id
    ).values("id", "subject_name")
    context = {"students": students, "subjects": subjects, "sessions": session}
    return render(request, "teachers/add_result.html", context)


# add teacher comment
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def teachers_comment(request):
    if request.method == "POST":
        student_id = request.POST.get("students")
        session_id = request.POST.get("session")
        teacher_comment = request.POST.get("comment")

        student = get_object_or_404(StudentModel, pk=student_id)
        session = get_object_or_404(Session, id=session_id)

        student_result = SubjectResult.objects.filter(
            student=student,
            class_name=request.user.teachermodel.class_name_id,
            session=session,
        )

        if student_result:
            try:
                for subjects in student_result:
                    if subjects.teachers_comment:
                        subjects.teachers_comment = teacher_comment
                        subjects.save(update_fields=["teachers_comment"])
                        messages.success(request, "Comment updated successfully!")
                        return redirect("teachers:add_result")

                student_result[0].teachers_comment = teacher_comment
                student_result[0].save(update_fields=["teachers_comment"])
                messages.success(request, "Comment added successfully!")
                return redirect("teachers:add_result")

            except Exception as err:
                messages.error(request, f"{err}")
                return redirect("teachers:add_result")
        else:
            messages.error(request, "Please add student result first")
            return redirect("teachers:add_result")


# for teachers to check result
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def show_result(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    ).values("pk", "name")

    session = Session.objects.all().values("id", "session_name")

    if request.method == "POST":
        student_id = request.POST.get("students")
        session_id = request.POST.get("session")

        student = get_object_or_404(StudentModel, pk=student_id)
        session = get_object_or_404(Session, id=session_id)

        student_result = SubjectResult.objects.filter(student=student, session=session)

        context = {"student_result": student_result, "student": student}

        if student_result:
            return render(request, "teachers/student_result.html", context)
        else:
            messages.error(request, "No result found for this session")
            return redirect("teachers:show_result")

    context = {
        "students": students,
        "sessions": session,
    }

    return render(request, "teachers/show_result.html", context)


# for promoting students up one class
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def promote_student(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
        active=True,
    ).values("pk", "name")

    new_class = request.user.teachermodel.class_name_id + 1

    try:
        check_exists = Class.objects.filter(pk=new_class).exists()

        if check_exists:
            klass = Class.objects.values("pk", "class_name")
            new_class_name = get_object_or_404(klass, pk=new_class)
        else:
            messages.error(request, "Can not promote in this class.")
            return redirect("teachers:dash")
    except Exception as err:
        messages.error(request, f"Can not promote in this class because {err}")
        return redirect("teachers:dash")

    sub_class = SubClass.objects.filter(class_name=new_class).values("pk", "sub_class")

    context = {
        "students": students,
        "new_class": new_class_name,
        "sub_class": sub_class,
    }

    return render(request, "teachers/promote.html", context)


def promote_student_process(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("teachers:dash")
    else:
        student_id = request.POST.get("students")
        class_id = request.POST.get("classes")
        sub_class_id = request.POST.get("sub_class")

        student = get_object_or_404(StudentModel, pk=student_id)
        class_name = get_object_or_404(Class, pk=class_id)
        previous_class_id = int(class_id) - 1
        previous_class = get_object_or_404(Class, pk=previous_class_id)
        sub_class = get_object_or_404(SubClass, pk=sub_class_id)
        session = get_object_or_404(Session, pk=3)

        student_result = SubjectResult.objects.filter(
            student=student, class_name=previous_class, session=session
        )

        if student_result:
            student.class_name = class_name
            student.sub_class = sub_class
            student.paid = False
            student.active = False
            student.save()
            messages.success(request, "Student promoted successfully!")
            return redirect("teachers:promote")
        else:
            messages.error(
                request,
                "Complete result not found for this student. Contact admin to promote this student",
            )
            return redirect("teachers:promote")


# for teachers to send messages to students
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def send_messages(request):
    form = StudentMessageForm()
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    ).values("pk", "name")
    if request.method == "POST":
        form = StudentMessageForm(request.POST)
        student_id = request.POST.get("students")
        student = get_object_or_404(StudentModel, pk=student_id)
        if form.is_valid():
            student_message = form.save(commit=False)
            student_message.teacher = request.user.teachermodel
            student_message.student = student
            student_message.private = True
            student_message.save()
            notify.send(
                sender=request.user,
                recipient=student.user,
                verb="new private message!",
                target=student.user,
            )
            messages.success(request, "Message sent successfully!")
            return redirect("teachers:message")

    context = {
        "students": students,
        "form": form,
    }

    return render(request, "teachers/send_message.html", context)


# general messages
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def send_general_message(request):
    form = StudentMessageForm()
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    )
    if request.method == "POST":
        for pupil in students:
            student = get_object_or_404(students, pk=pupil.pk)
            form = StudentMessageForm(request.POST)
            if form.is_valid():
                student_message = form.save(commit=False)
                student_message.teacher = request.user.teachermodel
                student_message.student = student
                student_message.save()
                notify.send(
                    sender=request.user,
                    recipient=student.user,
                    verb="new general message!",
                    target=student.user,
                )
            else:
                messages.error(request, "Message failed to send.")
                return redirect("teachers:general_message")
        if pupil == students.last():
            messages.success(request, "Message sent to all students successfully!")
            return redirect("teachers:general_message")

    context = {
        "form": form,
    }

    return render(request, "teachers/send_general_message.html", context)


# todo: merge html of admin send messages and teacher send messages

# for teachers to view messages
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def view_messages(request):
    message = StudentMessages.objects.filter(
        teacher=request.user.teachermodel
    ).select_related("teacher", "student")
    context = {"message": message}

    return render(request, "student/view_message.html", context)


# view admin messages for teachers
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def view_admin_messages(request):
    message = TeacherMessages.objects.filter(
        teacher=request.user.teachermodel, private=True
    ).select_related("admin", "teacher")

    context = {"message": message}

    return render(request, "users/view_message.html", context)


# view admin messagesfor teachers
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def view_general_messages(request):
    message = TeacherMessages.objects.filter(
        teacher=request.user.teachermodel, private=False
    ).select_related("teacher", "admin")

    context = {"message": message}

    return render(request, "users/view_message.html", context)


# for teachers to update messages
@method_decorator([teacher_admin], name="dispatch")
class UpdateMessage(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentMessages
    template_name = "teachers/update_message.html"
    login_url = "account_login"
    slug_field = "slug"
    slug_url_kwarg = "slug_pk"
    fields = [
        "title",
        "message",
    ]
    success_message = "Message updated successfully!"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_at = timezone.now()
        form.save()
        notify.send(
            sender=self.object.teacher.user,
            recipient=self.object.student.user,
            verb="updated message!",
            target=self.object.student.user,
        )
        return super().form_valid(form)

    def get_success_url(self):
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto


# for teachers to delete messages
@method_decorator([teacher_admin], name="dispatch")
class DeleteMessage(LoginRequiredMixin, DeleteView):
    model = StudentMessages
    template_name = "teachers/delete_message.html"
    login_url = "account_login"
    context_object_name = "message"
    slug_field = "slug"
    slug_url_kwarg = "slug_pk"

    def get_success_url(self):
        messages.success(self.request, "Message deleted successfully!")
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto
