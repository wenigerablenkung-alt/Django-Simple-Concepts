from django.contrib import admin
from .models import Post, Category, Comment, UserProfile

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
 
 
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'view_count', 'created_at']
    list_filter = ['status', 'categories', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    raw_id_fields = ['author']
    filter_horizontal = ['categories']
    actions = ['make_published']
 
    def make_published(self, request, queryset):
        count = queryset.update(status='published')
        self.message_user(request, f"{count} post(s) marked as published.")
    make_published.short_description = "Mark selected posts as published"
 
 
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    search_fields = ['author__username', 'body']
 
 
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'joined_at']
    search_fields = ['user__username', 'bio']