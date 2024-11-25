from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=[('draft', 'Draft'), ('published', 'Published')],
        default='draft'
    )
    upvotes = models.ManyToManyField(User, related_name='article_upvotes', blank=True)
    downvotes = models.ManyToManyField(User, related_name='article_downvotes', blank=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.slug])

    def get_vote_count(self):
        return self.upvotes.count() - self.downvotes.count()

    def vote(self, user, vote_type):
        """
        Handle voting logic with proper checks to prevent double voting
        """
        if vote_type not in ['up', 'down']:
            raise ValueError("Invalid vote type")

        # Remove any existing votes by this user
        self.upvotes.remove(user)
        self.downvotes.remove(user)

        # Add the new vote
        if vote_type == 'up':
            self.upvotes.add(user)
        else:
            self.downvotes.add(user)


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title}'
