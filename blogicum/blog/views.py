from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .models import Category, Comment, Post, User
from .forms import CommentEditForm, PostEditForm, UserEditForm
from .utils import all_posts, get_post_detail, category_posts


class HomePageListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = all_posts().filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )
    paginate_by = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostEditForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy("blog:profile", kwargs={"username": username})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    post_data = None

    def get_queryset(self):
        self.post_data = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if self.post_data.author == self.request.user:
            return all_posts().filter(pk=self.kwargs['post_id'])
        return category_posts().filter(pk=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.check_post_data():
            context['flag'] = True
            context['form'] = CommentEditForm()
        context['comments'] = self.object.comments.all().select_related(
            'author'
        )
        return context

    def check_post_data(self):
        return all(
            (
                self.post_data.category.is_published,
                self.post_data.is_published,
                self.post_data.pub_date <= timezone.now()
            )
        )

    def get_success_url(self):
        pk = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': pk})


class CategoryPostListView(HomePageListView):
    template_name = 'blog/category.html'
    category = None

    def get_queryset(self):
        slug = self.kwargs['category_slug']
        self.category = get_object_or_404(
            Category, slug=slug, is_published=True
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserPostListView(HomePageListView):
    template_name = 'blog/profile.html'
    author = None

    def get_queryset(self):
        username = self.kwargs['username']
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            return all_posts().filter(author=self.author)
        return super().get_queryset().filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment.html'
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_post_detail(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        form.instance.post = self.post_data
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': pk})


class CommentMixinView(LoginRequiredMixin, View):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        get_post_detail(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': pk})


class CommentUpdateView(CommentMixinView, UpdateView):
    form_class = CommentEditForm


class CommentDeleteView(CommentMixinView, DeleteView):
    fields = ('text',)
