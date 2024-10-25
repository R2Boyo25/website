from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Article, Comment

# from .widgets import HtmlEditor


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_filter = ("created",)
    readonly_fields = ("created", "modified")

    prepopulated_fields = {"slug": ["title"]}

    # widgets = {
    #     "content": HtmlEditor(attrs={"style": "width: 90%; height: 100%;"}),
    # }


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("name", "content", "article", "created", "active")
    list_filter = ("active", "created")
    search_fields = ("name", "email", "content")
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
