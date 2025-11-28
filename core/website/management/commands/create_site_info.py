from pathlib import Path
from django.core.files import File
from django.core.management.base import BaseCommand
from website.models import SiteInfoModel

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR


class Command(BaseCommand):
    help = "Create default SiteInfo object with logo"

    def handle(self, *args, **options):
        file_path = IMAGE_DIR / "logo.svg"

        if not file_path.exists():
            self.stdout.write(
                self.style.WARNING(f"logo {file_path.name} not found")
            )
            return

        with open(file_path, "rb") as img_f:
            logo_file = File(img_f, name=file_path.name)

            # شرط دقیق‌تر برای پیدا کردن رکورد مشابه
            site_info = SiteInfoModel.objects.filter(
                store_name="فروشگاه من",
                support_email="support@example.com",
                support_phone="0000000 - 021",
            ).first()

            if site_info:
                self.stdout.write(
                    self.style.WARNING(
                        "Similar SiteInfo object already exists."
                    )
                )
            else:
                SiteInfoModel.objects.create(
                    store_name="فروشگاه من",
                    logo=logo_file,
                    support_email="support@example.com",
                    support_phone="0000000 - 021",
                    head_office_address="اصفهان، خیابان مثال، پلاک ۱۲۳",
                    support_hours="شنبه تا چهارشنبه ۹ تا ۱۷",
                )
                self.stdout.write(
                    self.style.SUCCESS("Object SiteInfo was created")
                )
