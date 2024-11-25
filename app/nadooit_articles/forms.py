from django import forms
from .models import Article, Comment
from django.core.exceptions import ValidationError
import bleach

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'status']
        
    def clean_content(self):
        """
        Clean and sanitize HTML content to prevent XSS attacks
        """
        content = self.cleaned_data['content']
        # Define allowed HTML tags and attributes
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a'
        ]
        allowed_attrs = {
            'a': ['href', 'title'],
            '*': ['class']
        }
        # Clean the content
        cleaned_content = bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        return cleaned_content

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
        
    def clean_content(self):
        """
        Clean and sanitize comment content
        """
        content = self.cleaned_data['content']
        # Only allow basic formatting
        allowed_tags = ['p', 'br', 'strong', 'em']
        allowed_attrs = {}
        cleaned_content = bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        if not cleaned_content.strip():
            raise ValidationError("Comment cannot be empty.")
        return cleaned_content
