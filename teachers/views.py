from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

# Create your views here.
from schoolz.users.decorators import (
    admin_required,
    admin_student,
    teacher_admin,
    teacher_required,
    user_is_admin,
    user_is_teacher,
)
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


# teacher signup for admins
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
        return redirect("users:dash")


# Teacher list for students and admin
@method_decorator([admin_student], name="dispatch")
class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    login_url = "home"
    template_name = "teachers/list.html"
    context_object_name = "teachers"

    def get_queryset(self):
        # a vey useful feature that reduces number of queries from 22 to 4
        # i have added the foreign keys i would use in the html to be preloaded so they wouldn't to called continually
        # instead they would be prefetched
        teachers = Teacher.objects.all().select_related(
            "teachermodel__class_name", "teachermodel__sub_class"
        )
        return teachers


class TeacherProfileView(LoginRequiredMixin, DetailView):
    model = Teacher
    login_url = "home"
    context_object_name = "teacher"
    template_name = "teachers/teacherprofile.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"


# Teacher update view for teachers only
@method_decorator([teacher_required], name="dispatch")
class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = TeacherModel
    login_url = "home"  # "account_login"
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


# Teacher update view for admin
@method_decorator([admin_required], name="dispatch")
class AdminTeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = TeacherModel
    login_url = "home"  # "account_login"
    template_name = "teachers/update.html"
    fields = [
        "section",
        "class_name",
        "sub_class",
    ]

    def get_success_url(self):
        return reverse_lazy("teachers:list")


# admin only
@method_decorator([admin_required], name="dispatch")
class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_delete.html"
    success_url = reverse_lazy("teachers:list")
    login_url = "account_login"
    context_object_name = "teachers"


@user_passes_test(user_is_teacher, login_url="home")
def teacher_dashboard(request):
    total_student = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    ).count()
    context = {
        "student": total_student,
    }
    return render(request, "teachers/teacher.html", context)


# for teachers to add student result
@user_passes_test(user_is_teacher, login_url="home")
def add_result(request):
    # using _id at the end of a request method can reduce the query by one
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    ).values("pk", "name")
    session = Session.objects.all()
    subjects = Subject.objects.filter(
        class_name=request.user.teachermodel.class_name_id
    ).values("id", "subject_name")
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


# for teachers to check result
@user_passes_test(user_is_teacher, login_url="home")
def show_result(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
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

        student = get_object_or_404(StudentModel, pk=student_id)
        session = get_object_or_404(Session, id=session_id)

        student_result = SubjectResult.objects.filter(student=student, session=session)

        context = {"student_result": student_result}

        if student_result:
            return render(request, "teachers/student_result.html", context)
        else:
            messages.error(request, "No result found for this session")
            return redirect("teachers:show_result")


# for promoting students up one class
@user_passes_test(user_is_teacher, login_url="home")
def promote_student(request):
    id_name = request.user.teachermodel.class_name_id
    students = StudentModel.objects.filter(
        class_name=id_name,
        sub_class=request.user.teachermodel.sub_class_id,
    ).values("pk", "name")

    new_class = id_name + 1

    try:
        check_exists = Class.objects.filter(pk=new_class).exists()

        if check_exists:
            new_class_name = get_object_or_404(Class, pk=new_class)
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

    sub_class = SubClass.objects.filter(class_name=new_class)

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
            student.save()
            messages.success(request, "Student promoted Successfully")
            return redirect("teachers:promote")
        else:
            messages.error(
                request,
                "Complete result not found for this student. Contact admin to promote this student",
            )
            return redirect("teachers:promote")


# note to self study this carefully and use this for all those rubbish two times processing you made before
# for teachers to send messages to students
@user_passes_test(user_is_teacher, login_url="home")
def send_messages(request):
    form = StudentMessageForm()
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    )
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
            messages.success(request, "Message sent successfully")
            return redirect("teachers:message")

    context = {
        "students": students,
        "form": form,
    }

    return render(request, "teachers/send_message.html", context)


# general messages
@user_passes_test(user_is_teacher, login_url="home")
def send_general_message(request):
    form = StudentMessageForm()
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
    )
    if request.method == "POST":
        for pupil in students:
            student = get_object_or_404(StudentModel, pk=pupil.pk)
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


# for teachers to view messages
@user_passes_test(user_is_teacher, login_url="home")
def view_messages(request):
    message = StudentMessages.objects.filter(
        teacher=request.user.teachermodel, private=True
    ).select_related("teacher", "student")
    context = {"message": message}

    return render(request, "student/view_message.html", context)


# for teachers to view general messages
@user_passes_test(user_is_teacher, login_url="home")
def view_general_messages(request):
    message = StudentMessages.objects.filter(
        teacher=request.user.teachermodel, private=False
    ).select_related("teacher", "student")

    context = {"message": message}

    return render(request, "student/view_message.html", context)


# for teachers to update messages
@method_decorator([teacher_admin], name="dispatch")
class UpdateMessage(UpdateView):
    model = StudentMessages
    template_name = "teachers/update_message.html"
    fields = [
        "title",
        "message",
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_at = timezone.now()
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Message updated successfully")
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto


@method_decorator([teacher_admin], name="dispatch")
class DeleteMessage(DeleteView):
    model = StudentMessages
    template_name = "teachers/delete_message.html"
    context_object_name = "message"

    def get_success_url(self):
        messages.success(self.request, "Message deleted successfully")
        # helps it to return directly to the previous page before the form
        nexto = self.request.POST.get("next", "/")
        return nexto


# admin list of student
@user_passes_test(user_is_admin, login_url="home")
def show_list(request):
    class_name = Class.objects.filter(section=request.user.adminmodel.section_id)
    sub_class = SubClass.objects.all()
    context = {"class_name": class_name, "sub_class": sub_class}
    return render(request, "teachers/admin_student.html", context)


def show_admin_student(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("teachers:show_list")
    else:
        class_id = request.POST.get("class_name")
        sub_class_id = request.POST.get("sub_class")

        class_name = get_object_or_404(Class, pk=class_id)
        sub_class = get_object_or_404(SubClass, pk=sub_class_id)

        student = StudentModel.objects.filter(
            class_name=class_name, sub_class=sub_class
        ).select_related("class_name")

        context = {"student": student}

        return render(request, "student/admin_student.html", context)


# next is to add a message for students result update
