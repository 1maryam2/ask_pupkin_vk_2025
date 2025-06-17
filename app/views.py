from datetime import timezone
import json
from urllib import request
from django.shortcuts import render, get_object_or_404
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .models import Question, Tag, Answer, QuestionLike
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import AnswerForm, AskForm, LoginForm, UserForm, SignUpForm
from django.contrib.auth import login as auth_login
from django.utils.text import slugify
from .models import Question, Answer, QuestionLike, AnswerLike
from .forms import UserSettingsForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
import json
import requests
from django.db.models import Sum, Q
from django.conf import settings
from django.core.cache import cache


def get_common_data():
    return {
        'popular_tags': Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10],
        'best_members': User.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5],
        'ws_url': 'localhost:8010',
    }
def paginate(objects, request, per_page=10, adjacent_pages=1):
    page = request.GET.get('page', 1)
    paginator = Paginator(objects, per_page)
    
    try:
        objects_page = paginator.page(page)
    except PageNotAnInteger:
        objects_page = paginator.page(1)
    except EmptyPage:
        objects_page = paginator.page(paginator.num_pages)
    current_page = objects_page.number
    total_pages = paginator.num_pages
    
    start_page = max(1, current_page - adjacent_pages)
    end_page = min(total_pages, current_page + adjacent_pages)
    
    if current_page <= adjacent_pages + 1:
        end_page = min(1 + (adjacent_pages * 2), total_pages)
    elif current_page >= total_pages - adjacent_pages:
        start_page = max(total_pages - (adjacent_pages * 2), 1)
    page_range = range(start_page, end_page + 1)
    
    return objects_page, page_range

def index(request):
    questions = Question.objects.all().order_by('-created_at')
    questions_page, page_range = paginate(questions, request)
    context = get_common_data()
    context.update({
        'registered_user': True,
        'questions': questions_page,
        'page_range': page_range,
        'use_rating': True,
    })
    
    return render(request, 'index.html', context)
@login_required
def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id) 
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Чтобы просмотреть ответы, пожалуйста, войдите или зарегистрируйтесь')
    
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            new_answer = Answer.objects.create(
                content=content,
                author=request.user,
                question=question
            )
            return redirect('question', question_id=question.id)
    
    answers = Answer.objects.filter(question=question).order_by('-is_correct', '-created_at')
    paginator = Paginator(answers, 5)
    page_number = request.GET.get('page')
    
    try:
        answers = paginator.page(page_number)
    except PageNotAnInteger:
        answers = paginator.page(1)
    except EmptyPage:
        answers = paginator.page(paginator.num_pages)
    
    page_range = paginator.get_elided_page_range(
        number=answers.number,
        on_each_side=1,
        on_ends=1
    )
    
    context = {
        'question': question,
        'answers': answers,
        'page_range': page_range,
        **get_common_data()
    }
    return render(request, 'question.html', context)

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name__iexact=tag_name)
    questions = tag.questions.all().order_by('-created_at')
    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]
    best_members = User.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]
    questions_page, page_range = paginate(questions, request)
    context = get_common_data()
    context.update( {
        'use_rating': True,
       'questions': questions_page,
        'page_range': page_range,
        'tag': tag,
        'popular_tags': popular_tags,
        'best_members': best_members,
    })
    return render(request, 'tag.html', context)
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})
@login_required
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            
            for tag_name in form.cleaned_data['tags']:
                tag, _ = Tag.objects.get_or_create(name=slugify(tag_name.lower()))
                question.tags.add(tag)
            
            return redirect('question', question_id=question.id)
    else:
        form = AskForm()
    return render(request, 'ask.html', {'form': form, **get_common_data()})
def login(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST, request.FILES)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(reverse('settings'))
            else:
                form.add_error(field = None, error="User not found")
        else:
            print(form.errors)
    context = get_common_data()
    context['form'] = form
    return render(request, 'login.html', context)
def hot(request):
    hot_questions = Question.objects.all().order_by('-rating', '-created_at')
    
    context = get_common_data()
    questions_page, page_range = paginate(hot_questions, request)
    context.update({
        'questions': questions_page,
        'page_range': page_range,
        'use_rating': True
    })
    return render(request, 'hot.html', context)
@login_required
def settings(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        profile = user.profile
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        
        messages.success(request, 'Настройки сохранены!')
        return redirect('settings')
    
    context = {
        'user': request.user,
        **get_common_data()
    }
    return render(request, 'settings.html', context)
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  
            auth_login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form, **get_common_data()})

def logout(request):
    auth.logout(request)
    if request.META.get('HTTP_REFERER', '').endswith('/settings'):
        return redirect('index')
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def users_create(request):
    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('login'))
    context = get_common_data()
    return render(request, 'signup.html', context)
def users(request):
    users = User.objects.all()
    return render(request, 'users.html',{'users':users})
@login_required(login_url=reverse_lazy('login'))
def profile_edit(request):
    return render(request, 'settings.html')
@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question
    )
    if not created:
        like.delete()
    actual_likes = QuestionLike.objects.filter(question=question).count()
    question.rating = actual_likes
    question.save()
    
    return JsonResponse({
        'success': True,
        'new_rating': actual_likes
    })

@login_required
def like_answer(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

    answer = get_object_or_404(Answer, pk=answer_id)
    like, created = AnswerLike.objects.get_or_create(user=request.user, answer=answer)
    if not created:
        like.delete()
    answer.refresh_from_db()
    new_rating = AnswerLike.objects.filter(answer=answer).count()

    return JsonResponse({
        'success': True,
        'new_rating': new_rating,
        'is_liked': created
    })
@login_required
@require_POST
def mark_answer_correct(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.question.author:
        return JsonResponse({
            'success': False,
            'message': 'Only the author of the question can mark answers as correct'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        is_correct = data.get('is_correct', False)
        if is_correct:
            Answer.objects.filter(question=answer.question, is_correct=True).update(is_correct=False)
        answer.is_correct = is_correct
        answer.save()
        return JsonResponse({
            'success': True,
            'is_correct': answer.is_correct
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)