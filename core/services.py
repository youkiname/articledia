from .models import BrowserData, LoginDate, Ban, Chapter, Article, EditingNotification, ModeratorArticleBundle
from django.contrib.auth.models import User
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from os import path


def get_file_extension(request_file) -> str:
    return path.splitext(request_file.name)[-1]


def save_article_image(request_file) -> str:
    filename = datetime.now().strftime('image_%Y_%m_%d_%H_%M_%S') + get_file_extension(request_file)
    fs = FileSystemStorage('core/static/core/images/')
    return fs.save(filename, request_file)


def check_file_extension(request_file) -> bool:
    return get_file_extension(request_file) in ['.jpg', '.jpeg', '.png']


def create_notifications(editor: BrowserData, article: Article) -> None:
    now = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    for bundle in ModeratorArticleBundle.objects.filter(article=article).all():
        EditingNotification.objects.create(
            user=bundle.user,
            editor=editor,
            article=article,
            text=f"Статья '{article.title}' была изменена {now}",
        )


def is_subscribed(user: User, article: Article) -> bool:
    return ModeratorArticleBundle.objects.filter(article=article, user=user).exists()


def create_ban(ip, ban_type: str) -> None:
    browser_data, created = BrowserData.objects.get_or_create(ip=ip)
    Ban.objects.create(
        type=ban_type,
        browser_data=browser_data
    )


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def get_or_create_browser_data(request) -> BrowserData:
    ip = get_client_ip(request)
    data, created = BrowserData.objects.get_or_create(ip=ip)
    return data


def check_ban(ip: str, types: list[str]) -> bool:
    browser_data, _ = BrowserData.objects.get_or_create(ip=ip)
    return Ban.objects.filter(type__in=types, browser_data=browser_data).exists()


def get_bans(ip: str) -> list[Ban]:
    browser_data, _ = BrowserData.objects.get_or_create(ip=ip)
    return Ban.objects.filter(browser_data=browser_data).all()


def store_login_history(request, user: User) -> None:
    browser_data = get_or_create_browser_data(request)
    LoginDate.objects.create(
        browser_data=browser_data,
        user=user
    )


def save_chapters(article: Article, titles: list[str], texts: list[str], creator: BrowserData):
    chapter_last_index = article.get_chapter_last_index()
    for i, chapter_title in enumerate(titles):
        if not (chapter_title and texts[i]):
            continue
        chapter_last_index += 1
        Chapter.objects.create(article=article,
                               creator=creator,
                               title=chapter_title,
                               text=texts[i],
                               index=chapter_last_index)
