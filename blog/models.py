from typing import Any
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from taggit.managers import TaggableManager
from kazani.settings import AUTH_USER_MODEL


class Article(models.Model):
    class ContentType(models.IntegerChoices):
        JSON = 1
        MARKDOWN = 2
        HTML = 3

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=256)
    slug = models.SlugField()
    author = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comments_enabled = models.BooleanField(
        default=True,
        help_text="Whether to display the form to submit comments and to display accepted comments.",
    )

    page_url = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        default=None,
        help_text="Absolute path to show page at (/ for homepage, /about, etc.)",
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    tags = TaggableManager(
        blank=True, help_text="Tags for (eventual) searching and for search engines."
    )
    description = models.CharField(
        max_length=480,
        default="",
        help_text="Description of the page for the article list and search engines.",
    )

    is_draft = models.BooleanField(
        default=True, help_text="Honestly does nothing but shows DRAFT on the page."
    )
    is_hidden = models.BooleanField(
        default=True, help_text="Hides the page from the article list."
    )
    is_indexed = models.BooleanField(
        default=False, help_text="Whether to allow search engines to index this page."
    )
    no_container = models.BooleanField(
        default=False, help_text="Remove everything but the navigation and footer."
    )

    content = models.TextField(help_text="Content of the page")
    content_type = models.IntegerField(
        choices=ContentType.choices,
        default=ContentType.MARKDOWN,
    )
    script = models.TextField(
        default="",
        blank=True,
        help_text="Javascript code that goes at the end of body.",
    )
    head = models.TextField(
        default="", blank=True, help_text="HTML that is inserted into <head>"
    )

    extra_seo = models.JSONField(default=dict, blank=True)
    override_seo = models.BooleanField(default=False)

    __prev_is_hidden = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__prev_is_hidden = self.is_hidden

    def save(self, *args, **kwargs):
        if self.page_url:
            try:
                temp = Article.objects.get(page_url=self.page_url)

                if self != temp:
                    temp.page_url = None
                    temp.save()

            except Article.DoesNotExist:
                pass

        if self.__prev_is_hidden != self.is_hidden and not self.is_hidden:
            self.is_indexed = True

        if self.page_url:
            self.page_url = self.page_url.rstrip("/") + "/"

        super().save(*args, **kwargs)
        self.__prev_is_hidden = self.is_hidden

    def get_absolute_url(self) -> str:
        if self.page_url:
            return self.page_url

        return reverse(
            "article",
            kwargs={
                "year": self.created.year,
                "month": self.created.month,
                "day": self.created.day,
                "id": self.id,
                "slug": self.slug,
            },
        )

    def get_seo(self, request: HttpRequest) -> dict[str, Any]:
        same_as = (
            f"https://{request.get_host()}{reverse('article-by-id', args=[self.id])}"
        )

        if self.page_url:
            same_as = [
                same_as,
                f"https://{request.get_host()}"
                + reverse(
                    "article",
                    kwargs={
                        "year": self.created.year,
                        "month": self.created.month,
                        "day": self.created.day,
                        "id": self.id,
                        "slug": self.slug,
                    },
                ),
            ]

        return (
            {
                "@type": "BlogPosting",
                "headline": self.title,
                "description": self.description,
                "isFamilyFriendly": True,
                "dateCreated": self.created.isoformat(),
                "datePublished": self.created.isoformat(),
                "dateModified": self.modified.isoformat(),
                "keywords": [tag[1] for tag in self.tags.values_list()],
                "url": f"https://{request.get_host()}{self.get_absolute_url()}",
                "sameAs": same_as,
                "author": {
                    "@type": "Person",
                    "name": self.author.username,
                    "url": f"https://{request.get_host()}/users/{self.author.id}",
                },
                **self.extra_seo,
            }
            if not self.override_seo
            else self.extra_seo
        )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["created"]


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.content!r} by {self.name}"


class Upload(models.Model):
    ident = models.CharField(
        max_length=512,
        help_text="Identifier for the image. Used to auto-generate the url if it's not specified (/media/ident). Also used to refer to it in Markdown.",
    )
    path = models.CharField(
        max_length=512,
        help_text="Absolute path to serve file at (/media/image.png, etc.)",
        blank=True,
    )
    content = models.FileField(upload_to="uploads/")

    def __str__(self) -> str:
        return self.content.name

    def save(self, *args, **kwargs) -> None:
        if self.path is None or self.path.strip() == "":
            self.path = f"/media/{self.ident.strip()}"

        self.ident = self.ident.strip()

        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return self.path
