import random
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker

from blog.models import PostModel, PostCategoryModel
from account.models import ProfileModel

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "img"
fake = Faker("fa_IR")


class Command(BaseCommand):
    help = "ایجاد چند پست نمونه با دسته‌بندی و نویسنده"

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            type=int,
            help="تعداد پست‌هایی که باید ایجاد شوند",
        )

    def handle(self, *args, **options):
        count = options["count"]

        author = ProfileModel.objects.first()
        if not author:
            self.stdout.write(
                self.style.ERROR("هیچ نویسنده‌ای (ProfileModel) وجود ندارد.")
            )
            return

        categories = list(PostCategoryModel.objects.all())
        if not categories:
            self.stdout.write(
                self.style.ERROR(
                    "هیچ دسته‌بندی‌ای وجود ندارد. ابتدا دسته‌بندی‌ها را ایجاد کنید."
                )
            )
            return

        image_files = (
            list(IMAGE_DIR.glob("*.jpg"))
            + list(IMAGE_DIR.glob("*.png"))
            + list(IMAGE_DIR.glob("*.gif"))
        )
        if not image_files:
            self.stdout.write(
                self.style.WARNING(
                    "هیچ تصویری در پوشه images یافت نشد. پست‌ها بدون تصویر ساخته می‌شوند."
                )
            )

        created_count = 0
        for i in range(count):
            title = fake.sentence(nb_words=5)
            slug = slugify(title, allow_unicode=True)
            while PostModel.objects.filter(slug=slug).exists():
                slug = f"{slug}-{random.randint(1,999)}"

            content = fake.paragraph(nb_sentences=5)
            now = timezone.now()

            image_file = None
            if image_files:
                selected_image = random.choice(image_files)
                with open(selected_image, "rb") as f:
                    image_file = SimpleUploadedFile(
                        selected_image.name,
                        f.read(),
                        content_type="image/jpeg",
                    )

            post = PostModel.objects.create(
                title=title,
                slug=slug,
                content=content,
                image=image_file if image_file else None,
                author=author,
                status=True,
                published_date=now,
            )

            chosen_categories = random.sample(
                categories, k=min(2, len(categories))
            )
            post.category.add(*chosen_categories)

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"پست '{title}' ایجاد شد."))

        self.stdout.write(
            self.style.SUCCESS(f"مجموع پست‌های ایجاد شده: {created_count}")
        )
