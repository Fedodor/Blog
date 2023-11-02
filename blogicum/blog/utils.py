from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from blog.models import Post


def all_posts():
    query_set = (
        Post.objects.select_related(
            'author',
            'location',
            'category'
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    return query_set


def get_post_detail(post_data):
    post = get_object_or_404(
        Post,
        pk=post_data['post_id'],
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
    return post


def category_posts():
    query_set = all_posts().filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )
    return query_set
