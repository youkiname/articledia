from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout, name='logout'),
    path('article/<int:article_id>/', views.detail, name='detail'),
    path('article/create/', views.create_article, name='create_article'),
    path('article/store/', views.store_article, name='store_article'),
    path('article/edit-article/<int:article_id>/', views.edit_article, name='edit_article'),
    path('article/update-article/<int:article_id>/', views.update_article, name='update_article'),
    path('article/edit-chapter/<int:article_id>/<int:chapter_id>/', views.edit_chapter, name='edit_chapter'),
    path('article/update-chapter/<int:article_id>/<int:chapter_id>/', views.update_chapter, name='update_chapter'),
    path('editing-history/<int:article_id>/', views.editing_history, name='editing_history'),
]
