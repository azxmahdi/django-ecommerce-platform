from django.urls import path

from .views import ProductCommentCreateView, LikeOrDislikeProductCommentView

app_name = "review"

urlpatterns = [
    path(
        "product/comment/create/",
        ProductCommentCreateView.as_view(),
        name="product-comment-create",
    ),
    path(
        "like-or-dislike/product-comment/",
        LikeOrDislikeProductCommentView.as_view(),
        name="like-or-dislike-product-comment",
    ),
]
