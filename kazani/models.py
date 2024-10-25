from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from django.urls import reverse


class User(AbstractUser):
    # about_me = models.JSONField(default=list)
    profile_picture = models.URLField(null=True, blank=True)
    # extra_seo = models.JSONField(blank=True, default=dict)
    about_me = models.TextField(null=True, blank=True)

    def get_absolute_url(self) -> str | None:
        # return reverse(
        #     "profile",
        #     args=[self.id],
        # )

        return self.about_me

    # def get_seo(self, request: HttpRequest) -> dict[str, Any]:
    #     return {
    #         "@type": "Person",
    #         "name": self.username,
    #         "image": self.profile_picture,
    #         "givenName": self.first_name,
    #         "familyName": self.last_name,
    #         **self.extra_seo,
    #     }

    def __str__(self) -> str:
        return self.username
