from django.db.models import (
    Model, CharField,
    DateTimeField, ForeignKey,
    IntegerField, CASCADE, SET_NULL,
    TextField, BooleanField
)
from django.contrib.auth.models import User
import os.path


class BrowserData(Model):
    ip = CharField(max_length=16, db_index=True, unique=True)


class LoginDate(Model):
    browser_data = ForeignKey(BrowserData, on_delete=SET_NULL, null=True)
    user = ForeignKey(User, on_delete=CASCADE)
    date = DateTimeField(auto_now_add=True)


class Ban(Model):
    type = CharField(max_length=100)
    browser_data = ForeignKey(BrowserData, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)


class Article(Model):
    image_filename = CharField(max_length=200)
    title = CharField(max_length=200)
    creator = ForeignKey(BrowserData, on_delete=SET_NULL, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def image_url(self) -> str:
        path = '/static/core/images/' + self.image_filename
        return path

    def get_abstract(self):
        first_chapter = self.chapter_set.filter(active=True).order_by('index').first()
        if not first_chapter:
            return "No abstract..."
        return first_chapter.text

    def active_chapters(self):
        return self.chapter_set.filter(active=True).order_by('index')

    def get_chapter_last_index(self) -> int:
        chapter = self.chapter_set.filter(active=True).order_by('-index').first()
        if not chapter:
            return 0
        return chapter.index

    def editing_history(self):
        result = {}
        for i in range(1, self.get_chapter_last_index() + 1):
            result[i] = self.chapter_set.filter(index=i).order_by('created_at')
        return result

    def creator_ip(self):
        print(self.creator)
        return self.creator.ip

    def human_created_at(self):
        return self.created_at.strftime("%Y-%m-%d")

    def __str__(self):
        return self.title


class Chapter(Model):
    article = ForeignKey(Article, on_delete=CASCADE)
    creator = ForeignKey(BrowserData, on_delete=SET_NULL, null=True)
    title = CharField(max_length=200)
    text = TextField()
    index = IntegerField(default=1)
    active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def creator_ip(self):
        return self.creator.ip

    def __str__(self):
        return self.title


class ModeratorArticleBundle(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    article = ForeignKey(Article, on_delete=CASCADE)


class EditingNotification(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    editor = ForeignKey(BrowserData, on_delete=SET_NULL, null=True)
    article = ForeignKey(Article, on_delete=CASCADE)
    text = CharField(max_length=200)
    viewed = BooleanField(default=False)
