from django.contrib import messages
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
from schoolz.users.decorators import admin_required, admin_student, teacher_required
from schoolz.users.models import Teacher
from students.forms import StudentMessageForm
from students.models import StudentMessages, StudentModel, Subject, SubjectResult

from .forms import TeacherSignUpForm
from .models import Class, Session, SubClass, TeacherModel


def load_sub_class(request):
    class_id = request.GET.get("class")
    sub_class = SubClass.objects.filter(class_name=class_id).order_by("sub_class")

    context = {"sub_class": sub_class}
    return render(request, "others/subclass_dropdown_list_options.html", context)


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
        if self.request.user.is_admin:
            return redirect("users:dash")


@method_decorator([admin_student], name="dispatch")
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
        "mobile",
        "email",
        "joining_date",
    ]

    def get_success_url(self):
        return reverse_lazy("teachers:dash")


@method_decorator([admin_required], name="dispatch")
class AdminTeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = TeacherModel
    login_url = "account_login"
    template_name = "teachers/update.html"
    fields = [
        "class_name",
        "sub_class",
    ]

    def get_success_url(self):
        return reverse_lazy("teachers:list")


@method_decorator([admin_required], name="dispatch")
class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_delete.html"
    success_url = reverse_lazy("teachers:list")
    login_url = "account_login"
    context_object_name = "teachers"


def user_is_teacher(user):
    if user.is_teacher:
        return True


@user_passes_test(user_is_teacher, login_url="home")
def teacher_dashboard(request):
    total_student = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name.pk,
        sub_class=request.user.teachermodel.sub_class.pk,
    ).count()
    context = {
        "student": total_student,
    }
    return render(request, "teachers/teacher.html", context)


@user_passes_test(user_is_teacher, login_url="home")
def add_result(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name,
        sub_class=request.user.teachermodel.sub_class,
    )
    session = Session.objects.all()
    subjects = Subject.objects.filter(class_name=request.user.teachermodel.class_name)
    context = {"students": students, "subjects": subjects, "sessions": session}
    return render(request, "teachers/add_result.html", context)


def staff_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("teachers:add_result")
    else:
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
            student_obj = StudentModel.objects.get(pk=student_id)
            subject_obj = Subject.objects.get(id=subject_id)
            session_obj = Session.objects.get(id=session_id)
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
                messages.success(request, "Result Updated Successfully!")
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
                messages.success(request, "Result Added Successfully!")
                return redirect("teachers:add_result")
        except (
            ArithmeticError,
            ValueError,
            KeyError,
            EnvironmentError,
            TypeError,
            IndexError,
            AssertionError,
            AttributeError,
            ConnectionAbortedError,
            ConnectionError,
            BrokenPipeError,
            ChildProcessError,
            ConnectionRefusedError,
            ConnectionResetError,
            FileNotFoundError,
            InterruptedError,
            NotImplementedError,
            SystemError,
            SyntaxError,
            TimeoutError,
            UnboundLocalError,
            UnicodeError,
        ):
            messages.error(request, "Failed to Add Result!")
            return redirect("teachers:add_result")


def show_result(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name,
        sub_class=request.user.teachermodel.sub_class,
    )

    session = Session.objects.all()

    context = {
        "students": students,
        "sessions": session,
    }

    return render(request, "teachers/show_result.html", context)


