import hashlib
import json
from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import redirect
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.contrib.auth.models import AnonymousUser

from blog.render import render_page
from .models import Article, Comment
from .forms import CommentForm


# def index(request: HttpRequest, page: int = 1):  # pylint: disable=unused-argument
#    return HttpResponse(Article.objects.all())


class ArticleListView(ListView):
    model = Article
    paginate_by = 10
    ordering = "-created"

    def get_queryset(self) -> QuerySet[Any]:
        if (
            not isinstance(self.request.user, AnonymousUser)
            and self.request.user.is_superuser
        ):
            return super().get_queryset().exclude(page_url="/")

        return super().get_queryset().filter(is_hidden=False).exclude(page_url="/")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)

        ctx["seo"] = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "Blog",
                "title": "Kazani's Blog",
                "blogPost": [
                    article.get_seo(self.request) for article in ctx["object_list"]
                ],
            },
            indent="\t",
        )

        ctx["title"] = "Articles"
        if ctx["page_obj"].paginator.num_pages not in (0, 1):
            ctx[
                "title"
            ] += f" - Page {ctx['page_obj'].number} of {ctx['page_obj'].paginator.num_pages}"

        return ctx


def get_article(
    request: HttpRequest, year: int, month: int, day: int, id: int, slug: str
):  # pylint: disable=unused-argument,redefined-builtin
    article = get_object_or_404(Article, id=id)

    seo = {"@context": "https://schema.org", **article.get_seo(request)}

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment: Comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.save()

    return render(
        request,
        "blog/article.html",
        {
            "article": article,
            "tags": article.tags.values_list,
            "content": render_page(article.content, article),
            "seo": json.dumps(seo, indent="\t"),
            "title": article.title,
            "script": f"<script>{article.script}</script>",
            "comments": [
                {
                    "name": comment.name,
                    "created": comment.created,
                    "content": comment.content,
                    "email_hash": hashlib.md5(
                        comment.email.encode("utf-8")
                    ).hexdigest(),
                }
                for comment in article.comments.filter(active=True).order_by("-created")
            ],
        },
    )


def redirect_date_article(
    request: HttpRequest, year: int, month: int, day: int, id: int
):  # pylint: disable=unused-argument,redefined-builtin
    return redirect_article_id(request, id)


def redirect_article_id(
    request: HttpRequest, id: int
):  # pylint: disable=unused-argument,redefined-builtin
    return redirect(get_object_or_404(Article, id=id).get_absolute_url())
