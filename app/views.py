from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
QUESTIONS =[{
        'id': i,
        'tittle': f'Question {i}',
        'content': f'Long lorem ipsum {i}',
        'tags': ['bender', 'black-jack'],
    }for i in range (1,100)
    ]

def paginate(objects, request, per_page=10, adjacent_pages=1):
    page = request.GET.get('page', 1)
    paginator = Paginator(objects, per_page)
    
    try:
        objects_page = paginator.page(page)
    except PageNotAnInteger:
        objects_page = paginator.page(1)
    except EmptyPage:
        objects_page = paginator.page(paginator.num_pages)
    
    # Вычисляем диапазон страниц для отображения
    current_page = objects_page.number
    total_pages = paginator.num_pages
    
    start_page = max(1, current_page - adjacent_pages)
    end_page = min(total_pages, current_page + adjacent_pages)
    
    # Корректируем диапазон, если мы у границ
    if current_page <= adjacent_pages + 1:
        end_page = min(1 + (adjacent_pages * 2), total_pages)
    elif current_page >= total_pages - adjacent_pages:
        start_page = max(total_pages - (adjacent_pages * 2), 1)
    
    page_range = range(start_page, end_page + 1)
    
    return objects_page, page_range
# Create your views here.
def index(request):
    questions_page, page_range = paginate(QUESTIONS, request, per_page=10, adjacent_pages=1)
    return render(request, 'index.html', {
        'questions': questions_page,
        'page_range': page_range,
    })
def question(request, question_id):
    item = QUESTIONS[question_id-1]
    return render(request, 'question.html', {'question': item})
def ask(request):
    return render(request, 'ask.html')
def login(request):
    return render(request, 'login.html')
def settings(request):
    return render(request, 'settings.html')
def signup(request):
    return render(request, 'signup.html')
def tag(request, tag_name=None):
    # Фильтрация вопросов по тегу, если он указан
    if tag_name:
        filtered_questions = [q for q in QUESTIONS if tag_name in q['tags']]
    else:
        filtered_questions = QUESTIONS
    
    # Пагинация
    questions_page, page_range = paginate(filtered_questions, request, per_page=10, adjacent_pages=1)
    
    return render(request, 'tag.html', {
        'questions': questions_page,
        'page_range': page_range,
        'current_tag': tag_name,  # Передаем текущий тег в шаблон
    })