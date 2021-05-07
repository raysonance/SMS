import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from teachers.models import Section


class User(AbstractUser):
    """Default user for Schoolz."""

    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Types(models.TextChoices):
        ADMIN = "Admin", "ADMIN"
        TEACHER = "Teacher", "TEACHER"
        STUDENT = "Student", "STUDENT"

    type = models.CharField(
        _("Type"), max_length=50, choices=Types.choices, default=Types.STUDENT
    )

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class AdminManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have a valid email.")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ADMIN)


class TeacherManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have a valid email.")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.TEACHER)


class StudentManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have a valid email.")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.STUDENT)


class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.ADMIN
            self.is_admin = True
        return super().save(*args, **kwargs)


class AdminModel(models.Model):
    uuid = models.UUIDField(
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, primary_key=True
    )
    name = models.CharField("Full Name", max_length=150)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to="adminfile/")
    date_of_birth = models.DateField(blank=True, null=True)
    mobile = models.CharField(max_length=11, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(default="reddit")
    joining_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return "{} ({})".format(self.name, self.section)

    @property
    def get_photo_url(self):
        return f"{settings.MEDIA_URL}{self.photo}"

    def get_absolute_url(self):
        return reverse("teachers:dash", args=None)


class Teacher(User):
    objects = TeacherManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.TEACHER
            self.is_teacher = True
        return super().save(*args, **kwargs)


class Student(User):
    objects = StudentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.STUDENT
            self.is_student = True
        return super().save(*args, **kwargs)
