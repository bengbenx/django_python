from rest_framework import generics,mixins,permissions
from ..models import Post
from .serializers import PostSerializer,UserSerializer
from django.contrib.auth import get_user_model
from .permissions import IsAuthorOrReadonly
from django.utils.text import slugify

# class PostListView(generics.ListAPIView):
#     queryset=Post.objects.all()
#     serializer_class=PostSerializer

# class PostListView(mixins.ListModelMixin,
#                 mixins.CreateModelMixin,
#                 generics.GenericAPIView):
#     queryset=Post.objects.all()
#     serializer_class=PostSerializer

#     def get(self,request,*args,**kwargs):
#         return self.list(request,*args,**kwargs)

#     def post(self,request,*args,**kwargs):
#         return self.create(request,*args,**kwargs)

class PostListView(generics.ListCreateAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self,serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user,
                    status='published',
                    slug=slugify(serializer.validated_data['title'],allow_unicode=True))



# class PostDetailView(generics.RetrieveAPIView):
#     queryset=Post.objects.all()
#     serializer_class=PostSerializer

# class PostDetailView(mixins.RetrieveModelMixin,
#                 mixins.UpdateModelMixin,
#                 mixins.DestroyModelMixin,
#                 generics.GenericAPIView):
#     queryset=Post.objects.all()
#     serializer_class=PostSerializer

#     def get(self,request,*args,**kwargs):
#         return self.retrieve(request,*args,**kwargs)

#     def put(self,request,*args,**kwargs):
#         return self.update(request,*args,**kwargs)

#     def delete(self,request,*args,**kwargs):
#         return self.destroy(request,*args,**kwargs)
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly,IsAuthorOrReadonly]
    
    def perform_update(self,serializer):
        if serializer.is_valid():
            serializer.save(slug=slugify(serializer.validated_data['title'],allow_unicode=True))

class UserListView(generics.ListAPIView):
    queryset=get_user_model().objects.all()
    serializer_class=UserSerializer

class UserDetailView(generics.RetrieveAPIView):
    queryset=get_user_model().objects.all()
    serializer_class=UserSerializer