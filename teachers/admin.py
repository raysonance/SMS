from django.contrib import admin

from .models import Class, Section, Session, SubClass, TeacherMessages, TeacherModel

admin.site.register(Class)
admin.site.register(TeacherModel)
admin.site.register(Session)
admin.site.register(SubClass)
admin.site.register(Section)
admin.site.register(TeacherMessages)
