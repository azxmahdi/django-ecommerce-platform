from django.core.management.base import BaseCommand
from pages.models import StaticPageModel


class Command(BaseCommand):
    help = "ایجاد صفحات ثابت (راهنمای خرید، چرا روتی‌کالا، درباره ما و ...)"

    def handle(self, *args, **options):
        pages = [
            {
                "slug": "راهنمای-خرید",
                "title": "راهنمای خرید",
                "content": "اینجا توضیحات مربوط به صفحه راهنمای خرید اینجا قرار می‌گیرد...",
            },
            {
                "slug": "چرا-روتی-کالا",
                "title": "چرا روتی‌کالا",
                "content": "اینجا توضیحات مربوط به صفحه چرا روتی‌کالا اینجا قرار می‌گیرد...",
            },
            {
                "slug": "درباره-ما",
                "title": "درباره ما",
                "content": "اینجا توضیحات مربوط به صفحه درباره ما اینجا قرار می‌گیرد...",
            },
        ]

        for page_data in pages:
            page, created = StaticPageModel.objects.get_or_create(
                slug=page_data["slug"],
                defaults={
                    "title": page_data["title"],
                    "content": page_data["content"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"صفحه '{page.title}' ایجاد شد.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"صفحه '{page.title}' از قبل وجود دارد."
                    )
                )
