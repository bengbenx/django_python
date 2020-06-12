from django.contrib import admin
from .models import Post, Comment

admin.site.site_header='My Project Admin page'
admin.site.index_title='Feature area'
admin.site.site_title='My Django Blog'
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=('title','slug','author','status')
    list_filter=('status','created','publish','author')
    search_fields=('title','body')
    prepopulated_fields={'slug':('title',)}
    raw_id_fields=('author',)
    date_hierarchy='publish'
    ordering=('status','publish')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display=('name','email','post','created','active')
    list_filter=('active','created','updated')
    search_fields=('name','email','body')