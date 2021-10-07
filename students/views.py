import decimal
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from schoolz.users.decorators import (
    admin_required,
    teacher_admin_student,
    teacher_required,
    teacher_student,
    user_is_student,
)
from schoolz.users.models import College, Student
from teachers.models import Class, Session, SubClass, TeacherModel
from teachers.views import user_is_teacher

from .forms import StudentAdminSignUpForm, StudentModelForm, StudentSignUpForm
from .models import (
    ArticlePost,
    AssignmentSolution,
    Choice,
    ClassTestPost,
    ClassTestSolution,
    ClassWorkPost,
    Code,
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

# todo: add function for adminmodel, teachermodel, studentmodel


# for loading sub_class according to equivalent Class using ajax
def load_sub_class(request):
    class_id = request.GET.get("class")
    sub_class = SubClass.objects.filter(class_name=class_id).order_by("sub_class")

    context = {"sub_class": sub_class}
    return render(request, "others/subclass_dropdown_list_options.html", context)


# function for ajax changing of user payment field
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
    else:
        return render(request, "403.html")


# signup of students for teachers
@method_decorator([teacher_required], name="dispatch")
class StudentSignupView(LoginRequiredMixin, CreateView):
    model = Student
    login_url = "account_login"
    form_class = StudentSignUpForm
    template_name = "student/signup.html"

    def get_form_kwargs(self):
        kwargs = super(StudentSignupView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})  # adds self.request.user to form
        kwargs.update({"request": self.request})  # adds self.request to form
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
        kwargs["forms"] = self.form2  # to add second form to sign up html page
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
        # preloaded so they wouldn't to called continually
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
            # set paid field to false if  class is changed
            if "class_name" in form.changed_data:
                self.object.paid = False
            # set active to false if class or sub_class is changed, student wont appear in promotion page
            if "class_name" or "sub_class" in form.changed_data:
                self.object.active = False

            if "email" in form.changed_data:
                try:
                    student = Student.objects.get(pk=self.object.pk)
                    student.email = self.object.email
                    student.save()
                except Exception as err:
                    messages.error(self.request, f"{err}")
                    return super().form_invalid(form)
            if "name" in form.changed_data:
                try:
                    student = Student.objects.get(pk=self.object.pk)
                    student.name = self.object.name
                    student.save()
                except Exception as err:
                    messages.error(self.request, f"{err}")
                    return super().form_invalid(form)
            form.save()
            messages.success(self.request, "Student has been updated")
            return super().form_valid(form)

    def get_success_url(self):
        return reverse("students:profile", args=[self.object.uuid])


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
        "address",
        "emergency_mobile_number",
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        if "name" in form.changed_data:
            try:
                student = Student.objects.get(pk=self.object.pk)
                student.name = self.object.name
                student.save()
            except Exception as err:
                messages.error(self.request, f"{err}")
                return super().form_invalid(form)
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_student:
            messages.success(self.request, "Updated!")
            return reverse_lazy("students:dash")
        else:
            messages.success(self.request, "Student has been updated")
            return reverse_lazy("students:student_teacher_list")


# student list for teachers
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def student_teacher_list(request):
    students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
        active=True,
    ).values("pk", "name", "emergency_mobile_number", "uuid", "paid")
    inactive_students = StudentModel.objects.filter(
        class_name=request.user.teachermodel.class_name_id,
        sub_class=request.user.teachermodel.sub_class_id,
        active=False,
    ).values("pk", "name", "emergency_mobile_number", "uuid", "paid")

    context = {"students": students, "inactive": inactive_students}

    return render(request, "student/student_list.html", context)


# function to make students active
@login_required
@user_passes_test(user_is_teacher, login_url="home")
def active(request, uuid_key):
    try:
        student = get_object_or_404(StudentModel, uuid=uuid_key)
        student.active = True
        student.save()
        messages.success(request, f"{student.name} has been made active")
        return redirect("students:student_teacher_list")
    except Exception as err:
        messages.error(request, f"{err}")
        return redirect("students:student_teacher_list")


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
class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = "student/student_delete.html"
    login_url = "account_login"
    context_object_name = "students"
    slug_field = "uuid"
    slug_url_kwarg = "uuid_pk"

    def get_success_url(self):
        messages.success(self.request, "Student has been deleted!")
        return reverse_lazy("users:show_list")


