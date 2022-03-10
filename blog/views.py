from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
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
from .models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.models import User

# Create your views here.


class AboutView(TemplateView):
    template_name = "about.html"


# region Post
class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.raw(
            "SELECT * FROM blog_post,auth_user WHERE blog_post.author_id = auth_user.id and published_date ORDER BY blog_post.published_date DESC"
        )


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, id=self.kwargs["pk"])
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
        context["liked"] = liked
        return context

    def get_object(self):
        object = super().get_object()
        object.views += 1
        object.save()
        return object


class CreatePostView(CreateView, LoginRequiredMixin):
    model = Post
    login_url = "/login/"
    redirect_field_name = "blog/post_detail.html"
    form_class = PostForm

    def form_valid(self, form):
        self.form = form.save(commit=False)
        self.form.author = self.request.user
        self.form.save()
        return super().form_valid(form)


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
    redirect_field_name = "blog/post_draft_list.html"
    template_name = "post_draft_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by("create_date")


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect("post_detail", pk=pk)


@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        # liked = False
    else:
        post.likes.add(request.user)
        # unliked = True
    return redirect("post_detail", pk=pk)


# endregion

# region Comments
@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("post_detail", pk=post.pk)

    else:
        form = CommentForm()
    return render(request, "blog/comment_form.html", {"form": form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect("post_detail", pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect("post_detail", pk=post_pk)


# endregion

## login
# class Login(LoginView):
#     template_name = "login.html"
