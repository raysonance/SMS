from django.db import models
from django.urls import reverse

from teachers.models import Class

# Create your models here.


class StudentModel(models.Model):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, primary_key=True
    )
    name = models.CharField("Full Name", max_length=100)
    photo = models.ImageField(upload_to="studentsfile/")
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    fathers_name = models.CharField("Father's Name", max_length=100)
    mothers_name = models.CharField("Mother's Name", max_length=100)
    date_of_birth = models.DateField("Birth Date", blank=True, null=True)
    email = models.EmailField("Email Address")
    address = models.TextField()
    emergency_mobile_number = models.CharField("Mobile Number", max_length=11)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="+", blank=True, null=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return "{} {}".format(self.name, self.class_name)

    def get_absolute_url(self):
        return reverse("teachers:dash", args=None)