# student dashboard
@login_required
@user_passes_test(user_is_student, login_url="home")
def student_dashboard(request):
    class_name = int(request.user.studentmodel.class_name_id)
    sub_class = int(request.user.studentmodel.sub_class_id)
    total_student = StudentModel.objects.filter(
        class_name=class_name,
        sub_class=sub_class,
    ).count()
    teachers = TeacherModel.objects.filter(
        class_name=class_name,
        sub_class=sub_class,
    )
    courses = Subject.objects.filter(
        class_name=class_name,
    ).count()

    sub_class = SubClass.objects.filter(id=sub_class).values(
        "class_name__class_name", "sub_class"
    )
    # contains the three most recent messages and if all are created or updated
    # more than a 30 day timeframe then the list would be empty
    three_message = [
        x
        for x in StudentMessages.objects.filter(student=request.user.studentmodel)[:3]
        if x.was_published_recently()
    ]

    context = {
        "student": total_student,
        "teachers": teachers,
        "courses": courses,
        "sub_class": sub_class,
        "message": three_message,
    }
    return render(request, "student/student_dashboard.html", context)


# for pin checking in result
def result_pin(request, class_id, session_id):
    if request.method == "POST":
        try:
            pin = request.POST.get("pin")
            if Code.objects.filter(
                uuid=pin, section=request.user.studentmodel.section_id
            ):
                student_result = SubjectResult.objects.filter(
                    student=request.user.pk, session=session_id, class_name=class_id
                )
                for result in student_result:
                    result.pin = True
                    result.save()
                code = Code.objects.get(uuid=pin)
                code.delete()
                messages.success(request, "Pin Correct! Result can now be viewed!")
                return redirect("students:show_result")
            else:
                messages.error(request, "Pin incorrect")
                return redirect(
                    "students:pin", class_id=class_id, session_id=session_id
                )
        except Exception as err:
            messages.error(request, f"Failed! {err}")
            return redirect("students:show_result")
    return render(request, "student/pin.html")


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
            if student_result[0].pin:
                first = student_result[0].session.session_name
                # checks either to be promoted to next session or next class
                if student_result[0].session != Session.objects.last():
                    promote_session = get_object_or_404(
                        Session, pk=student_result[0].session.id + 1
                    ).session_name
                else:
                    promote_session = get_object_or_404(
                        Class, pk=student_result[0].class_name.pk + 1
                    ).class_name
                # calculates the total percentage
                normal_total, student_total = 0, 0
                for result in student_result:
                    normal_total += 100
                    student_total += result.total_score
                percentage = (student_total / normal_total) * 100

                # checks for teacher comment in all filtered subject results
                for comments in student_result:
                    if comments.teachers_comment:
                        comment = comments.teachers_comment
                        break
                    else:
                        comment = "No comment has been inputted for this student."

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
                messages.error(request, "This result has not been paid for.")
                return redirect(
                    "students:pin", class_id=class_id, session_id=session_id
                )
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
        if len(str(query)) < 3:
            messages.error(request, "Search character's length must be three or more!")
            return render(request, "student/search_all.html")
        student = StudentModel.objects.filter(
            Q(name__icontains=query) | Q(class_name__class_name__icontains=query)
        ).select_related("class_name", "sub_class")
        teacher = TeacherModel.objects.filter(
            Q(name__icontains=query) | Q(class_name__class_name__icontains=query)
        ).select_related("class_name", "sub_class")
        context = {"students": student, "teachers": teacher}
        return render(request, "student/search_all.html", context)


# classroom


