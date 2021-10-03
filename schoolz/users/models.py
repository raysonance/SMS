from datetime import datetime, timedelta
import random
import string
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils import text, timezone
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
    username = CharField(_("Username"), blank=True, max_length=255, unique=True)
    name = CharField(_("Name of User"), blank=True, max_length=255)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class FavourManager(BaseUserManager):
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


class AdminManager(FavourManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ADMIN)


class TeacherManager(FavourManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.TEACHER)


class StudentManager(FavourManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.STUDENT)


def rand_slug():
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(6)
    )


class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.ADMIN
            self.is_admin = True
        if not self.username:
            username = self.name + "-" + rand_slug()
            while Admin.objects.filter(username=username):
                username = self.name + "-" + rand_slug()
            self.username = username
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
    photo = models.ImageField(upload_to="adminfile/", null=True, blank=True)
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
        try:
            if self.photo.url:
                return f"{self.photo.url}"
        except Exception:
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
        if not self.username:
            username = self.name + "-" + rand_slug()
            while Teacher.objects.filter(username=username):
                username = self.name + "-" + rand_slug()
            self.username = username
        return super().save(*args, **kwargs)


class Student(User):
    objects = StudentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.STUDENT
            self.is_student = True
        if not self.username:
            username = self.name + "-" + rand_slug()
            while Student.objects.filter(username=username):
                username = self.name + "-" + rand_slug()
            self.username = username
        return super().save(*args, **kwargs)


class AdminMessages(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.ForeignKey("users.AdminModel", on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=50)
    sender_email = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    message = models.TextField()
    slug = models.SlugField(blank=True, max_length=255, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Admin Messages"

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = text.slugify(rand_slug() + "-" + self.title)
        super().save(*args, **kwargs)

    def was_published_recently(self):
        return self.updated_at >= timezone.now() - datetime.timedelta(days=30)

class Plan(models.Model):
    name = models.CharField(max_length=256)
    allotted_storage_space = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_month = models.DecimalField(max_digits=6, decimal_places=2)
    price_per_year = models.DecimalField(max_digits=6, decimal_places=2)
    upcoming_price_per_month = models.FloatField(null=True, blank=True)
    upcoming_price_per_year = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class College(models.Model):
    plan_subscribed = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    subscription_start_date = models.DateField(blank=True, null=True)
    subscription_end_date = models.DateField(blank=True, null=True)
    college_name = models.CharField(max_length=500)
    email = models.EmailField(max_length=256, unique=True)
    phone_no = models.CharField(max_length=13)
    card_info = models.CharField(max_length=16)
    signup_date = models.DateTimeField(auto_now_add=True)
    used_storage_space = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription_active = models.BooleanField(default=True)
    plan_cancelled_on = models.DateTimeField(blank=True, null=True)

    @property
    def name(self):
        return f'{self.college_name}'

    def __str__(self):
        return self.college_name

    def set_initial_subscription_dates(self):
        self.subscription_start_date = datetime.now().date()
        self.subscription_end_date = self.subscription_start_date + timedelta(days=365)

    def days_left(self):
        delta = self.subscription_end_date - datetime.now().date()
        return delta.days

    def renew(self, plan, card_info):
        # Only renew if days left is 15 or less
        if self.days_left() <= 15 or not self.subscription_active:
            self.plan_subscribed = plan
            self.card_info = card_info
            self.subscription_start_date = datetime.now().date()
            self.subscription_end_date = self.subscription_start_date + timedelta(days=365 + self.days_left())
            self.subscription_active = True
            self.plan_cancelled_on = None

    def plan_upgrade(self, new_plan):
        self.plan_subscribed = new_plan

    def cancel_plan(self):
        self.subscription_start_date = None
        self.subscription_end_date = datetime.now().date()
        self.subscription_active = False
        self.plan_cancelled_on = datetime.now()
