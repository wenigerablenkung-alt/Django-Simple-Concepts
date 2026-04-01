"""
URL configuration for lab4project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from lab4app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("request-demo/", views.request_demo, name="request_demo"),
    path("form-demo/", views.form_demo, name="form_demo"),
    path("session-demo/", views.session_demo, name="session_demo"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("posts/", views.post_list, name="post_list"),
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/<int:pk>/edit/", views.post_update, name="post_update"),
    path("posts/<int:pk>/delete/", views.post_delete, name="post_delete"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("middleware-demo/", views.middleware_demo, name="middleware_demo"),
    path("trigger-error/", views.trigger_error, name="trigger_error"),
]
