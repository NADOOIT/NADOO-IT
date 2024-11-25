from django.urls import path
from . import views

app_name = 'nadooit_articles'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('create/', views.article_create, name='article_create'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('<slug:slug>/edit/', views.article_edit, name='article_edit'),
    path('vote/<int:article_id>/', views.article_vote, name='article_vote'),
    path('comment/<int:article_id>/', views.comment_create, name='comment_create'),
]
