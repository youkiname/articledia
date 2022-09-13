from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Chapter, LoginDate, Ban, ModeratorArticleBundle, EditingNotification
from django.contrib import auth
from .decorators import login_required, has_access
from .services import (store_login_history, get_or_create_browser_data, save_chapters,
                       create_ban, get_bans, create_notifications, is_subscribed,
                       save_article_image, check_file_extension)
from django.http import Http404, HttpResponseRedirect


def try_login(request):
    username = request.POST['email']
    password = request.POST['password']
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        store_login_history(request, user)
    return user


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


def detail(request, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    is_moderator_subscribed = request.user.is_authenticated and is_subscribed(request.user, article)
    return render(request, 'core/detail.html', {
        'article': article,
        'is_subscribed': is_moderator_subscribed,
    })


@has_access(['creating'])
def create_article(request):
    return render(request, 'core/create_article.html')


@has_access(['creating'])
def store_article(request):
    title = request.POST['title']
    image = request.FILES['image']
    chapter_titles = request.POST.getlist('chapter_title[]')
    chapter_texts = request.POST.getlist('chapter_text[]')
    if not title or not check_file_extension(image):
        return redirect('create_article')
    image_filename = save_article_image(image)
    creator = get_or_create_browser_data(request)
    article = Article.objects.create(
        image_filename=image_filename,
        title=request.POST['title'],
        creator=creator
    )
    save_chapters(article, chapter_titles, chapter_texts, creator)
    return redirect('detail', article_id=article.id)


@has_access(['editing'])
def edit_article(request, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'core/edit_article.html', {
        'article': article
    })


@has_access(['editing'])
def update_article(request, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    title = request.POST['title']
    chapter_titles = request.POST.getlist('chapter_title[]')
    chapter_texts = request.POST.getlist('chapter_text[]')
    if not title:
        return redirect('edit_article', article_id=article.id)
    article.title = title
    article.save()
    editor = get_or_create_browser_data(request)
    save_chapters(article, chapter_titles, chapter_texts, editor)
    create_notifications(editor, article)
    return redirect('detail', article_id=article.id)


@has_access(['editing'])
def edit_chapter(request, article_id: int, chapter_id: int):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'core/edit_chapter.html', {
        'article': article,
        'chapter_id': chapter_id
    })


@has_access(['editing'])
def update_chapter(request, article_id: int, chapter_id: int):
    article = get_object_or_404(Article, pk=article_id)
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    title = request.POST['title']
    text = request.POST['text']
    if not title:
        return redirect('edit_chapter', article_id=article.id, chapter_id=chapter.id)
    chapter.active = False
    chapter.save()
    editor = get_or_create_browser_data(request)
    # create new chapter to save editing history
    new_chapter = Chapter.objects.create(article=article,
                                         creator=editor,
                                         title=title,
                                         text=text,
                                         index=chapter.index)
    # renew updated_at article field
    article.save()
    create_notifications(editor, article)
    return redirect('detail', article_id=article.id)


@login_required
def activate_chapter(request, chapter_id: int):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    Chapter.objects.filter(article_id=chapter.article_id, index=chapter.index).update(active=False)
    chapter.active = True
    chapter.save()
    return redirect('editing_history', article_id=chapter.article_id)


@login_required
def editing_history(request, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'core/editing_history.html', {
        'article': article
    })


@login_required
def login_history(request):
    login_dates = LoginDate.objects.filter(user=request.user).all()
    display_viewed = request.GET.get('display_viewed', False)
    notifications = EditingNotification.objects.filter(user=request.user)
    if not display_viewed:
        notifications = notifications.filter(viewed=False)
    return render(request, 'core/login_history.html', {
        'login_dates': login_dates,
        'notifications': notifications,
        'display_viewed': display_viewed
    })


@login_required
def ip_actions(request):
    ip = request.GET.get('ip', None)
    if not ip:
        raise Http404
    return render(request, 'core/ip_actions.html', {
        'ip': ip,
        'bans': get_bans(ip)
    })


@login_required
def ban_editing_by_ip(request):
    ip = request.GET.get('ip', None)
    if not ip:
        raise Http404
    create_ban(ip, 'editing')
    return HttpResponseRedirect(request.GET.get('next', '/'))


@login_required
def ban_creating_by_ip(request):
    ip = request.GET.get('ip', None)
    if not ip:
        raise Http404
    create_ban(ip, 'creating')
    return HttpResponseRedirect(request.GET.get('next', '/'))


@login_required
def delete_ban(request, ban_id: int):
    Ban.objects.filter(id=ban_id).delete()
    return HttpResponseRedirect(request.GET.get('next', '/'))


@login_required
def subscribe_notifications(request, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    ModeratorArticleBundle.objects.get_or_create(
        user=request.user,
        article=article
    )
    return HttpResponseRedirect(request.GET.get('next', '/'))


@login_required
def unsubscribe_notifications(request, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    ModeratorArticleBundle.objects.filter(
        user=request.user,
        article=article
    ).delete()
    return HttpResponseRedirect(request.GET.get('next', '/'))


@login_required
def mark_notifications_as_viewed(request):
    EditingNotification.objects.filter(user=request.user).update(viewed=True)
    return redirect('login_history')
