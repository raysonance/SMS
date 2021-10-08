import decimal
import random
import string
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import text, timezone

from teachers.models import Class, Section, Session, SubClass, TeacherModel

# Create your models here.


class StudentModel(models.Model):
    uuid = models.UUIDField(
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, primary_key=True
    )
    name = models.CharField("Full Name", max_length=100)
    photo = models.ImageField(upload_to="studentsfile/", blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    class_name = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    sub_class = models.ForeignKey(
        SubClass,
        on_delete=models.SET_NULL,
        null=True,
    )
    paid = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    fathers_name = models.CharField("Father's Name", max_length=100)
    mothers_name = models.CharField("Mother's Name", max_length=100)
    date_of_birth = models.DateField("Birth Date", null=True, blank=True)
    email = models.EmailField("Email Address", blank=True)
    address = models.TextField(blank=True)
    emergency_mobile_number = models.CharField("Mobile Number", max_length=11)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="+", null=True
    )
    updated_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="+", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return "{} {}".format(self.name, self.class_name)

    @property
    def get_photo_url(self):
        try:
            if self.photo.url:
                return f"{self.photo.url}"
        except Exception:
            return f"{settings.MEDIA_URL}{self.photo}"

    def get_absolute_url(self):
        try:
            if self.user.is_teacher:
                return reverse("teachers:dash", args=None)
            else:
                return reverse("users:dash", args=None)
        except Exception:
            return reverse("users:dash", args=None)


def rand_slug():
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(6)
    )


class StudentMessages(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(TeacherModel, on_delete=models.CASCADE, default=1)
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=50)
    message = models.TextField()
    private = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, max_length=255, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name_plural = "Student Messages"

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = text.slugify(rand_slug() + "-" + self.title)
        super().save(*args, **kwargs)

    def was_published_recently(self):
        return self.updated_at >= timezone.now() - timedelta(days=30)


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject_name


class SubjectResult(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL, null=True, default=1
    )
    class_name = models.ForeignKey(
        Class, null=True, on_delete=models.SET_NULL, default=1
    )
    sub_class = models.ForeignKey(
        SubClass, null=True, on_delete=models.SET_NULL, default=2
    )
    first_test = models.IntegerField()
    second_test = models.IntegerField()
    third_test = models.IntegerField()
    fourth_test = models.IntegerField()
    exam_score = models.IntegerField()
    total_score = models.IntegerField()
    grade = models.CharField(max_length=3)
    remark = models.CharField(max_length=20)
    pin = models.BooleanField(default=False)
    teachers_comment = models.CharField(max_length=100, null=True)
    head_teacher_comment = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {}".format(self.subject, self.student)


class Code(models.Model):
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, default=1)
    number = models.IntegerField(null=True)
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )

    def __str__(self):
        return f"number: {self.number}"


class ClassWorkPost(models.Model):
    college = models.ForeignKey("users.College", on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subclass = models.ForeignKey(SubClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherModel, on_delete=models.CASCADE)
    students = models.ManyToManyField(StudentModel, blank=True)
    title = models.CharField(max_length=256)
    is_assignment = models.BooleanField(default=False)
    is_classtest = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["date"]


class TextPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.post.title


def video_directory_path(instance, filename):
    # this will return a file path that is unique for all the users
    # file will be uploaded to MEDIA_ROOT/user_id/videos/filename
    return f"video_{instance.post.pk}/videos/{instance.post.pk}/{filename}"


class VideoPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)
    video_url = models.FileField(upload_to=video_directory_path, blank=True, null=True)

    def __str__(self):
        return self.post.title

    @property
    def get_media_url(self):
        return f"{settings.MEDIA_URL}{self.video_url}"

    def uploadable(self, file_tobe_uploaded):
        allotted_storage_space = (
            self.post.college.plan_subscribed.allotted_storage_space
        )
        used_storage_space = self.post.college.used_storage_space
        if (
            decimal.Decimal(file_tobe_uploaded.size / (1024 * 1024 * 1024))
            + used_storage_space
            > allotted_storage_space
        ):
            return False
        return True


def document_directory_path(instance, filename):
    # this will return a file path that is unique for all the users
    # file will be uploaded to MEDIA_ROOT/user_id/documents/filename
    return f"document_{instance.post.pk}/videos/{instance.post.pk}/{filename}"


class DocumentPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)
    document_url = models.FileField(
        upload_to=document_directory_path, blank=True, null=True
    )

    def __str__(self):
        return self.post.title

    @property
    def get_media_url(self):
        return f"{settings.MEDIA_URL}{self.document_url}"

    def uploadable(self, file_tobe_uploaded):
        allotted_storage_space = (
            self.post.college.plan_subscribed.allotted_storage_space
        )
        used_storage_space = self.post.college.used_storage_space
        print("NO")
        if (
            decimal.Decimal(file_tobe_uploaded.size / (1024 * 1024 * 1024))
            + used_storage_space
            > allotted_storage_space
        ):
            return False
        return True


def image_directory_path(instance, filename):
    # this will return a file path that is unique for all the users
    # file will be uploaded to MEDIA_ROOT/user_id/images/filename
    return f"image_{instance.post.pk}/videos/{instance.post.pk}/{filename}"


class ImagePost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)
    image_url = models.ImageField(upload_to=image_directory_path, blank=True, null=True)

    def __str__(self):
        return self.post.title

    @property
    def get_media_url(self):
        return f"{settings.MEDIA_URL}{self.image_url}"

    def uploadable(self, file_tobe_uploaded):
        allotted_storage_space = (
            self.post.college.plan_subscribed.allotted_storage_space
        )
        used_storage_space = self.post.college.used_storage_space
        print("NO")
        if (
            decimal.Decimal(file_tobe_uploaded.size / (1024 * 1024 * 1024))
            + used_storage_space
            > allotted_storage_space
        ):
            return False
        return True


class YouTubePost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    youtube_link = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.post.title


class ArticlePost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    article_link = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.post.title


class PostComment(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, default=None)
    is_teacher = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    marked_as_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.post.title


class CommentReply(models.Model):
    postcomment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, default=None)
    is_teacher = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    marked_as_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.postcomment.post.title


class ClassTestPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.post.title


class Question(models.Model):
    class_test_post = models.ForeignKey(ClassTestPost, on_delete=models.CASCADE)
    question = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.question


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=256, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.question} {self.choice}"


class ClassTestSolution(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    classtest = models.ForeignKey(ClassTestPost, on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, null=True)
    total_marks = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} {self.score}"


class StudentChoice(models.Model):
    classtestsolution = models.ForeignKey(ClassTestSolution, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    @property
    def is_correct(self):
        return self.choice.is_correct

    def __str__(self):
        return f"{self.question.question} {self.choice}"


def file_directory_path(instance, filename):
    # this will return a file path that is unique for all the users
    # file will be uploaded to MEDIA_ROOT/user_id/images/filename
    return f"image_{instance.post.pk}/assignments/{instance.post.pk}/{filename}"


class AssignmentSolution(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    file_url = models.FileField(upload_to=file_directory_path, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title}: {self.student.name} | Submitted @ {self.date}"

    @property
    def get_media_url(self):
        return f"{settings.MEDIA_URL}{self.file_url}"

    def uploadable(self, file_tobe_uploaded):
        allotted_storage_space = (
            self.post.college.plan_subscribed.allotted_storage_space
        )
        used_storage_space = self.post.college.used_storage_space
        print("NO")
        if (
            decimal.Decimal(file_tobe_uploaded.size / (1024 * 1024 * 1024))
            + used_storage_space
            > allotted_storage_space
        ):
            return False
        return True
