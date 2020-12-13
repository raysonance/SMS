from django.contrib import admin

from .models import StudentModel, Subject, SubjectResult

# Register your models here.

admin.site.register(StudentModel)
admin.site.register(Subject)
admin.site.register(SubjectResult)
