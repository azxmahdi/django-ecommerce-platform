from django.db import models
from django.utils import timezone
from datetime import timedelta


class SearchLogQuerySet(models.QuerySet):
    def get_popular_searches(self):
        from .models import SearchLogModel

        return (
            SearchLogModel.objects.values("query")
            .annotate(count=models.Count("id"))
            .order_by("-count")[:10]
        )


class SearchLogManager(models.Manager):
    def get_queryset(self):
        return SearchLogQuerySet(self.model, using=self._db)

    def get_popular_searches(self):
        return self.get_queryset().get_popular_searches()
