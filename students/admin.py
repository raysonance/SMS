from django.contrib import admin

from .models import StudentMessages, StudentModel, Subject, SubjectResult

# Register your models here.

admin.site.register(StudentModel)
admin.site.register(Subject)
admin.site.register(SubjectResult)
admin.site.register(StudentMessages)
