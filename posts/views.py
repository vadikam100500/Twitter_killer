from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Comment, Follow, Group, Post, User


def pages(request, value):
    paginator = Paginator(value, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    latest = (
        Post.objects.
        select_related('author', 'group').
        prefetch_related('comments').all()
    )
    page = pages(request, latest)
    return render(request, 'index.html', {'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:index')
    return render(request, 'new.html', {'form': form})


def search(request):
    query = request.GET.get("q")
    post_matching = Post.objects.filter(text__icontains=query)
    page = pages(request, post_matching)
    return render(request, 'search_new.html', {'page': page, 'value': query})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = (
        group.posts.
        select_related('author').
        prefetch_related('comments').all()[:12]
    )
    page = pages(request, posts)
    context = {
        'group': group,
        'page': page
    }
    return render(request, 'group.html', context)


def profile(request, username):
    author = get_object_or_404(
        User.objects.
        prefetch_related('posts', 'follower', 'following'),
        username=username
    )
    author_posts = (
        author.posts.
        select_related('group').
        prefetch_related('comments').all()
    )
    posts_count = author_posts.count()
    following = (
        request.user.is_authenticated
        and request.user != author
        and Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    )
    page = pages(request, author_posts)
    context = {
        'author': author,
        'count': posts_count,
        'page': page,
        'following': following
    }
    return render(request, 'profile.html', context)


@login_required
def profile_edit(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        return redirect('posts:profile', username)
    form = ProfileEditForm(
        request.POST or None, files=request.FILES or None, instance=author)
    if form.is_valid():
        form.save()
        return redirect('posts:profile', form.cleaned_data['username'])
    return render(request, 'profile_edit.html', {'form': form})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    author = post.author
    form = CommentForm()
    comments = (
        post.comments.select_related('author').all()
    )
    context = {
        'post': post,
        'author': author,
        'form': form,
        'comments': comments
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post', username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post', username, post_id)
    return render(request, 'new.html', {'form': form, 'post': post})


@login_required
def delete_post(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post', username, post_id)
    post.delete()
    return redirect('posts:index')


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
    return redirect('posts:post', username, post_id)


@login_required
def edit_comment(request, username, post_id, comment_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    author = post.author
    comment = post.comments.get(id=comment_id)
    if request.user != comment.author:
        return redirect('posts:post', username, post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('posts:post', username, post_id)
    comments = (
        post.comments.select_related('author').all()
    )
    context = {
        'post': post,
        'author': author,
        'form': form,
        'comments': comments,
        'comment': comment
    }
    return render(request, 'post.html', context)


@login_required
def delete_comment(request, username, post_id, comment_id):
    comment = get_object_or_404(
        Comment, post__id=post_id, id=comment_id
    )
    if request.user != comment.author:
        return redirect('posts:post', username, post_id)
    comment.delete()
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    posts = (Post.objects.select_related('author').
             select_related('group').
             prefetch_related('comments').filter(
             author__following__user=request.user
             ))
    page = pages(request, posts)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
