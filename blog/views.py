from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.forms import PostForm, CommentForm

# Create your views here.


class AboutView(TemplateView):
    template_name = "about.html"


class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by(
            "-published_date"
        )


class PostDetailView(DetailView):
    model = Post


class CreatePostView(CreateView, LoginRequiredMixin):
    model = Post
    login_url = "/login/"
    redirect_field_name = "blog/post_detail.html"
    form_class = PostForm


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    login_url = "/login/"
    redirect_field_name = "blog/post_detail.html"
    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("post_list")


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    login_url = "/login/"
    redirect_field_name = "blog/post_list.html"

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by("created_date")