@login_required
@user_passes_test(user_is_student, login_url="home")
def college_student(request):
    subclass_id = request.user.studentmodel.sub_class_id
    subclass = SubClass.objects.get(id=subclass_id)
    try:
        subjects = Subject.objects.filter(
            class_name=subclass.class_name,
        )
    except Exception as err:
        messages.error(request, f"{err}")
        context_dict = {
            "college_class": None,
        }
        return render(
            request,
            template_name="college/student/classroom/student_classroom.html",
            context=context_dict,
        )

    posts = ClassWorkPost.objects.filter(subclass_id=subclass_id)
    textposts = TextPost.objects.filter(post__subclass_id=subclass_id)
    videoposts = VideoPost.objects.filter(post__subclass_id=subclass_id)
    documentposts = DocumentPost.objects.filter(post__subclass_id=subclass_id)
    imageposts = ImagePost.objects.filter(post__subclass_id=subclass_id)
    youtubeposts = YouTubePost.objects.filter(post__subclass_id=subclass_id)
    articleposts = ArticlePost.objects.filter(post__subclass_id=subclass_id)
    classtestposts = ClassTestPost.objects.filter(post__subclass_id=subclass_id)

    posts_display = []

    # These loops are necessary to maintain the order of the posts (by datetime of post)
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
        "college_class": subclass,
        "subjects": subjects,
        "posts_display": posts_display,
        "comments_and_replies": comments_and_replies,
    }

    return render(
        request,
        template_name="college/student/classroom/student_classroom.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_student, login_url="home")
def college_student_assignments(request):
    college_subclass = request.user.studentmodel.sub_class
    try:
        subjects = [
            subject
            for subject in Subject.objects.all()
            if subject.class_name == college_subclass.class_name
        ]
    except Exception as err:
        messages.error(request, f"{err}")
        context_dict = {
            "college_class": None,
        }
        return render(
            request,
            template_name="college/student/classroom/student_classroom.html",
            context=context_dict,
        )

    posts = [
        post
        for post in ClassWorkPost.objects.all()
        if post.subclass == college_subclass and post.is_assignment
    ]
    textposts = [
        textpost for textpost in TextPost.objects.all() if textpost.post in posts
    ]
    videoposts = [
        videopost for videopost in VideoPost.objects.all() if videopost.post in posts
    ]
    documentposts = [
        documentpost
        for documentpost in DocumentPost.objects.all()
        if documentpost.post in posts
    ]
    imageposts = [
        imagepost for imagepost in ImagePost.objects.all() if imagepost.post in posts
    ]
    youtubeposts = [
        youtubepost
        for youtubepost in YouTubePost.objects.all()
        if youtubepost.post in posts
    ]
    articleposts = [
        articlepost
        for articlepost in ArticlePost.objects.all()
        if articlepost.post in posts
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

    context_dict = {
        "college_class": college_subclass,
        "subjects": subjects,
        "posts_display": posts_display,
    }

    return render(
        request,
        template_name="college/student/classroom/college_student_assignments.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_student, login_url="home")
def college_student_submit_assignment(request, pk=None):
    post = ClassWorkPost.objects.get(pk=pk)
    college = College.objects.first()
    assignment_solution = None
    try:
        assignment_solution = AssignmentSolution.objects.get(
            post=post, student=request.user.studentmodel
        )
    except Exception:
        pass

    if request.method == "POST":
        assignment_solution = AssignmentSolution.objects.create(
            student=request.user.studentmodel,
            post=post,
        )
        if assignment_solution.uploadable(
            file_tobe_uploaded=request.FILES["assignment_file"]
        ):
            assignment_solution.file_url = request.FILES["assignment_file"]
            assignment_solution.save()
            college.used_storage_space += decimal.Decimal(
                (assignment_solution.file_url.size / (1024 * 1024 * 1024))
            )
            college.save()
            return redirect(college_student)

        assignment_solution.delete()

        err = (
            "Your college has passed its total upload space limit. "
            "You can no longer upload any files. "
            "Please contact your college administrator regarding this"
        )
        messages.error(request, f"{err}")
        return redirect(college_student)

    try:
        textpost = TextPost.objects.get(post=post)
        context_dict = {
            "post": textpost,
            "assignment_solution": assignment_solution,
        }
        return render(
            request,
            template_name="college/student/classroom/college_student_submit_assignment.html",
            context=context_dict,
        )
    except Exception:
        pass

    try:
        videopost = VideoPost.objects.get(post=post)
        context_dict = {
            "post": videopost,
            "assignment_solution": assignment_solution,
        }
        return render(
            request,
            template_name="college/student/classroom/college_student_submit_assignment.html",
            context=context_dict,
        )
    except Exception:
        pass

    try:
        documentpost = DocumentPost.objects.get(post=post)
        context_dict = {
            "post": documentpost,
            "assignment_solution": assignment_solution,
        }
        return render(
            request,
            template_name="college/student/classroom/college_student_submit_assignment.html",
            context=context_dict,
        )
    except Exception:
        pass

    try:
        imagepost = ImagePost.objects.get(post=post)
        context_dict = {
            "post": imagepost,
            "assignment_solution": assignment_solution,
        }
        return render(
            request,
            template_name="college/student/classroom/college_student_submit_assignment.html",
            context=context_dict,
        )
    except Exception:
        pass

    try:
        youtubepost = YouTubePost.objects.get(post=post)
        context_dict = {
            "post": youtubepost,
            "assignment_solution": assignment_solution,
        }
        return render(
            request,
            template_name="college/student/classroom/college_student_submit_assignment.html",
            context=context_dict,
        )
    except Exception:
        pass

    try:
        articlepost = ArticlePost.objects.get(post=post)
        context_dict = {
            "post": articlepost,
            "assignment_solution": assignment_solution,
        }
        return render(
            request,
            template_name="college/student/classroom/college_student_submit_assignment.html",
            context=context_dict,
        )
    except Exception:
        pass

    context_dict = {
        "post": None,
        "assignment_solution": None,
    }
    return render(
        request,
        template_name="college/student/classroom/college_student_submit_assignment.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_student, login_url="home")
def college_student_reading_materials(request):
    college_subclass = request.user.studentmodel.sub_class

    try:
        subjects = [
            subject
            for subject in Subject.objects.all()
            if subject.class_name == college_subclass.class_name
        ]
    except Exception as err:
        messages.error(request, f"{err}")
        context_dict = {
            "college_class": None,
        }
        return render(
            request,
            template_name="college/student/classroom/student_classroom.html",
            context=context_dict,
        )

    posts = [
        post
        for post in ClassWorkPost.objects.all()
        if post.subclass == college_subclass
    ]
    textposts = [
        textpost for textpost in TextPost.objects.all() if textpost.post in posts
    ]
    documentposts = [
        documentpost
        for documentpost in DocumentPost.objects.all()
        if documentpost.post in posts
    ]

    posts_display = []

    for post in posts:
        for textpost in textposts:
            if textpost.post == post:
                posts_display.insert(0, textpost)
        for documentpost in documentposts:
            if documentpost.post == post:
                posts_display.insert(0, documentpost)

    context_dict = {
        "college_class": college_subclass,
        "subjects": subjects,
        "posts_display": posts_display,
    }

    return render(
        request,
        template_name="college/student/classroom/college_student_reading_materials.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_student, login_url="home")
def college_student_videos(request):
    college_subclass = request.user.studentmodel.sub_class

    try:
        subjects = [
            subject
            for subject in Subject.objects.all()
            if subject.class_name == college_subclass.class_name
        ]
    except Exception as err:
        messages.error(request, f"{err}")
        context_dict = {
            "college_class": None,
        }
        return render(
            request,
            template_name="college/student/classroom/student_classroom.html",
            context=context_dict,
        )

    posts = [
        post
        for post in ClassWorkPost.objects.all()
        if post.subclass == college_subclass
    ]
    videoposts = [
        videopost for videopost in VideoPost.objects.all() if videopost.post in posts
    ]
    youtubeposts = [
        youtubepost
        for youtubepost in YouTubePost.objects.all()
        if youtubepost.post in posts
    ]

    posts_display = []

    for post in posts:
        for videopost in videoposts:
            if videopost.post == post:
                posts_display.insert(0, videopost)
        for youtubepost in youtubeposts:
            if youtubepost.post == post:
                posts_display.insert(0, youtubepost)

    context_dict = {
        "college_class": college_subclass,
        "subjects": subjects,
        "posts_display": posts_display,
    }

    return render(
        request,
        template_name="college/student/classroom/college_student_videos.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_student, login_url="home")
def college_student_articles(request):
    college_subclass = request.user.studentmodel.sub_class

    try:
        subjects = [
            subject
            for subject in Subject.objects.all()
            if subject.class_name == college_subclass.class_name
        ]
    except Exception as err:
        messages.error(request, f"{err}")
        context_dict = {
            "college_class": None,
        }
        return render(
            request,
            template_name="college/student/classroom/student_classroom.html",
            context=context_dict,
        )

    posts = [
        post
        for post in ClassWorkPost.objects.all()
        if post.subclass == college_subclass
    ]
    articleposts = [
        articlepost
        for articlepost in ArticlePost.objects.all()
        if articlepost.post in posts
    ]

    posts_display = []

    for post in posts:
        for articlepost in articleposts:
            if articlepost.post == post:
                posts_display.insert(0, articlepost)

    context_dict = {
        "college_class": college_subclass,
        "subjects": subjects,
        "posts_display": posts_display,
    }

    return render(
        request,
        template_name="college/student/classroom/college_student_articles.html",
        context=context_dict,
    )


@login_required
@user_passes_test(user_is_student, login_url="home")
def college_student_classroom_give_test(request, pk=None):
    if request.method == "POST":
        # This request is for submitting a classtest
        data = json.loads(request.body)
        classtestpost_id = data["classtestpost_id"]
        qans = data["qans"]

        score = 0
        total_marks = len(qans)

        try:
            classtestpost = ClassTestPost.objects.get(pk=classtestpost_id)

            classtestsolution = ClassTestSolution.objects.create(
                student=request.user.studentmodel,
                classtest=classtestpost,
                score=score,
                total_marks=total_marks,
            )

            for key, value in qans.items():
                student_choice = StudentChoice.objects.create(
                    classtestsolution=classtestsolution,
                    student=request.user.studentmodel,
                    question=Question.objects.get(pk=key),
                    choice=Choice.objects.get(pk=value),
                )

                if student_choice.is_correct:
                    score += 1

            classtestsolution.score = score
            classtestsolution.save()

            return JsonResponse(
                {"process": "success", "msg": "Post successfully deleted"}
            )
        except Exception as err:
            return JsonResponse({"process": "failed", "msg": f"{err}"})

    classtestpost = ClassTestPost.objects.get(pk=pk)

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

    try:
        classtestsolution = ClassTestSolution.objects.get(
            student=request.user.studentmodel,
            classtest=classtestpost,
        )
        context_dict["classtestsolution"] = classtestsolution
    except Exception:
        context_dict["classtestsolution"] = None

    return render(
        request,
        template_name="college/student/classroom/student_give_test.html",
        context=context_dict,
    )


@login_required
@user_passes_test(teacher_student, login_url="home")
def college_teacher_student_account(request):
    return render(request, template_name="college/teacher_student_account.html")


@login_required
@user_passes_test(teacher_student, login_url="home")
def college_student_classroom_view_post(request, pk=None):
    textpost = TextPost.objects.get(pk=pk)

    context_dict = {
        "textpost": textpost,
    }
    return render(
        request, template_name="college/classroom_view_post.html", context=context_dict
    )


@login_required
@user_passes_test(teacher_student, login_url="home")
def college_classroom_post_comment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data["post_id"]
        comment = data["comment"]

        try:
            if request.user.teachermodel:
                is_teacher = True
            else:
                is_teacher = True

        except Exception:
            is_teacher = False

        try:
            classworkpost = ClassWorkPost.objects.get(pk=post_id)
            postcomment = PostComment.objects.create(
                post=classworkpost,
                comment=comment,
                author=request.user,
                is_teacher=is_teacher,
            )
        except Exception as err:
            return JsonResponse({"process": "failed", "msg": f"{err}"})

        return JsonResponse(
            {
                "process": "success",
                "comment_id": postcomment.pk,
                "author": f"{postcomment.author.first_name} {postcomment.author.last_name}",
                "comment": f"{postcomment.comment}",
                "is_teacher": f"{postcomment.is_teacher}",
                "date": f"{postcomment.date}",
                "msg": "Comment successfully posted",
            }
        )

    return JsonResponse({"process": "failed", "msg": "GET method not supported"})


@login_required
@user_passes_test(teacher_student, login_url="home")
def college_classroom_post_reply(request):
    if request.method == "POST":
        data = json.loads(request.body)
        comment_id = data["comment_id"]
        replied_to = data["replied_to"]

        # This escaping is must because it is marked safe in templates for <b>reply_to_username</b> to display
        # without escaping.
        comment = escape(data["comment"])
        comment = f"{replied_to} {comment}"

        try:
            if request.user.teachermodel:
                is_teacher = True
            else:
                is_teacher = True
        except Exception:
            is_teacher = False

        try:
            postcomment = PostComment.objects.get(pk=comment_id)
            commentreply = CommentReply.objects.create(
                postcomment=postcomment,
                comment=comment,
                author=request.user,
                is_teacher=is_teacher,
            )
        except Exception as err:
            return JsonResponse({"process": "failed", "msg": f"{err}"})

        return JsonResponse(
            {
                "process": "success",
                "comment_id": commentreply.postcomment.pk,
                "author": f"{commentreply.author.username}",
                "comment": f"{commentreply.comment}",
                "is_teacher": f"{commentreply.is_teacher}",
                "date": f"{commentreply.date}",
                "msg": "Reply successfully posted",
            }
        )

    return JsonResponse({"process": "failed", "msg": "GET method not supported"})


@login_required
@user_passes_test(teacher_student, login_url="home")
def delete_comment_or_reply(request, pk=None):
    if request.method == "POST":
        data = json.loads(request.body)
        comment_id = data["comment_id"]
        reply_id = data["reply_id"]

        if reply_id is None:
            # This request is for deleting a comment
            try:
                comment = PostComment.objects.get(pk=comment_id)
                comment.marked_as_deleted = True
                comment.save()
                return JsonResponse(
                    {"process": "success", "msg": "Comment deleted successfully"}
                )
            except Exception as err:
                return JsonResponse({"process": "failed", "msg": f"{err}"})
        else:
            # This request is for deleting a reply
            try:
                reply = CommentReply.objects.get(pk=reply_id)
                reply.marked_as_deleted = True
                reply.save()
                return JsonResponse(
                    {"process": "success", "msg": "Reply deleted successfully"}
                )
            except Exception as err:
                return JsonResponse({"process": "failed", "msg": f"{err}"})

    return JsonResponse({"process": "failed", "msg": "GET method not supported"})


def payment_failed(request):
    return render(request, template_name="payment_failed.html")
