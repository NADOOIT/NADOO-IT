from django.contrib import admin
from .models import Article, Comment

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at', 'get_vote_count')
    list_filter = ('status', 'created_at', 'published_at', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)

    def get_vote_count(self, obj):
        return obj.get_vote_count()
    get_vote_count.short_description = 'Votes'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created_at', 'parent')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'article__title')
