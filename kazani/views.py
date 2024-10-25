# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render, get_object_or_404

# from blog.render import HTMLRenderer
# from .models import User


# def profile_page(request: HttpRequest, id: int) -> HttpResponse:
#     user = get_object_or_404(User, id=id)

#     return render(
#         request,
#         "profile.html",
#         {
#             "user": user,
#             "seo": {"@context": "https://schema.org", **user.get_seo(request)},
#             "content": HTMLRenderer(user.about_me).to_html(user),
#         },
#     )
