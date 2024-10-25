from django.urls import path, register_converter

from . import views, converters

register_converter(converters.TwoDigitLeftPadIntConverter, "two_digit")
register_converter(converters.FourDigitLeftPadIntConverter, "four_digit")
register_converter(converters.Base32Converter, "b32")
register_converter(converters.IntNotZero, "int_nz")

urlpatterns = [
    path(
        "<four_digit:year>/<two_digit:month>/<two_digit:day>/<b32:id>-<slug:slug>",
        views.get_article,
        name="article",
    ),
    path(
        "<four_digit:year>/<two_digit:month>/<two_digit:day>/<b32:id>",
        views.redirect_date_article,
        name="redirect_article",
    ),
    path("by-id/<b32:id>", views.redirect_article_id, name="article-by-id"),
    # path("", views.index, name="index"),
    # path("page/<int_nz:page>", views.index, name="index_page"),
    path("", views.ArticleListView.as_view(), name="articles"),
]
