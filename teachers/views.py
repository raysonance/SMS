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
from students.models import StudentModel, Subject, SubjectResult

from .forms import TeacherSignUpForm
from .models import Session, TeacherModel


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
        class_name=request.user.teachermodel.class_name.pk
    ).count()
    context = {
        "student": total_student,
    }
    return render(request, "teachers/teacher.html", context)


@user_passes_test(user_is_teacher, login_url="home")
def add_result(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name
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
        class_name=request.user.teachermodel.class_name
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
