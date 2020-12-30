from django.contrib import admin

from .models import Class, Session, SubClass, TeacherModel

admin.site.register(Class)
admin.site.register(TeacherModel)
admin.site.register(Session)
admin.site.register(SubClass)
