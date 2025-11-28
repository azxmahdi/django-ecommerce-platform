from shop.models import SearchLogModel


def add_search_log(query, user=None):
    SearchLogModel.objects.get_or_create(
        query=query, user=user if user and user.is_authenticated else None
    )
