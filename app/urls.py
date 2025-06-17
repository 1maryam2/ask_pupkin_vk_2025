from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('main', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('ask', views.ask, name='ask'),
    path('login/', views.login, name='login'),
    path('settings', views.settings, name='settings'),
    path('signup', views.signup, name='signup'),
    path('tag/', views.tag, name='all_tags'), 
    path('users', views.users, name='users'), 
    path('logout/', views.logout, name='logout'),
    path('tag/<str:tag_name>/', views.tag, name='questions_by_tag'),
    path('question/<int:question_id>/like/', views.like_question, name='like_question'),
    path('answer/<int:answer_id>/like/', views.like_answer, name='like_answer'),
    path('answer/<int:answer_id>/mark_correct/', views.mark_answer_correct, name='mark_answer_correct')
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)