from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout, name='logout'),
    path('login-history/', views.login_history, name='login_history'),
    path('article/<int:article_id>/', views.detail, name='detail'),
    path('article/create/', views.create_article, name='create_article'),
    path('article/store/', views.store_article, name='store_article'),
    path('article/edit-article/<int:article_id>/', views.edit_article, name='edit_article'),
    path('article/update-article/<int:article_id>/', views.update_article, name='update_article'),
    path('article/edit-chapter/<int:article_id>/<int:chapter_id>/', views.edit_chapter, name='edit_chapter'),
    path('article/update-chapter/<int:article_id>/<int:chapter_id>/', views.update_chapter, name='update_chapter'),
    path('editing-history/<int:article_id>/', views.editing_history, name='editing_history'),
    path('activate-chapter/<int:chapter_id>/', views.activate_chapter, name='activate_chapter'),
    path('ip-actions/', views.ip_actions, name='ip_actions'),
    path('ban-editing/', views.ban_editing_by_ip, name='ban_editing'),
    path('ban-creating/', views.ban_creating_by_ip, name='ban_creating'),
    path('delete-ban/<int:ban_id>/', views.delete_ban, name='delete_ban'),
    path('subscribe-notifications/<int:article_id>/', views.subscribe_notifications, name='subscribe_notifications'),
    path('unsubscribe-notifications/<int:article_id>/', views.unsubscribe_notifications, name='unsubscribe_notifications'),
    path('mark_notifications_as_viewed/', views.mark_notifications_as_viewed, name='mark_notifications_as_viewed'),
]
