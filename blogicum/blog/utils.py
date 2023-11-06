from django.db.models import Count
from django.utils import timezone


def filter_posts(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def annotation_posts(queryset):
    return queryset.select_related(
        'author', 'location', 'category'
    ).order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count('comments')
    )
