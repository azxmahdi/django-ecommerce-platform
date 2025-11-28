from pathlib import Path
from django.core.files import File
from django.core.management.base import BaseCommand

from banner.models import BannerModel, BannerPosition
from shop.models import ProductCategoryModel
from blog.models import PostCategoryModel


BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "files"


class Command(BaseCommand):
    help = "Create sample banners with product_category and post_category"

    def handle(self, *args, **options):
        banners = [
            {
                "position": BannerPosition.MAIN,
                "filename": "main-1.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="زنانه"
                ),
                "order": 1,
            },
            {
                "position": BannerPosition.MAIN,
                "filename": "main-2.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="کفش-مردانه"
                ),
                "order": 2,
            },
            {
                "position": BannerPosition.MAIN,
                "filename": "main-3.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="پیراهن-مردانه"
                ),
                "order": 3,
            },
            {
                "position": BannerPosition.SMALL,
                "filename": "small-1.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="کیف-دستی-زنانه"
                ),
                "order": 1,
            },
            {
                "position": BannerPosition.SMALL,
                "filename": "small-2.gif",
                "post_category": PostCategoryModel.objects.get(slug="استایل"),
                "order": 2,
            },
            {
                "position": BannerPosition.SIDEBAR,
                "filename": "sidebar-1.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="مردانه"
                ),
                "order": 1,
            },
            {
                "position": BannerPosition.SIDEBAR,
                "filename": "sidebar-2.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="رژلب"
                ),
                "order": 2,
            },
            {
                "position": BannerPosition.CATEGORY,
                "filename": "category-1.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="پیراهن-مردانه"
                ),
                "title": "لباس مردانه",
                "order": 1,
            },
            {
                "position": BannerPosition.CATEGORY,
                "filename": "category-2.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="ساعت-هوشمند"
                ),
                "title": "ساعت هوشمند",
                "order": 2,
            },
            {
                "position": BannerPosition.CATEGORY,
                "filename": "category-3.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="ماشین-اسباب-بازی"
                ),
                "title": "ماشین اسباب بازی",
                "order": 3,
            },
            {
                "position": BannerPosition.CATEGORY,
                "filename": "category-4.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="گوشی-هوشمند"
                ),
                "title": "گوشی هوشمند",
                "order": 4,
            },
            {
                "position": BannerPosition.CATEGORY,
                "filename": "category-5.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="مانتو-زنانه"
                ),
                "title": "مانتو زنانه",
                "order": 5,
            },
            {
                "position": BannerPosition.CATEGORY,
                "filename": "category-6.jpg",
                "product_category": ProductCategoryModel.objects.get(
                    slug="قهوه-ساز"
                ),
                "title": "قهوه ساز",
                "order": 6,
            },
        ]

        for banner_data in banners:
            file_path = IMAGE_DIR / banner_data["filename"]
            if not file_path.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"فایل {banner_data['filename']} یافت نشد."
                    )
                )
                continue

            with open(file_path, "rb") as img_f:
                file = File(img_f, name=file_path.name)

                defaults = {
                    "is_active": True,
                    "order": banner_data["order"],
                    "title": banner_data.get("title", None),
                }
                if "product_category" in banner_data:
                    defaults["product_category"] = banner_data[
                        "product_category"
                    ]
                if "post_category" in banner_data:
                    defaults["post_category"] = banner_data["post_category"]

                banner, created = BannerModel.objects.get_or_create(
                    position=banner_data["position"].value,
                    file=file,
                    defaults=defaults,
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"بنر جدید ایجاد شد با فایل {file_path.name} و موقعیت {banner_data['position'].label}."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"بنر با موقعیت {banner_data['position'].label} از قبل وجود دارد."
                        )
                    )
