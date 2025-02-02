from django import template
from ..models import Post,Reference
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register=template.Library()

@register.simple_tag()
def total_posts():
    return Post.published.count()

@register.simple_tag()
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts=Post.published.order_by('-publish')[:count]
    return {'latest_posts':latest_posts}

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
    
@register.simple_tag()
def total_references():
    return Reference.objects.count()

@register.inclusion_tag('blog/reference/latest_references.html')
def show_latest_references(count=5):
    latest_references=Reference.objects.order_by('-created')[:count]
    return {'latest_references':latest_references}