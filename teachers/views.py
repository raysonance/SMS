import decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from notifications.signals import notify

# Create your views here.
from schoolz.users.decorators import (
    admin_required,
    student_admin,
    teacher_admin,
    teacher_required,
    user_is_teacher,
)
from schoolz.users.models import College, Teacher
from students.forms import StudentMessageForm
from students.models import (
    ArticlePost,
    AssignmentSolution,
    Choice,
    ClassTestPost,
    ClassTestSolution,
    ClassWorkPost,
    CommentReply,
    DocumentPost,
    ImagePost,
    PostComment,
    Question,
    StudentChoice,
    StudentMessages,
    StudentModel,
    Subject,
    SubjectResult,
    TextPost,
    VideoPost,
    YouTubePost,
)

from .forms import TeacherModelForm, TeacherSignUpForm, TeacherUpdateForm
from .models import Class, Section, Session, SubClass, TeacherMessages, TeacherModel

# todo: add function for adminmodel, teachermodel, studentmodel


# function for ajax fetching of user subclass
def load_sub_class(request):
    class_id = request.GET.get("class")
    sub_class = SubClass.objects.filter(class_name=class_id)

    context = {"sub_class": sub_class}
    return render(request, "others/subclass_dropdown_list_options.html", context)


# function for ajax fetching of user class
def load_class(request):
    section_id = request.GET.get("section")
    class_name = Class.objects.filter(section=section_id)

    context = {"class_name": class_name}
    return render(request, "others/class_dropdown_list_option.html", context)


# function for ajax fetching of user comment for results
def show_teachers_comment(request):
    try:
        student_id = request.GET.get("student")
        session_id = request.GET.get("session")
        class_id = request.user.teachermodel.class_name_id
        student_result = SubjectResult.objects.filter(
            student=student_id, session=session_id, class_name=class_id
        ).select_related("student")

        context = {"result": student_result}
        return render(request, "others/comment.html", context)

    except Exception:
        messages.error(request, "Cannot load teacher comments, contact administrator.")
        return render(request, "teachers/add_result.html", context)


# function for ajax fetching of user result
def load_student_result(request):
    if request.method == "GET":
        student_id = request.GET.get("students")
        session_id = request.GET.get("session")
        class_id = request.user.teachermodel.class_name_id

        student = get_object_or_404(StudentModel, pk=student_id)
        session = get_object_or_404(Session, id=session_id)
        klass = get_object_or_404(Class, pk=class_id)

        student_result = SubjectResult.objects.filter(
            student=student, session=session, class_name=klass
        )

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
    form_class = TeacherSignUpForm  # for user model
    form2 = TeacherModelForm  # for teacher model
    template_name = "teachers/signup.html"

    def get_form_kwargs(self):
        kwargs = super(TeacherSignupView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})  # adds self.request.user to form
        kwargs.update({"request": self.request})  # adds self.request to form
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "teachers"
        kwargs["form2"] = self.form2  # to add second form to sign up html page
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.POST.get("more") == "on":
            return redirect("teachers:signup")
        else:
            return redirect("users:dash")


# list for student and admin
@login_required
@user_passes_test(student_admin, login_url="home")
def teacher_list(request, section):
    if section == "Primary":
        # create Primary first in section!
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


