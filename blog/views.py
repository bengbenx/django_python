from django.shortcuts import render, get_object_or_404,redirect
from .models import Post, Comment,Reference
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm, SearchForm,ReferenceForm
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from django.db.models import Count
from django.contrib.auth.decorators import login_required

@login_required
def post_share(request,post_id):
    post=get_object_or_404(Post,id=post_id,status='published')
    sent=False

    if request.method=='POST':
        form=EmailPostForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            post_url=request.build_absolute_uri(post.get_absolute_url())
            subject=f"{cd['name']} recomend you read {post.title}"
            message=(f"Read {post.title} at {post_url}\n\n"
                    f"{cd['name']} comments: {cd['comments']}")
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject,message,email_from,[cd['to']])
            sent=True
    else:
        form=EmailPostForm()

    return render(request,
                'blog/post/share.html',
                {'post':post,'form':form,'sent':sent})


@login_required
def post_list(request, tag_slug=None):
    object_list=Post.published.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        object_list=object_list.filter(tags__in=[tag])

    paginator=Paginator(object_list,3)
    page=request.GET.get('page')

    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)

    return render(request,
                'blog/post/list.html',
                {'page':page,'posts':posts, 'tag':tag})

@login_required
def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post, slug=post,
                            status='published',
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)

    #list active comments
    comments=post.comments.filter(active=True)
    new_comment=None

    if request.method=='POST':
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment=comment_form.save(commit=False)
            new_comment.post=post
            new_comment.save()
    else:
        comment_form=CommentForm()

    #list similar posts
    post_tags_ids=post.tags.values_list('id',flat=True)
    similar_posts=Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts=similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request,
                    'blog/post/detail.html',
                    {'post':post,
                    'comments':comments,
                    'new_comment':new_comment,
                    'comment_form':comment_form,
                    'similar_posts':similar_posts})

#from django.contrib.postgres.search import (SearchVector,SearchQuery,SearchRank)
#from .forms import SearchForm
from django.contrib.postgres.search import TrigramSimilarity

@login_required
def post_search(request):

    if 'query' in request.GET:
        form=SearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            #results=Post.published.annotate(
            #        search = SearchVector('title','body'),
            #        ).filter(search=query)
            #search_vector=SearchVector('title','body')
            #search_vector=SearchVector('title',weight='A') + \
            #            SearchVector('body',weight='B')
            #search_query=SearchQuery(query)
            #results=Post.published.annotate(search=search_vector,
            #                rank=SearchRank(search_vector,search_query)
            #                ).filter(search=search_query).order_by('-rank')
            #results=Post.published.annotate(search=search_vector,
            #                rank=SearchRank(search_vector,search_query)
            #                ).filter(rank__gte=0.3).order_by('-rank')
            results=Post.published.annotate(
                            similarity=TrigramSimilarity('title',query),
                            ).filter(similarity__gt=0.1).order_by('-similarity')
    else:
        form=SearchForm()
        query=None
        results=[]

    return render(request,
                    'blog/post/search.html',
                    {'form':form,'query':query, 'results':results})
    
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (ListView, FormView, CreateView, 
                        UpdateView, DeleteView)
from django.urls import reverse_lazy

class PostListView(LoginRequiredMixin,ListView):
    queryset=Post.published.all()
    context_object_name='posts'
    paginate_by=2
    template_name='blog/post/list.html'

    def get_queryset(self):
        qs=super().get_queryset()
        tag_slug=self.kwargs.get('tag_slug')

        if tag_slug:
            tag=get_object_or_404(Tag,slug=tag_slug)
            qs=qs.filter(tags__in=[tag])
            self.tag=tag
        else:
            self.tag=None
        
        return qs

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)

        if self.tag:
            context['tag']=self.tag

        return context

class PostDetailView(LoginRequiredMixin,FormView):
    form_class=CommentForm
    template_name='blog/post/detail.html'

    def get_initial(self):
        pk=self.kwargs.get('pk')
        slug=self.kwargs.get('slug')
        self.post=get_object_or_404(Post,pk=pk,slug=slug)

        self.comments=self.post.comments.filter(active=True)
        self.new_comment=None

        post_tags_ids=self.post.tags.values_list('id',flat=True)
        similar_posts=Post.published.filter(tags__in=post_tags_ids).exclude(id=self.post.id)
        self.similar_posts=similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
        return super().get_initial()

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['post']=self.post
        context['comments']=self.comments
        context['similar_posts']=self.similar_posts
        return context

    def form_valid(self,form):
        new_comment=form.save(commit=False)
        new_comment.post=self.post
        new_comment.save()
        context=self.get_context_data()
        context['new_comment']=new_comment
        return render(self.request,self.template_name,context=context)

from django.utils.text import slugify

class PostCreateView(LoginRequiredMixin,CreateView):
    model=Post
    template_name='blog/post/post_form.html'
    fields=['title','body','tags']

    def form_valid(self,form):
        form.instance.author=self.request.user
        form.instance.status='published'
        form.instance.slug=slugify(form.instance.title, allow_unicode=True)

        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UpdateView):
    model=Post
    fields=['title','body','tags']
    template_name='blog/post/post_form.html'
    query_pk_and_slug=True

    def get_queryset(self):
        qs=super().get_queryset()

        return qs.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model=Post
    template_name='blog/post/post_confirm_delete.html'
    query_pk_and_slug=True
    success_url=reverse_lazy('blog:post_list')

    def get_queryset(self):
        qs=super().get_queryset()

        return qs.filter(author=self.request.user)

class ReferenceListView(LoginRequiredMixin,ListView):
    queryset=Reference.objects.all()
    context_object_name='references'
    paginate_by=5
    template_name='blog/reference/reference_list.html'

    def get_queryset(self):
        qs=super().get_queryset()
        
        return qs

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)

        return context

class ReferenceCreateView(LoginRequiredMixin,CreateView):
    model=Reference
    template_name='blog/reference/reference_form.html'
    fields=['title','description','link']
    success_url=reverse_lazy('blog:reference_list')

    def form_valid(self,form):
        form.instance.author=self.request.user
        form.instance.slug=slugify(form.instance.title, allow_unicode=True)
        obj=form.save()
        return super().form_valid(form)

class ReferenceUpdateView(LoginRequiredMixin,UpdateView):
    model=Reference
    fields=['title','description','link']
    template_name='blog/reference/reference_form.html'
    query_pk_and_slug=True
    success_url=reverse_lazy('blog:reference_list')

    def get_queryset(self):
        qs=super().get_queryset()

        return qs.filter(author=self.request.user)

class ReferenceDeleteView(LoginRequiredMixin,DeleteView):
    model=Reference
    template_name='blog/reference/reference_confirm_delete.html'
    query_pk_and_slug=True
    success_url=reverse_lazy('blog:reference_list')

    def get_queryset(self):
        qs=super().get_queryset()

        return qs.filter(author=self.request.user)