def show_student_result(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("teachers:show_result")
    else:
        student_id = request.POST.get("students")
        session_id = request.POST.get("session")

        student = StudentModel.objects.get(pk=student_id)
        session = Session.objects.get(id=session_id)

        student_result = SubjectResult.objects.filter(student=student, session=session)

        context = {"student_result": student_result}

        if student_result:
            return render(request, "teachers/student_result.html", context)
        else:
            messages.error(request, "No result found for this session")
            return redirect("teachers:show_result")


def promote_student(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name,
        sub_class=request.user.teachermodel.sub_class,
    )

    class_name = Class.objects.get(
        class_name=request.user.teachermodel.class_name.class_name
    )

    new_class = class_name.pk + 1

    try:
        check_exists = Class.objects.filter(pk=new_class).exists()

        if check_exists:
            new_class_name = Class.objects.get(pk=new_class)
        else:
            messages.error(request, "Can not promote in this class.")
            return redirect("teachers:dash")

    except (
        ArithmeticError,
        ValueError,
        KeyError,
        EnvironmentError,
        TypeError,
        IndexError,
        AssertionError,
        AttributeError,
        ConnectionAbortedError,
        ConnectionError,
        BrokenPipeError,
        ChildProcessError,
        ConnectionRefusedError,
        ConnectionResetError,
        FileNotFoundError,
        InterruptedError,
        NotImplementedError,
        SystemError,
        SyntaxError,
        TimeoutError,
        UnboundLocalError,
        UnicodeError,
    ):
        messages.error(request, "Can not promote in this class.")
        return redirect("teachers:dash")

    sub_class = SubClass.objects.filter(class_name=new_class_name)

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

        student = StudentModel.objects.get(pk=student_id)
        class_name = Class.objects.get(pk=class_id)
        previous_class_id = int(class_id) - 1
        previous_class = Class.objects.get(pk=previous_class_id)
        sub_class = SubClass.objects.get(pk=sub_class_id)
        session = Session.objects.get(pk=3)

        student_result = SubjectResult.objects.filter(
            student=student, class_name=previous_class, session=session
        )

        if student_result:
            student.class_name = class_name
            student.sub_class = sub_class
            student.save()
            messages.success(request, "Student promoted Successfully")
            return redirect("teachers:promote")
        else:
            messages.error(
                request,
                "Complete result not found for this student. Contact admin to promote this student",
            )
            return redirect("teachers:promote")


def send_messages(request):
    form = StudentMessageForm()
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name,
        sub_class=request.user.teachermodel.sub_class,
    )
    if request.method == "POST":
        form = StudentMessageForm(request.POST)
        student_id = request.POST.get("students")
        student = StudentModel.objects.get(pk=student_id)
        if form.is_valid():
            student_message = form.save(commit=False)
            student_message.teacher = request.user.teachermodel
            student_message.student = student
            student_message.save()
            messages.success(request, "Message sent successfully")
            return redirect("teachers:message")

    context = {
        "students": students,
        "form": form,
    }

    return render(request, "teachers/send_message.html", context)


def send_general_message(request):
    form = StudentMessageForm()
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name,
        sub_class=request.user.teachermodel.sub_class,
    )
    if request.method == "POST":
        for pupil in students:
            student = StudentModel.objects.get(pk=pupil.pk)
            form = StudentMessageForm(request.POST)
            if form.is_valid():
                student_message = form.save(commit=False)
                student_message.teacher = request.user.teachermodel
                student_message.student = student
                student_message.save()
            else:
                messages.error(request, "Message failed to send.")
                return redirect("teachers:general_message")
        if pupil == students.last():
            messages.success(request, "Message sent to all students successfully")
            return redirect("teachers:general_message")

    context = {
        "form": form,
    }

    return render(request, "teachers/send_general_message.html", context)


def view_messages(request):
    message = StudentMessages.objects.filter(
        teacher=request.user.teachermodel
    ).order_by("-created_at")

    context = {"message": message}

    return render(request, "student/view_message.html", context)


class UpdateMessage(UpdateView):
    model = StudentMessages
    template_name = "teachers/update_message.html"
    fields = [
        "title",
        "message",
    ]

    def get_success_url(self):
        return reverse_lazy("teachers:view_message")


class DeleteMessage(DeleteView):
    model = StudentMessages
    template_name = "teachers/delete_message.html"
    context_object_name = "message"
    success_url = reverse_lazy("teachers:view_message")
