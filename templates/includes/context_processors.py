import datetime as dt

from django.db.models.aggregates import Count
from posts.models import Group, Post


def year(request):
    """Add variable with the current year."""
    year = dt.date.today().year
    return {'year': year}


def groups(request):
    """Set of groups"""
    groups = Group.objects.prefetch_related('posts', ).all()
    return {'groups': groups}


def most_commented(request):
    """Set of most commented posts"""
    most_commented = (
        Post.objects
        .select_related('author', 'group')
        .prefetch_related('comments')
        .annotate(count_comments=Count('comments'))
        .order_by("-count_comments")[:5]
    )
    return {'most_commented': most_commented}
