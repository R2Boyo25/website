"""
URL configuration for kazani project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.contrib.syndication.views import Feed
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import path, re_path, include, register_converter, reverse
from django.shortcuts import get_object_or_404
from django.conf.urls.static import static
from blog.views import get_article
from blog.models import Article
from blog import converters
from kazani import settings

# from kazani import views


def get_root(request: HttpRequest) -> HttpResponse:
    try:
        article = Article.objects.get(page_url="/")

    except Article.DoesNotExist:
        return HttpResponse(
            f'No homepage has been defined. <a href="{request.scheme}://{request.get_host()}{reverse("admin:index")}blog/article/">Please make one.</a>',
            status=404,
        )

    return get_article(request, 0, 0, 0, article.id, "")


class BlogSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Article.objects.filter(is_indexed=True)

    def lastmod(self, obj: Article):
        return obj.created


class BlogFeed(Feed):
    title = "Kazani.dev's blog"
    link = "/articles/"
    description = "Kazani's personal blog. I talk about Computer Science, Linux, and other things here!"

    def items(self):
        return Article.objects.order_by("-created").filter(is_hidden=False)

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.description


register_converter(converters.Base32Converter, "b32")


urlpatterns = [
    path("kaz/__admin_/", admin.site.urls),
    path("articles/", include("blog.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"blog": BlogSitemap}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("feed/", BlogFeed()),
    # path("profiles/<b32:id>", views.profile_page, name="profile"),
    path("", get_root, name="index"),
    re_path(
        "^.*$",
        lambda request: get_article(
            request,
            0,
            0,
            0,
            get_object_or_404(
                Article, page_url=request.get_full_path().rstrip("/") + "/"
            ).id,
            "",
        ),
    ),
]
