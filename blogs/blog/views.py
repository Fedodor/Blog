from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentEditForm, PostEditForm, UserEditForm
from .mixin import CommentMixinView, PostMixinView
from .models import Category, Comment, Post, User
from .utils import annotation_posts, filter_posts


class HomePageListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = annotation_posts(filter_posts(Post.objects.all()))
    paginate_by = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user.username
            }
        )


class PostUpdateView(PostMixinView, UpdateView):
    form_class = PostEditForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': self.kwargs[self.pk_url_kwarg]
            }
        )


class PostDeleteView(PostMixinView, DeleteView):

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=PostEditForm(instance=self.object),
        )

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user.username
            }
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(
            Post,
            pk=self.kwargs[self.pk_url_kwarg],
        )
        if post.author != self.request.user:
            return get_object_or_404(
                filter_posts(Post.objects),
                pk=self.kwargs[self.pk_url_kwarg],
            )
        return post

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentEditForm(),
            comments=self.get_object().comments.all().select_related(
                'author'
            ),
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            post_id=self.kwargs[self.pk_url_kwarg]
        )


class CategoryPostListView(HomePageListView):
    template_name = 'blog/category.html'

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return annotation_posts(
            filter_posts(self.get_category().posts.all())
        )

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            category=self.get_category(),
        )


class UserPostListView(HomePageListView):
    template_name = 'blog/profile.html'

    def get_author(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username'],
        )

    def get_queryset(self):
        if self.get_author() == self.request.user:
            # Все посты автора
            return annotation_posts(
                self.get_author().posts.all()
            )
        # Посты автора, которые пользователи могут посмотреть
        return annotation_posts(
            filter_posts(self.get_author().posts.all())
        )

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.get_author(),
        )


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user.username
            }
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def get_post(self):
        return get_object_or_404(
            filter_posts(Post.objects.all()),
            pk=self.kwargs[self.pk_url_kwarg],
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.get_post()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': self.kwargs['post_id']
            }
        )


class CommentUpdateView(CommentMixinView, UpdateView):
    form_class = CommentEditForm


class CommentDeleteView(CommentMixinView, DeleteView):
    fields = ('text',)
