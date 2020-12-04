from django.db import models

# Create your models here.


class Class(models.Model):
    class_name = models.CharField(max_length=20)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.class_name
