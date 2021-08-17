from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_post, name='new_post'),
    path('search/', views.search, name='search'),
    path('follow/', views.follow_index, name='follow_index'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/edit/', views.profile_edit, name='profile_edit'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit, name='post_edit'),
    path('<username>/<int:post_id>/post_delete/',
         views.delete_post, name='post_delete'),
    path('<username>/<int:post_id>/comment/',
         views.add_comment, name='add_comment'),
    path('<username>/<int:post_id>/<int:comment_id>/edit/',
         views.edit_comment, name='edit_comment'),
    path('<username>/<int:post_id>/<int:comment_id>/delete/',
         views.delete_comment, name='delete_comment'),
    path('<str:username>/follow/',
         views.profile_follow, name='profile_follow'),
    path('<str:username>/unfollow/',
         views.profile_unfollow, name='profile_unfollow'),
]
