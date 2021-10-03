from django.contrib import admin

from .models import ArticlePost, AssignmentSolution, Choice, ClassTestPost, ClassWorkPost, CommentReply, DocumentPost, ImagePost, PostComment, Question, StudentChoice, StudentMessages, StudentModel, Subject, SubjectResult, TextPost, VideoPost, YouTubePost

# Register your models here.

admin.site.register(StudentModel)
admin.site.register(Subject)
admin.site.register(SubjectResult)
admin.site.register(StudentMessages)
admin.site.register(ClassWorkPost)
admin.site.register(TextPost)
admin.site.register(VideoPost)
admin.site.register(DocumentPost)
admin.site.register(ImagePost)
admin.site.register(YouTubePost)
admin.site.register(ArticlePost)
admin.site.register(PostComment)
admin.site.register(CommentReply)
admin.site.register(ClassTestPost)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(StudentChoice)
admin.site.register(AssignmentSolution)