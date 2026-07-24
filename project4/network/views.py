from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    if request.method == "GET":
        posts = Post.objects.order_by("-post_time")
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/index.html", {
            "posts": page_obj
        })
    if request.method == "POST":
        content = request.POST.get("content")
        poster = request.user
        Post.objects.create(poster=poster, content=content)
        return HttpResponseRedirect(reverse("index"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def edit(request):
    pass


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    posts = user.posts.order_by("-post_time")
    following_count = user.follow.count()
    follower_count = user.followers.count()
    return render(request, "network/profile.html", {
        "follower": follower_count,
        "follow": following_count,
        "posts": posts,
        "profile_user": user
    })


def follow(request, user_id):
    profile_user = User.objects.get(pk=user_id)
    if profile_user not in request.user.follow.all():
        request.user.follow.add(profile_user)
    else:
        request.user.follow.remove(profile_user)
    return HttpResponseRedirect(reverse("profile", args=[user_id]))


def following(request):
    if request.method == "GET":
        posts = Post.objects.order_by("-post_time").filter(poster__in=request.user.follow.all())
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/following.html", {
            "posts": page_obj
        })


def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    if post not in request.user.like_posts.all():
        request.user.like_posts.add(post)
    else:
        request.user.like_posts.remove(post)
    return JsonResponse({"likes": post.like.count()})





