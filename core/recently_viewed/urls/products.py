from django.urls import path

from ..views import RemoveProductView, RemoveAllProductsView

app_name = "products"


urlpatterns = [
    path(
        "remove/product/", RemoveProductView.as_view(), name="remove-product"
    ),
    path(
        "remove/all/products/",
        RemoveAllProductsView.as_view(),
        name="remove-all-products",
    ),
]
