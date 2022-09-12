from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Chapter
from django.contrib import auth
from .decorators import login_required


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def save_chapters(article, titles, texts):
    chapter_last_index = article.get_chapter_last_index()
    for i, chapter_title in enumerate(titles):
        if not (chapter_title and texts[i]):
            continue
        chapter_last_index += 1
        Chapter.objects.create(article=article,
                               title=chapter_title,
                               text=texts[i],
                               index=chapter_last_index)


def try_login(request) -> bool:
    username = request.POST['email']
    password = request.POST['password']
    user = auth.authenticate(request, username=username, password=password)
    print(user)
    if user is not None:
        auth.login(request, user)
    return user is not None


def login_page(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        if try_login(request):
            return redirect('index')
    return render(request, 'core/login.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')


def index(request):
    search_query = request.GET.get('q', '')
    articles = Article.objects.filter(title__contains=search_query).order_by('-created_at').all()
    return render(request, 'core/index.html', {
        'articles': articles,
        'search_query': search_query
    })


def detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'core/detail.html', {
        'article': article
    })


def create_article(request):
    return render(request, 'core/create_article.html')


def store_article(request):
    title = request.POST['title']
    chapter_titles = request.POST.getlist('chapter_title[]')
    chapter_texts = request.POST.getlist('chapter_text[]')
    if not title:
        return redirect('create_article')
    article = Article.objects.create(title=request.POST['title'])
    save_chapters(article, chapter_titles, chapter_texts)
    return redirect('detail', article_id=article.id)


def edit_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'core/edit_article.html', {
        'article': article
    })


def update_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    title = request.POST['title']
    chapter_titles = request.POST.getlist('chapter_title[]')
    chapter_texts = request.POST.getlist('chapter_text[]')
    if not title:
        return redirect('edit_article', article_id=article.id)
    article.title = title
    article.save()
    save_chapters(article, chapter_titles, chapter_texts)
    return redirect('detail', article_id=article.id)


def edit_chapter(request, article_id, chapter_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'core/edit_chapter.html', {
        'article': article,
        'chapter_id': chapter_id
    })


def update_chapter(request, article_id, chapter_id):
    article = get_object_or_404(Article, pk=article_id)
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    title = request.POST['title']
    text = request.POST['text']
    if not title:
        return redirect('edit_chapter', article_id=article.id, chapter_id=chapter.id)
    chapter.active = False
    chapter.save()
    # create new chapter to save editing history
    new_chapter = Chapter.objects.create(article=article,
                                         title=title,
                                         text=text,
                                         index=chapter.index)
    # renew updated_at article field
    article.save()
    return redirect('detail', article_id=article.id)


@login_required
def editing_history(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'core/editing_history.html', {
        'article': article
    })
