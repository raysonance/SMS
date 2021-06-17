import datetime
import random
import string
import uuid

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
        return self.updated_at >= timezone.now() - datetime.timedelta(days=30)


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