# to show the profile of a teacher
class TeacherProfileView(LoginRequiredMixin, DetailView):
    model = Teacher
    login_url = "account_login"
    context_object_name = "teacher"
    template_name = "teachers/teacherprofile.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    def get_queryset(self):
        # a very useful feature that reduces number of queries from 22 to 6
        teacher = Teacher.objects.all().select_related(
            "teachermodel__class_name",
            "teachermodel__sub_class",
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
        # checks if name is part of what was updated
        if "name" in form.changed_data:
            try:
                teacher = Teacher.objects.get(pk=self.object.pk)
                teacher.name = self.object.name
                teacher.save()
            except Exception as err:
                messages.error(self.request, f"{err}")
                return super().form_invalid(form)
        form.save()
        return super().form_valid(form)

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
        kwargs[
            "user"
        ] = (
            self.request.user.adminmodel
        )  # adds self.request.user.adminmodel to the form
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
    ).values("class_name__class_name", "sub_class", "id")
    total_student_count = len(total_student)
    # contains the three most recent messages and if all are created or updated
    # more than a 30 day timeframe then the list would be empty
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
        # get posted data
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

        # get the model itself
        if student_id and subject_id and session_id:
            student_obj = get_object_or_404(StudentModel, pk=student_id)
            subject_obj = get_object_or_404(Subject, id=subject_id)
            session_obj = get_object_or_404(Session, id=session_id)
        else:
            messages.error(request, "Failed to Add Result!")
            return redirect("teachers:add_result")

        try:
            # Check if Result Already Exists
            check_exist = SubjectResult.objects.filter(
                subject=subject_obj, student=student_obj, session=session_obj
            ).exists()
            if check_exist:  # update
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
                        subjects.save(
                            update_fields=["teachers_comment"]
                        )  # way of saving a field to a saved model
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
            student.paid = False  # sets student paid field to false
            student.active = (
                False  # sets active to false, student will not appear in promotion page
            )
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
            # notify student of incoming message
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


# view admin messages for teachers
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


