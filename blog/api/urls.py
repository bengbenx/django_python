from django.urls import path
from . import views

app_name='blog'
urlpatterns=[
    path('posts/',views.PostListView.as_view(),name='api_post_list'),
    path('posts/<int:pk>/',views.PostDetailView.as_view(), name='api_post_detail'),
    path('users/',views.UserListView.as_view(), name='api_user_list'),
    path('users/<int:pk>',views.UserDetailView.as_view(), name='api_user_detail'),
]