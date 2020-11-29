from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

# Create your models here.
User = get_user_model()


class Class(models.Model):
    class_name = models.CharField(max_length=20)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.class_name


class Teacher(models.Model):
    name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to="teachers", default="teacheravatar.jpg")
    date_of_birth = models.DateField(blank=True, null=True)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=11, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        ordering = ["joining_date", "name"]

    def __str__(self):
        return "{} ({})".format(self.name, self.class_name)

    def get_absolute_url(self):
        return reverse("home", args=None)