# classroom


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def college_teacher_classroom(request):
    subclass_pk = (request.user.teachermodel.sub_class_id,)
    pk = subclass_pk[0]

    try:
        college_subclass = SubClass.objects.get(pk=pk)

    except Exception as err:
        messages.error(request, f"{err}")
        context_dict = {
            "college_class": None,
        }
        return render(
            request,
            template_name="college/teacher/classroom/teacher_classroom.html",
            context=context_dict,
        )

    try:
        subjects = [
            subject
            for subject in Subject.objects.all()
            if subject.class_name == college_subclass.class_name
        ]
        students = [
            student
            for student in StudentModel.objects.all()
            if student.class_name == college_subclass.class_name
        ]

    except Exception as err:
        messages.error(request, f"{err}")
        context_dict = {
            "college_class": None,
        }
        return render(
            request,
            template_name="college/teacher/classroom/teacher_classroom.html",
            context=context_dict,
        )

    posts = [
        post
        for post in ClassWorkPost.objects.all()
        if post.subclass == college_subclass
    ]
    textposts = [
        textpost
        for textpost in TextPost.objects.all()
        if textpost.post.subclass == college_subclass
    ]
    videoposts = [
        videopost
        for videopost in VideoPost.objects.all()
        if videopost.post.subclass == college_subclass
    ]
    documentposts = [
        documentpost
        for documentpost in DocumentPost.objects.all()
        if documentpost.post.subclass == college_subclass
    ]
    imageposts = [
        imagepost
        for imagepost in ImagePost.objects.all()
        if imagepost.post.subclass == college_subclass
    ]
    youtubeposts = [
        youtubepost
        for youtubepost in YouTubePost.objects.all()
        if youtubepost.post.subclass == college_subclass
    ]
    articleposts = [
        articlepost
        for articlepost in ArticlePost.objects.all()
        if articlepost.post.subclass == college_subclass
    ]
    classtestposts = [
        classtestpost
        for classtestpost in ClassTestPost.objects.all()
        if classtestpost.post.subclass == college_subclass
    ]

    posts_display = []

    for post in posts:
        for textpost in textposts:
            if textpost.post == post:
                posts_display.insert(0, textpost)
        for videopost in videoposts:
            if videopost.post == post:
                posts_display.insert(0, videopost)
        for documentpost in documentposts:
            if documentpost.post == post:
                posts_display.insert(0, documentpost)
        for imagepost in imageposts:
            if imagepost.post == post:
                posts_display.insert(0, imagepost)
        for youtubepost in youtubeposts:
            if youtubepost.post == post:
                posts_display.insert(0, youtubepost)
        for articlepost in articleposts:
            if articlepost.post == post:
                posts_display.insert(0, articlepost)
        for classtestpost in classtestposts:
            if classtestpost.post == post:
                posts_display.insert(0, classtestpost)

    comments_and_replies = []

    for comment in PostComment.objects.all():
        for post in posts_display:
            if comment.post == post.post:
                try:
                    replies = CommentReply.objects.filter(postcomment=comment)
                    comments_and_replies.append(
                        {
                            "comments": {
                                "post_pk": post.post.pk,
                                "comment": comment,
                                "replies": replies,
                            }
                        }
                    )
                except Exception:
                    pass

    context_dict = {
        "college_class": college_subclass,
        "subjects": subjects,
        "students": students,
        "posts_display": posts_display,
        "comments_and_replies": comments_and_replies,
    }

    return render(
        request,
        template_name="college/teacher/classroom/teacher_classroom.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def college_teacher_classroom_add_post(request, pk=None):
    if request.method == "POST":
        college = College.objects.first()
        college_class_pk = pk
        try:
            # Get the data from the form
            title = request.POST.get("title")
            subject_pk = request.POST.get("subject")
            student_pks = request.POST.get("students").split(" ")
            postype = request.POST.get("postype")

            subclass_post = SubClass.objects.get(pk=college_class_pk)

            if postype == "regular" or postype == "assignment":
                is_assignment = False
                is_classtest = False
                if postype == "assignment":
                    is_assignment = True

                classworkpost = ClassWorkPost.objects.create(
                    college=college,
                    class_name=subclass_post.class_name,
                    subclass=subclass_post,
                    subject=Subject.objects.get(pk=subject_pk),
                    teacher=request.user.teachermodel,
                    title=title,
                    is_assignment=is_assignment,
                    is_classtest=is_classtest,
                )

                # link students to this post
                this_class_students = [
                    student
                    for student in StudentModel.objects.all()
                    if student.sub_class == subclass_post
                    and student.class_name == subclass_post.class_name
                ]

                if student_pks[0] == "all":
                    for student in this_class_students:
                        classworkpost.students.add(student)
                else:
                    for student in this_class_students:
                        if str(student.pk) in student_pks:
                            classworkpost.students.add(student)

                post_category = request.POST.get("postcategory")

                if post_category == "textpost":
                    textpostbody = request.POST.get("textpostbody")
                    TextPost.objects.create(post=classworkpost, body=textpostbody)
                elif post_category == "videopost":
                    videopostbody = request.POST.get("videopostbody")
                    videopostfile = request.FILES["videopostfile"]
                    video_post = VideoPost.objects.create(
                        post=classworkpost,
                        body=videopostbody,
                    )
                    if not video_post.uploadable(file_tobe_uploaded=videopostfile):
                        video_post.delete()
                        classworkpost.delete()
                        err = (
                            "Your college has passed its total upload space limit. "
                            "You can no longer upload any files. "
                            "Please contact your college administrator regarding this"
                        )
                        messages.error(request, f"{err}")
                        return redirect(college_teacher_classroom, pk=college_class_pk)
                    video_post.video_url = videopostfile
                    video_post.save()
                    college.used_storage_space = college.used_storage_space + (
                        decimal.Decimal(video_post.video_url.size)
                        / (1024 * 1024 * 1024)
                    )
                    college.save()
                elif post_category == "documentpost":
                    documentpostbody = request.POST.get("documentpostbody")
                    documentpostfile = request.FILES["documentpostfile"]
                    document_post = DocumentPost.objects.create(
                        post=classworkpost,
                        body=documentpostbody,
                    )
                    if not document_post.uploadable(
                        file_tobe_uploaded=documentpostfile
                    ):
                        document_post.delete()
                        classworkpost.delete()
                        err = (
                            "Your college has passed its total upload space limit. "
                            "You can no longer upload any files. "
                            "Please contact your college administrator regarding this"
                        )
                        messages.error(request, f"{err}")
                        return redirect(college_teacher_classroom, pk=college_class_pk)
                    document_post.document_url = documentpostfile
                    document_post.save()
                    college.used_storage_space = college.used_storage_space + (
                        college.Decimal(document_post.document_url.size)
                        / (1024 * 1024 * 1024)
                    )
                    college.save()
                elif post_category == "imagepost":
                    imagepostbody = request.POST.get("imagepostbody")
                    imagepostfile = request.FILES["imagepostfile"]
                    image_post = ImagePost.objects.create(
                        post=classworkpost,
                        body=imagepostbody,
                    )
                    if not image_post.uploadable(file_tobe_uploaded=imagepostfile):
                        image_post.delete()
                        classworkpost.delete()
                        err = (
                            "Your college has passed its total upload space limit. "
                            "You can no longer upload any files. "
                            "Please contact your college administrator regarding this"
                        )
                        messages.error(request, f"{err}")
                        return redirect(college_teacher_classroom, pk=college_class_pk)
                    image_post.image_url = imagepostfile
                    image_post.save()
                    college.used_storage_space = college.used_storage_space + (
                        decimal.Decimal(image_post.image_url.size)
                        / (1024 * 1024 * 1024)
                    )
                    college.save()
                elif post_category == "youtubepost":
                    youtube_link = request.POST.get("youtubepostbody")
                    if youtube_link.count("watch?v=") != 0:
                        youtube_link = youtube_link.replace("watch?v=", "embed/")
                    YouTubePost.objects.create(
                        post=classworkpost, youtube_link=youtube_link
                    )
                elif post_category == "articlepost":
                    article_link = request.POST.get("articlepostbody")
                    ArticlePost.objects.create(
                        post=classworkpost, article_link=article_link
                    )

            elif postype == "classtest":
                is_assignment = False
                is_classtest = True

                classworkpost = ClassWorkPost.objects.create(
                    college=college,
                    class_name=subclass_post.class_name,
                    subclass=subclass_post,
                    subject=Subject.objects.get(pk=subject_pk),
                    teacher=request.user.teachermodel,
                    title=title,
                    is_assignment=is_assignment,
                    is_classtest=is_classtest,
                )

                # link students to this post
                this_class_students = [
                    student
                    for student in StudentModel.objects.all()
                    if student.sub_class == subclass_post
                    and student.class_name == subclass_post.class_name
                ]

                if student_pks[0] == "all":
                    for student in this_class_students:
                        classworkpost.students.add(student)
                else:
                    for student in this_class_students:
                        if str(student.pk) in student_pks:
                            classworkpost.students.add(student)

                classtestpostbody = request.POST.get("classtestpostbody")

                classtestpost = ClassTestPost.objects.create(
                    post=classworkpost, body=classtestpostbody
                )

                totalnoofquestions = int(request.POST.get("totalnoofquestions"))

                for i in range(1, (totalnoofquestions + 1)):
                    question = request.POST.get(f"q{i}")

                    question = Question.objects.create(
                        class_test_post=classtestpost, question=question
                    )

                    option1 = request.POST.get(f"q{i}o1")
                    option2 = request.POST.get(f"q{i}o2")
                    option3 = request.POST.get(f"q{i}o3")
                    option4 = request.POST.get(f"q{i}o4")

                    correct_ans = {
                        f"q{i}o1": option1,
                        f"q{i}o2": option2,
                        f"q{i}o3": option3,
                        f"q{i}o4": option4,
                    }

                    correct_option = correct_ans[request.POST.get(f"ans{i}")]

                    Choice.objects.create(
                        question=question,
                        choice=option1,
                        is_correct=(True if correct_option == option1 else False),
                    )

                    Choice.objects.create(
                        question=question,
                        choice=option2,
                        is_correct=(True if correct_option == option2 else False),
                    )

                    if option3 is not None:
                        Choice.objects.create(
                            question=question,
                            choice=option3,
                            is_correct=(True if correct_option == option3 else False),
                        )

                    if option4 is not None:
                        Choice.objects.create(
                            question=question,
                            choice=option4,
                            is_correct=(True if correct_option == option4 else False),
                        )
            return redirect(college_teacher_classroom)
        except Exception as err:
            messages.error(request, f"{err}")
            return redirect(college_teacher_classroom)


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def college_teacher_classroom_view_test(request, slug_pk):
    classtestpost = ClassTestPost.objects.get(post__slug=slug_pk)
    questions = [
        question
        for question in Question.objects.all()
        if question.class_test_post == classtestpost
    ]
    choices = [
        choice for choice in Choice.objects.all() if choice.question in questions
    ]

    context_dict = {
        "classtestpost": classtestpost,
        "questions": questions,
        "choices": choices,
    }
    return render(
        request,
        template_name="college/teacher/classroom/teacher_view_test.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def view_tests_submissions(request, class_pk=None):
    college_subclass = SubClass.objects.get(pk=class_pk)
    classworkposts = ClassWorkPost.objects.filter(
        class_name=college_subclass.class_name, subclass=college_subclass
    )
    classtestposts = [post for post in classworkposts if post.is_classtest]
    classtestposts = [
        post for post in ClassTestPost.objects.all() if post.post in classtestposts
    ]
    classtest_solutions = [
        post
        for post in ClassTestSolution.objects.all()
        if post.classtest in classtestposts
    ]

    context_dict = {
        "classtest_solutions": classtest_solutions,
    }
    return render(
        request,
        template_name="college/teacher/classroom/view_tests_submissions.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def view_assignments_submissions(request, class_pk=None):
    college_subclass = SubClass.objects.get(pk=class_pk)
    classworkposts = ClassWorkPost.objects.filter(
        class_name=college_subclass.class_name, subclass=college_subclass
    )
    assignment_posts = [post for post in classworkposts if post.is_assignment]
    assignment_solutions = [
        post
        for post in AssignmentSolution.objects.all()
        if post.post in assignment_posts
    ]

    context_dict = {
        "assignment_solutions": assignment_solutions,
    }
    return render(
        request,
        template_name="college/teacher/classroom/view_assignments_submissions.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def view_test_performance(request, slug_pk):
    classtestsolution = ClassTestSolution.objects.get(classtest__post__slug=slug_pk)
    student_choices = [
        choice
        for choice in StudentChoice.objects.all()
        if choice.classtestsolution == classtestsolution
    ]

    test_items = []

    for choice in student_choices:
        question = choice.question
        choices = Choice.objects.filter(question=question)
        selected_choice = choice.choice
        test_items.append(
            {
                "question": question,
                "choices": choices,
                "selected_choice": selected_choice,
            }
        )

    context_dict = {
        "classtestsolution": classtestsolution,
        "test_items": test_items,
    }
    return render(
        request,
        template_name="college/teacher/classroom/view_test_performance.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_teacher, login_url="home")
def college_teacher_classroom_delete_test(request, slug_pk):
    college = College.objects.first()
    post = None
    if request.method == "POST":
        try:
            post = ClassWorkPost.objects.get(slug=slug_pk)
        except Exception as err:
            return JsonResponse({"process": "failed", "msg": f"{err}"})

        try:
            videopost = VideoPost.objects.get(post=post)
            if videopost:
                college.used_storage_space = college.used_storage_space - (
                    decimal.Decimal(videopost.video_url.size) / (1024 * 1024 * 1024)
                )
                college.save()
        except Exception:
            pass

        try:
            documentpost = DocumentPost.objects.get(post=post)
            if documentpost:
                college.used_storage_space = college.used_storage_space - (
                    decimal.Decimal(documentpost.document_url.size)
                    / (1024 * 1024 * 1024)
                )
                college.save()
        except Exception:
            pass

        try:
            imagepost = ImagePost.objects.get(post=post)
            if imagepost:
                college.used_storage_space = college.used_storage_space - (
                    decimal.Decimal(imagepost.image_url.size) / (1024 * 1024 * 1024)
                )
                college.save()
        except Exception:
            pass

        post.delete()
        return JsonResponse({"process": "success", "msg": "Post successfully deleted"})

    return JsonResponse(
        {"process": "failed", "msg": "GET not supported by this endpoint"}
    )
