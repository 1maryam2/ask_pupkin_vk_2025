from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike

admin.site.unregister(User) 

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile', )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.register(User, CustomUserAdmin)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'rating')
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
    raw_id_fields = ('author',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'question', 'created_at', 'is_correct')
    list_filter = ('created_at', 'is_correct')
    search_fields = ('content',)
    raw_id_fields = ('author', 'question')

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'question')
    raw_id_fields = ('user', 'question')

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer')
    raw_id_fields = ('user', 'answer')