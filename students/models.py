import datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone

from teachers.models import Class, Session, SubClass, TeacherModel

# Create your models here.


class StudentModel(models.Model):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, primary_key=True
    )
    name = models.CharField("Full Name", max_length=100)
    photo = models.ImageField(upload_to="studentsfile/")
    class_name = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    sub_class = models.ForeignKey(
        SubClass, on_delete=models.SET_NULL, null=True, default=1
    )
    fathers_name = models.CharField("Father's Name", max_length=100)
    mothers_name = models.CharField("Mother's Name", max_length=100)
    date_of_birth = models.DateField("Birth Date", blank=True, null=True)
    email = models.EmailField("Email Address")
    address = models.TextField()
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

    def get_absolute_url(self):
        return reverse("teachers:dash", args=None)


class StudentMessages(models.Model):
    teacher = models.ForeignKey(TeacherModel, on_delete=models.CASCADE, default=1)
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField()
    private = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"

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
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL, null=True, default=1
    )
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, default=1)
    first_test = models.IntegerField()
    second_test = models.IntegerField()
    third_test = models.IntegerField()
    fourth_test = models.IntegerField()
    exam_score = models.IntegerField()
    total_score = models.IntegerField()
    grade = models.CharField(max_length=10)
    remark = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {}".format(self.subject, self.student)
