import datetime
import random
import string

from django.db import models
from django.urls import reverse
from django.utils import text, timezone

# Create your models here.


class Section(models.Model):
    id = models.AutoField(primary_key=True)
    sections = models.CharField(max_length=50)

    def __str__(self):
        return self.sections


class Class(models.Model):
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, default=1)
    class_name = models.CharField(max_length=50)

    class Meta:
        ordering = ["pk"]
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.class_name


class SubClass(models.Model):
    id = models.AutoField(primary_key=True)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    sub_class = models.CharField(max_length=50)

    class Meta:
        ordering = ["pk"]
        verbose_name_plural = "Subclasses"

    def __str__(self):
        return f"{self.sub_class} of {self.class_name}"


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    session_name = models.CharField(max_length=20)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.session_name


class TeacherModel(models.Model):
    uuid = models.UUIDField(
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, primary_key=True
    )
    name = models.CharField("Full Name", max_length=150, default="wannabe")
    photo = models.ImageField(upload_to="teacherfile/")
    date_of_birth = models.DateField(blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    class_name = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    sub_class = models.ForeignKey(
        SubClass, on_delete=models.SET_NULL, null=True, default=1
    )
    address = models.TextField(default="clouds")
    mobile = models.CharField(max_length=11, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["joining_date", "name"]

    def __str__(self):
        return "{} ({})".format(self.name, self.class_name)

    def get_absolute_url(self):
        return reverse("users:dash", args=None)


def rand_slug():
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(6)
    )


class TeacherMessages(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.ForeignKey("users.AdminModel", on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherModel, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=50)
    message = models.TextField()
    private = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, max_length=255, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Teacher Messages"

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = text.slugify(rand_slug() + "-" + self.title)
        super().save(*args, **kwargs)

    def was_published_recently(self):
        return self.updated_at >= timezone.now() - datetime.timedelta(days=30)
