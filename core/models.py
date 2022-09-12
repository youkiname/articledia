from django.db.models import (
    Model, CharField,
    DateTimeField, ForeignKey,
    IntegerField, CASCADE,
    TextField, BooleanField
)


class Article(Model):
    title = CharField(max_length=200)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

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
        print(result)
        return result

    def human_created_at(self):
        return self.created_at.strftime("%Y-%m-%d")

    def __str__(self):
        return self.title


class Chapter(Model):
    article = ForeignKey(Article, on_delete=CASCADE)
    title = CharField(max_length=200)
    text = TextField()
    index = IntegerField(default=1)
    active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
