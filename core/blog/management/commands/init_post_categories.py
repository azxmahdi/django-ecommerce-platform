from django.core.management.base import BaseCommand
from blog.models import PostCategoryModel
from django.utils.text import slugify
import re


class Command(BaseCommand):
    help = "Create 10 logical categories for posts"

    def persian_slugify(self, text):
        text = str(text).strip()
        text = re.sub(r"[\s\u200c]+", "-", text)
        text = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9\-_]", "", text)
        text = re.sub(r"-+", "-", text)
        return text.strip("-") or slugify(text, allow_unicode=True)

    def handle(self, *args, **options):
        categories = [
            "استایل",
            "سلامت",
            "تکنولوژی",
            "سفر",
            "غذا",
            "کتاب",
            "هنر",
            "ورزش",
            "کودک",
        ]

        created_count = 0
        for name in categories:
            category, created = PostCategoryModel.objects.get_or_create(
                slug=name,
                defaults={"name": name},
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"دسته‌بندی '{name}' ایجاد شد (slug: {name})."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"دسته‌بندی '{name}' از قبل وجود دارد.")
                )

        self.stdout.write(
            self.style.SUCCESS(f"مجموع دسته‌بندی‌های ایجاد شده: {created_count}")
        )
