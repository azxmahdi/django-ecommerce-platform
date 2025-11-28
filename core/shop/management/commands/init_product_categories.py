import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify


from shop.models import ProductCategoryModel
from shop.services.category.cache import CategoryCache
from shop.services.category.provider import CategoryProvider


class Command(BaseCommand):
    help = "Create base shop categories in a hierarchical structure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete all existing categories and recreate them",
        )

    def persian_slugify(self, text):
        text = str(text).strip()

        text = re.sub(r"[\s\u200c]+", "-", text)

        text = re.sub(
            r"[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9\-_]",
            "",
            text,
        )

        text = re.sub(r"-+", "-", text)

        text = text.strip("-")

        if not text:
            text = slugify(text, allow_unicode=False)

        return text

    def create_unique_slug(self, name):
        original_slug = self.persian_slugify(name)

        if not original_slug:
            original_slug = slugify(name, allow_unicode=False)
            if not original_slug:
                original_slug = "category"

        slug = original_slug
        counter = 1

        while ProductCategoryModel.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def handle(self, *args, **options):
        force = options["force"]

        if force:
            self.stdout.write("Deleting all existing categories...")
            ProductCategoryModel.objects.all().delete()

        if ProductCategoryModel.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    "Categories already exist! Use --force to recreate them."
                )
            )
            return

        categories_structure = {
            "الکترونیک": {
                "موبایل و تبلت": [
                    "گوشی هوشمند",
                    "گوشی ساده",
                    "تبلت",
                    "شارژر",
                    "کابل اتصال",
                    "کیف و کاور",
                    "هندزفری بی‌سیم",
                    "پاوربانک",
                ],
                "کامپیوتر و لپ‌تاپ": [
                    "لپ‌تاپ",
                    "کامپیوتر دسکتاپ",
                    "مانیتور",
                    "کیبورد و ماوس",
                    "کابل HDMI",
                    "کارت گرافیک",
                    "رم کامپیوتر",
                ],
                "صوتی و تصویری": [
                    "تلویزیون",
                    "سینمای خانگی",
                    "پخش‌کننده DVD",
                    "پروژکتور",
                    "اسپیکر",
                    "هدفون بی‌سیم",
                    "هدفون سیمی",
                ],
                "لوازم جانبی": [
                    "کابل شارژ",
                    "شارژر دیواری",
                    "شارژر فندکی",
                    "هندزفری سیمی",
                    "کیف دوربین",
                    "کارت حافظه",
                ],
            },
            "مد و پوشاک": {
                "مردانه": [
                    "پیراهن مردانه",
                    "تی‌شرت مردانه",
                    "شلوار مردانه",
                    "کفش مردانه",
                    "کمربند مردانه",
                    "ساعت مچی مردانه",
                ],
                "زنانه": [
                    "مانتو زنانه",
                    "لباس مجلسی زنانه",
                    "شلوار زنانه",
                    "کفش زنانه",
                    "کیف دستی زنانه",
                    "روسری",
                ],
                "بچه‌گانه": [
                    "پیراهن بچه‌گانه",
                    "شلوار بچه‌گانه",
                    "سویشرت بچه‌گانه",
                    "کفش بچه‌گانه",
                    "ست بادی نوزادی",
                    "هدبند",
                ],
                "اکسسوری": ["گردنبند", "دستبند", "عینک آفتابی", "کلاه", "شال"],
            },
            "خانه و آشپزخانه": {
                "لوازم آشپزخانه": [
                    "یخچال",
                    "ظرفشویی",
                    "مایکروویو",
                    "جاروبرقی",
                    "کتری برقی",
                    "قهوه‌ساز",
                ],
                "دکوراسیون": [
                    "تابلو",
                    "قاب عکس",
                    "گلدان",
                    "فرش",
                    "پرده",
                    "کنسول و بوفه",
                ],
                "خواب و حمام": [
                    "ست حوله",
                    "ملحفه",
                    "بالش",
                    "پتو",
                    "سرویس خواب کودک",
                ],
                "سرو و پذیرایی": [
                    "سرویس غذاخوری",
                    "چای‌خوری",
                    "قهوه‌خوری",
                    "لیوان",
                    "بطری",
                    "سینی",
                ],
            },
            "زیبایی و سلامت": {
                "مراقبت پوست": [
                    "کرم مرطوب‌کننده",
                    "ضدآفتاب",
                    "ماسک صورت",
                    "سرم",
                    "پاک‌کننده",
                    "تونر",
                ],
                "مراقبت مو": [
                    "شامپو",
                    "نرم‌کننده",
                    "ماسک مو",
                    "روغن مو",
                    "تونیک پوست سر",
                    "سرم مو",
                ],
                "آرایشی": [
                    "کرم پودر",
                    "رژلب",
                    "ریمل",
                    "سایه چشم",
                    "خط چشم",
                    "لاک ناخن",
                ],
                "بهداشتی": [
                    "مسواک",
                    "خمیر دندان",
                    "صابون",
                    "شامپو بچه",
                    "دستمال مرطوب",
                    "ضدعفونی‌کننده",
                ],
            },
            "ورزش و سفر": {
                "لوازم ورزشی": [
                    "دمبل",
                    "مت ورزشی",
                    "تردمیل",
                    "دوچرخه ثابت",
                    "کفش ورزشی",
                    "طناب پرش",
                ],
                "پوشاک ورزشی": [
                    "تی‌شرت ورزشی",
                    "شلوارک",
                    "دمپایی",
                    "سویشرت",
                    "کوله‌پشتی",
                ],
                "سفر و کمپینگ": [
                    "چادر",
                    "کیسه خواب",
                    "چراغ قوه",
                    "زیرانداز",
                    "کوله‌پشتی سفر",
                    "اجاق کوهنوردی",
                ],
                "ساعت و تناسب اندام": [
                    "ساعت هوشمند",
                    "دستبند سلامتی",
                    "ترازو",
                    "پوشیدنی تناسب اندام",
                    "هدفون ورزشی",
                ],
            },
            "کودک و نوزاد": {
                "اسباب‌بازی": [
                    "عروسک",
                    "پازل",
                    "ماشین اسباب‌بازی",
                    "بازی فکری",
                    "بلوک ساختنی",
                    "قطار چوبی",
                ],
                "وسایل آموزشی": [
                    "کتاب آموزشی",
                    "لگو",
                    "دوچرخه بچه‌گانه",
                    "ساعت آموزشی",
                    "فلش کارت",
                    "پازل آموزشی",
                ],
                "لباس کودک": [
                    "ست بادی",
                    "کلاه کودک",
                    "جوراب کودک",
                    "کاپشن کودک",
                ],
                "سیسمونی": [
                    "روروک",
                    "کریر",
                    "گهواره",
                    "تشک بازی",
                    "صندلی ماشین",
                    "تخت کنار مادر",
                ],
            },
            "کتاب و فرهنگ": {
                "رمان و داستان": [
                    "رمان معاصر",
                    "داستان کوتاه",
                    "مجموعه داستان",
                    "رمان نوجوان",
                    "رمان خارجی",
                    "داستان فلسفی",
                ],
                "آموزشی": [
                    "کتاب درسی",
                    "مهارت‌های نرم",
                    "زبان‌های خارجی",
                    "برنامه‌نویسی",
                    "کسب و کار",
                    "موفقیت",
                ],
                "کودک و نوجوان": [
                    "قصه کودکانه",
                    "شعر کودکان",
                    "کتاب آموزشی کودک",
                    "کتاب مصور",
                    "کتاب سرگرمی",
                    "کتاب شعر نوجوان",
                ],
                "فرهنگی و هنری": [
                    "هنر و نقاشی",
                    "عکاسی",
                    "تاریخ هنر",
                    "معماری",
                    "موسیقی",
                    "طراحی داخلی",
                ],
            },
            "خودرو و ابزار": {
                "لوازم جانبی خودرو": [
                    "روکش صندلی",
                    "فرش کفی",
                    "نگهدارنده موبایل",
                    "دوربین خودرو",
                    "پاوربانک فندکی",
                    "اسپری تمیزکننده",
                ],
                "ابزار دستی": [
                    "پیچ‌گوشتی",
                    "آچار",
                    "چکش",
                    "متر",
                    "انبردست",
                    "تیغ و رنده",
                ],
                "ابزار برقی": [
                    "دریل",
                    "فرز",
                    "اره برقی",
                    "پولیش ابزار",
                    "جاروبرقی صنعتی",
                    "سنگ‌فرز",
                ],
                "لوازم مراقبت خودرو": [
                    "واکس بدنه",
                    "شامپو بدنه",
                    "واکس داشبورد",
                    "پولیش خودرو",
                    "اسپری لاستیک",
                    "دستمال میکروفایبر",
                ],
            },
        }

        created_count = 0
        processed_count = 0

        for main_category_name, subcategories in categories_structure.items():
            main_category_slug = self.create_unique_slug(main_category_name)

            try:
                main_category = ProductCategoryModel.objects.get(
                    name=main_category_name, parent__isnull=True
                )
                if not main_category.slug or main_category.slug.startswith(
                    "-"
                ):
                    main_category.slug = main_category_slug
                    main_category.save()
                    self.stdout.write(
                        self.style.WARNING(
                            f"Updated slug for existing category: {main_category_name} -> {main_category_slug}"
                        )
                    )
                created = False
            except ProductCategoryModel.DoesNotExist:
                main_category = ProductCategoryModel.objects.create(
                    name=main_category_name, slug=main_category_slug
                )
                created = True

            if created:
                created_count += 1
            processed_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Main category: {main_category_name} (slug: {main_category.slug})"
                )
            )

            for subcategory_name, subsubcategories in subcategories.items():
                subcategory_slug = self.create_unique_slug(subcategory_name)

                try:
                    subcategory = ProductCategoryModel.objects.get(
                        name=subcategory_name, parent=main_category
                    )
                    if not subcategory.slug or subcategory.slug.startswith(
                        "-"
                    ):
                        subcategory.slug = subcategory_slug
                        subcategory.save()
                        self.stdout.write(
                            self.style.WARNING(
                                f"Updated slug for existing subcategory: {subcategory_name} -> {subcategory_slug}"
                            )
                        )
                    created = False
                except ProductCategoryModel.DoesNotExist:
                    subcategory = ProductCategoryModel.objects.create(
                        name=subcategory_name,
                        parent=main_category,
                        slug=subcategory_slug,
                    )
                    created = True

                if created:
                    created_count += 1
                processed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Subcategory: {subcategory_name} (slug: {subcategory.slug})"
                    )
                )

                for subsubcategory_name in subsubcategories:
                    subsubcategory_slug = self.create_unique_slug(
                        subsubcategory_name
                    )

                    try:
                        subsubcategory = ProductCategoryModel.objects.get(
                            name=subsubcategory_name, parent=subcategory
                        )
                        if (
                            not subsubcategory.slug
                            or subsubcategory.slug.startswith("-")
                        ):
                            subsubcategory.slug = subsubcategory_slug
                            subsubcategory.save()
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Updated slug for existing sub-subcategory: {subsubcategory_name} -> {subsubcategory_slug}"
                                )
                            )
                        created = False
                    except ProductCategoryModel.DoesNotExist:
                        subsubcategory = ProductCategoryModel.objects.create(
                            name=subsubcategory_name,
                            parent=subcategory,
                            slug=subsubcategory_slug,
                        )
                        created = True

                    if created:
                        created_count += 1
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    Sub-subcategory: {subsubcategory_name} (slug: {subsubcategory.slug})"
                        )
                    )

        cache_manager = CategoryCache(CategoryProvider())
        cache_manager.invalidate()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted!"
                f"\n• Total categories processed: {processed_count}"
                f"\n• Categories created: {created_count}"
            )
        )
