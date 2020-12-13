from django.db import models
from django.urls import reverse

# Create your models here.


class Class(models.Model):
    class_name = models.CharField(max_length=20)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.class_name


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    session_name = models.CharField(max_length=20)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.session_name


class TeacherModel(models.Model):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, primary_key=True
    )
    name = models.CharField("Full Name", max_length=150, default="wannabe")
    photo = models.ImageField(upload_to="teacherfile/")
    date_of_birth = models.DateField(blank=True, null=True)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=11, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["joining_date", "name"]

    def __str__(self):
        return "{} ({})".format(self.name, self.class_name)

    def get_absolute_url(self):
        return reverse("teachers:dash", args=None)
