import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count

from .models import Post, Category, Comment, UserProfile
from .forms import ContactForm, PostForm, CustomRegistrationForm, CommentForm


def home(request):
    stats = {
        "total_posts": Post.objects.count(),
        "published_posts": Post.objects.filter(status="published").count(),
        "total_categories": Category.objects.count(),
    }
    return render(request, "lab4app/home.html", {"stats": stats})


def request_demo(request):
    info = {
        "method": request.method,
        "get_params": dict(request.GET),
        "post_params": dict(request.POST),
        "user_agent": request.META.get("HTTP_USER_AGENT", "Unknown"),
        "remote_addr": request.META.get("REMOTE_ADDR", "Unknown"),
        "cookies": dict(request.COOKIES),
        "session_key": request.session.session_key,
        "user": str(request.user),
        "is_authenticated": request.user.is_authenticated,
        "accepts_json": "application/json" in request.META.get("HTTP_ACCEPT", ""),
    }

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(info)

    if request.method == "POST":
        response = render(
            request,
            "lab4app/request_demo.html",
            {"info": info, "message": "You sent a POST request!"},
        )
        response.set_cookie(
            "demo_cookie",
            "hello_from_django",
            max_age=3600,
            httponly=True,
            samesite="Lax",
        )
        return response

    return render(request, "lab4app/request_demo.html", {"info": info})


def form_demo(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            messages.success(
                request, f"Thanks {name}! Message received about: '{subject}'"
            )

            return redirect("form_demo")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ContactForm()

    return render(request, "lab4app/form_demo.html", {"form": form})


def session_demo(request):
    action = request.GET.get("action", "")

    if action == "set":
        request.session["username"] = request.GET.get("name", "Guest")
        request.session["visit_count"] = request.session.get("visit_count", 0) + 1
        request.session["last_page"] = request.path
        messages.success(request, "Session data saved!")

    elif action == "delete":
        if "username" in request.session:
            del request.session["username"]
        messages.info(request, "Username removed from session.")

    elif action == "clear":
        request.session.flush()
        messages.warning(request, "Session cleared!")

    session_data = {
        "session_key": request.session.session_key,
        "username": request.session.get("username", "Not set"),
        "visit_count": request.session.get("visit_count", 0),
        "last_page": request.session.get("last_page", "Not set"),
    }

    return render(request, "lab4app/session_demo.html", {"session_data": session_data})


def cart_add(request):
    """Shopping cart using sessions — a practical session example."""
    if request.method == "POST":
        item_name = request.POST.get("item_name", "")
        item_price = request.POST.get("item_price", "0")

        cart = request.session.get("cart", [])
        cart.append({"name": item_name, "price": float(item_price)})

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(request, f"Added '{item_name}' to cart!")
    return redirect("cart_view")


def cart_view(request):
    """Display the shopping cart stored in the session."""
    cart = request.session.get("cart", [])
    total = sum(item["price"] for item in cart)
    return render(request, "lab4app/cart.html", {"cart": cart, "total": total})


def cart_clear(request):
    """Remove cart from session."""
    if "cart" in request.session:
        del request.session["cart"]
    messages.info(request, "Cart cleared.")
    return redirect("cart_view")


def post_list(request):
    posts = Post.objects.filter(status="published")
    search_query = request.GET.get("q", "")
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    category_id = request.GET.get("category", "")
    if category_id:
        posts = posts.filter(categories__id=category_id)

    posts = posts.annotate(comment_count=Count("comments"))
    posts = posts.select_related("author")
    posts = posts.prefetch_related("categories")

    categories = Category.objects.all()

    return render(
        request,
        "lab4app/post_list.html",
        {
            "posts": posts,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_id,
        },
    )


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, status="published")
    post.increment_views()

    comments = post.comments.select_related("author").order_by("-created_at")
    comment_form = CommentForm()
    if request.method == "POST" and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment posted!")
            return redirect("post_detail", pk=pk)

    return render(
        request,
        "lab4app/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()

            messages.success(request, f"Post '{post.title}' created successfully!")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()

    return render(request, "lab4app/post_form.html", {"form": form, "action": "Create"})


@login_required
def post_update(request, pk):
    """UPDATE — Edit an existing post."""
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated!")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "lab4app/post_form.html",
        {"form": form, "post": post, "action": "Update"},
    )


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == "POST":
        title = post.title
        post.delete()
        messages.success(request, f"Post '{title}' deleted.")
        return redirect("post_list")

    return render(request, "lab4app/post_confirm_delete.html", {"post": post})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Account created.")
            return redirect("dashboard")
    else:
        form = CustomRegistrationForm()

    return render(request, "lab4app/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "dashboard")
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "lab4app/login.html", {"next": request.GET.get("next", "")})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You've been logged out.")
        return redirect("home")
    return redirect("home")


@login_required
def dashboard(request):
    user = request.user
    user_posts = Post.objects.filter(author=user).order_by("-created_at")[:5]

    profile, created = UserProfile.objects.get_or_create(user=user)

    context = {
        "user": user,
        "profile": profile,
        "user_posts": user_posts,
        "post_count": Post.objects.filter(author=user).count(),
        "published_count": Post.objects.filter(author=user, status="published").count(),
    }
    return render(request, "lab4app/dashboard.html", context)


def middleware_demo(request):
    return render(request, "lab4app/middleware_demo.html")


def trigger_error(request):
    raise ValueError("This is a test error to demonstrate error middleware!")
