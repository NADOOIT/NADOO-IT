from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import PermissionDenied
from .models import Article, Comment
from .forms import ArticleForm, CommentForm

def article_list(request):
    articles = Article.objects.filter(status='published')
    return render(request, 'nadooit_articles/article_list.html', {'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    comments = article.comments.filter(parent=None)
    comment_form = CommentForm()
    
    if request.htmx and request.method == 'GET':
        return render(request, 'nadooit_articles/partials/article_content.html', 
                     {'article': article, 'comments': comments, 'comment_form': comment_form})
    
    return render(request, 'nadooit_articles/article_detail.html',
                 {'article': article, 'comments': comments, 'comment_form': comment_form})

@login_required
@csrf_protect
def article_vote(request, article_id):
    if not request.htmx:
        return HttpResponse("HTMX required", status=400)
    
    article = get_object_or_404(Article, id=article_id)
    vote_type = request.POST.get('vote_type')
    
    if vote_type not in ['up', 'down']:
        return HttpResponse("Invalid vote type", status=400)
    
    try:
        article.vote(request.user, vote_type)
        return render(request, 'nadooit_articles/partials/vote_buttons.html', {'article': article})
    except Exception as e:
        return HttpResponse(str(e), status=400)

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.slug = slugify(article.title)
            article.save()
            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm()
    return render(request, 'nadooit_articles/article_form.html', {'form': form})

@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save()
            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm(instance=article)
    return render(request, 'nadooit_articles/article_form.html', {'form': form, 'article': article})

@login_required
@require_POST
def comment_create(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent = get_object_or_404(Comment, id=parent_id)
        comment.save()
        
        if request.htmx:
            context = {'comment': comment}
            if comment.parent:
                template = 'nadooit_articles/partials/comment_reply.html'
            else:
                template = 'nadooit_articles/partials/comment.html'
            return render(request, template, context)
            
    return redirect(article.get_absolute_url())
