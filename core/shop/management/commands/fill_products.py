import random
import itertools
from uuid import uuid4
from pathlib import Path
from decimal import Decimal
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from django.utils.text import slugify

from faker import Faker

from shop.models import (
    ProductCategoryModel,
    ProductModel,
    ProductImageModel,
    CategoryFeatureModel,
    FeatureOptionModel,
    ProductFeatureModel,
    ProductStatusType,
    AttributeModel,
    AttributeValueModel,
    ProductVariantModel,
)

BASE_DIR = Path(__file__).resolve().parent
fake_fa = Faker("fa_IR")
fake_en = Faker("en_US")


class Command(BaseCommand):
    help = (
        "For each final subset, create the specified number of products "
        "and initialize all properties of that subset and its parents."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            type=int,
            help="Number of products for each end subcategory",
        )

    def get_category_attributes(self, category_name):

        attributes_mapping = {
            # الکترونیک - موبایل و تبلت
            "گوشی هوشمند": ["رنگ", "حافظه داخلی"],
            "گوشی ساده": ["رنگ", "حافظه داخلی"],
            "تبلت": ["رنگ", "حافظه داخلی"],
            "شارژر": ["رنگ", "طول کابل"],
            "کابل اتصال": ["رنگ", "نوع اتصال"],
            "کیف و کاور": ["رنگ", "جنس"],
            "هندزفری بی‌سیم": ["رنگ", "نوع اتصال"],
            "پاوربانک": ["رنگ", "ظرفیت"],
            # الکترونیک - کامپیوتر و لپ‌تاپ
            "لپ‌تاپ": ["رنگ", "حافظه رم"],
            "کامپیوتر دسکتاپ": ["رنگ", "حافظه رم"],
            "مانیتور": ["رنگ", "اندازه صفحه نمایش"],
            "کیبورد و ماوس": ["رنگ", "نوع اتصال"],
            "کابل HDMI": ["رنگ", "طول"],
            "کارت گرافیک": ["رنگ", "حافظه"],
            "رم کامپیوتر": ["رنگ", "ظرفیت"],
            # الکترونیک - صوتی و تصویری
            "تلویزیون": ["رنگ", "اندازه صفحه نمایش"],
            "سینمای خانگی": ["رنگ", "قدرت"],
            "پخش‌کننده DVD": ["رنگ", "فرمت‌های پشتیبانی"],
            "پروژکتور": ["رنگ", "رزولوشن"],
            "اسپیکر": ["رنگ", "قدرت"],
            "هدفون بی‌سیم": ["رنگ", "باتری"],
            "هدفون سیمی": ["رنگ", "طول کابل"],
            # الکترونیک - لوازم جانبی
            "کابل شارژ": ["رنگ", "طول"],
            "شارژر دیواری": ["رنگ", "وات"],
            "شارژر فندکی": ["رنگ", "وات"],
            "هندزفری سیمی": ["رنگ", "طول کابل"],
            "کیف دوربین": ["رنگ", "جنس"],
            "کارت حافظه": ["رنگ", "ظرفیت"],
            # مد و پوشاک - مردانه
            "پیراهن": ["رنگ", "سایز"],
            "تی‌شرت": ["رنگ", "سایز"],
            "شلوار": ["رنگ", "سایز"],
            "کفش": ["رنگ", "سایز"],
            "کمربند": ["رنگ", "سایز"],
            "ساعت مچی": ["رنگ", "سایز"],
            # مد و پوشاک - زنانه
            "مانتو": ["رنگ", "سایز"],
            "لباس مجلسی": ["رنگ", "سایز"],
            "شلوار": ["رنگ", "سایز"],
            "کفش": ["رنگ", "سایز"],
            "کیف دستی": ["رنگ", "ابعاد"],
            "روسری": ["رنگ", "ابعاد"],
            # مد و پوشاک - بچه‌گانه
            "پیراهن": ["رنگ", "سایز"],
            "شلوار": ["رنگ", "سایز"],
            "سویشرت": ["رنگ", "سایز"],
            "کفش": ["رنگ", "سایز"],
            "ست بادی نوزادی": ["رنگ", "سایز"],
            "هدبند": ["رنگ", "سایز"],
            # مد و پوشاک - اکسسوری
            "گردنبند": ["رنگ", "طول"],
            "دستبند": ["رنگ", "سایز"],
            "عینک آفتابی": ["رنگ", "ابعاد"],
            "کلاه": ["رنگ", "سایز"],
            "کمربند": ["رنگ", "سایز"],
            "شال": ["رنگ", "ابعاد"],
            # خانه و آشپزخانه - لوازم آشپزخانه
            "یخچال": ["رنگ", "ظرفیت"],
            "ظرفشویی": ["رنگ", "ظرفیت"],
            "مایکروویو": ["رنگ", "ظرفیت"],
            "جاروبرقی": ["رنگ", "قدرت"],
            "کتری برقی": ["رنگ", "ظرفیت"],
            "قهوه‌ساز": ["رنگ", "ظرفیت"],
            # خانه و آشپزخانه - دکوراسیون
            "تابلو": ["رنگ", "ابعاد"],
            "قاب عکس": ["رنگ", "ابعاد"],
            "گلدان": ["رنگ", "ابعاد"],
            "فرش": ["رنگ", "ابعاد"],
            "پرده": ["رنگ", "ابعاد"],
            "کنسول و بوفه": ["رنگ", "ابعاد"],
            # خانه و آشپزخانه - خواب و حمام
            "ست حوله": ["رنگ", "سایز"],
            "ملحفه": ["رنگ", "سایز"],
            "بالش": ["رنگ", "سایز"],
            "پتو": ["رنگ", "ابعاد"],
            "سرویس خواب کودک": ["رنگ", "سایز"],
            # خانه و آشپزخانه - سرو و پذیرایی
            "سرویس غذاخوری": ["رنگ", "تعداد تکه"],
            "چای‌خوری": ["رنگ", "تعداد تکه"],
            "قهوه‌خوری": ["رنگ", "تعداد تکه"],
            "لیوان": ["رنگ", "ظرفیت"],
            "بطری": ["رنگ", "ظرفیت"],
            "سینی": ["رنگ", "ابعاد"],
            # زیبایی و سلامت - مراقبت پوست
            "کرم مرطوب‌کننده": ["رنگ", "ظرفیت"],
            "ضدآفتاب": ["رنگ", "ظرفیت"],
            "ماسک صورت": ["رنگ", "ظرفیت"],
            "سرم": ["رنگ", "ظرفیت"],
            "پاک‌کننده": ["رنگ", "ظرفیت"],
            "تونر": ["رنگ", "ظرفیت"],
            # زیبایی و سلامت - مراقبت مو
            "شامپو": ["رنگ", "ظرفیت"],
            "نرم‌کننده": ["رنگ", "ظرفیت"],
            "ماسک مو": ["رنگ", "ظرفیت"],
            "روغن مو": ["رنگ", "ظرفیت"],
            "تونیک پوست سر": ["رنگ", "ظرفیت"],
            "سرم مو": ["رنگ", "ظرفیت"],
            # زیبایی و سلامت - آرایشی
            "کرم پودر": ["رنگ", "ظرفیت"],
            "رژلب": ["رنگ", "ظرفیت"],
            "ریمل": ["رنگ", "ظرفیت"],
            "سایه چشم": ["رنگ", "ظرفیت"],
            "خط چشم": ["رنگ", "ظرفیت"],
            "لاک ناخن": ["رنگ", "ظرفیت"],
            # زیبایی و سلامت - بهداشتی
            "مسواک": ["رنگ", "نوع"],
            "خمیر دندان": ["رنگ", "ظرفیت"],
            "صابون": ["رنگ", "وزن"],
            "شامپو بچه": ["رنگ", "ظرفیت"],
            "دستمال مرطوب": ["رنگ", "تعداد"],
            "ضدعفونی‌کننده": ["رنگ", "ظرفیت"],
            # ورزش و سفر - لوازم ورزشی
            "دمبل": ["رنگ", "وزن"],
            "مت ورزشی": ["رنگ", "ابعاد"],
            "تردمیل": ["رنگ", "قدرت"],
            "دوچرخه ثابت": ["رنگ", "قدرت"],
            "کفش ورزشی": ["رنگ", "سایز"],
            "طناب پرش": ["رنگ", "طول"],
            # ورزش و سفر - پوشاک ورزشی
            "تی‌شرت ورزشی": ["رنگ", "سایز"],
            "شلوارک": ["رنگ", "سایز"],
            "دمپایی": ["رنگ", "سایز"],
            "سویشرت": ["رنگ", "سایز"],
            "کوله‌پشتی": ["رنگ", "ظرفیت"],
            # ورزش و سفر - سفر و کمپینگ
            "چادر": ["رنگ", "ابعاد"],
            "کیسه خواب": ["رنگ", "ابعاد"],
            "چراغ قوه": ["رنگ", "قدرت"],
            "زیرانداز": ["رنگ", "ابعاد"],
            "کوله‌پشتی سفر": ["رنگ", "ظرفیت"],
            "اجاق کوهنوردی": ["رنگ", "قدرت"],
            # ورزش و سفر - ساعت و تناسب اندام
            "ساعت هوشمند": ["رنگ", "ابعاد"],
            "دستبند سلامتی": ["رنگ", "سایز"],
            "ترازو": ["رنگ", "ظرفیت"],
            "پوشیدنی تناسب اندام": ["رنگ", "سایز"],
            "هدفون ورزشی": ["رنگ", "نوع اتصال"],
            # کودک و نوزاد - اسباب‌بازی
            "عروسک": ["رنگ", "ابعاد"],
            "پازل": ["رنگ", "تعداد تکه"],
            "ماشین اسباب‌بازی": ["رنگ", "ابعاد"],
            "بازی فکری": ["رنگ", "تعداد بازیکن"],
            "بلوک ساختنی": ["رنگ", "تعداد تکه"],
            "قطار چوبی": ["رنگ", "ابعاد"],
            # کودک و نوزاد - وسایل آموزشی
            "کتاب آموزشی": ["رنگ", "تعداد صفحه"],
            "لگو": ["رنگ", "تعداد تکه"],
            "دوچرخه بچه‌گانه": ["رنگ", "سایز"],
            "ساعت آموزشی": ["رنگ", "ابعاد"],
            "فلش کارت": ["رنگ", "تعداد کارت"],
            "پازل آموزشی": ["رنگ", "تعداد تکه"],
            # کودک و نوزاد - لباس کودک
            "ست بادی": ["رنگ", "سایز"],
            "شلوار": ["رنگ", "سایز"],
            "پیراهن": ["رنگ", "سایز"],
            "کلاه": ["رنگ", "سایز"],
            "جوراب": ["رنگ", "سایز"],
            "کاپشن": ["رنگ", "سایز"],
            # کودک و نوزاد - سیسمونی
            "روروک": ["رنگ", "ابعاد"],
            "کریر": ["رنگ", "ابعاد"],
            "گهواره": ["رنگ", "ابعاد"],
            "تشک بازی": ["رنگ", "ابعاد"],
            "صندلی ماشین": ["رنگ", "ابعاد"],
            "تخت کنار مادر": ["رنگ", "ابعاد"],
            # کتاب و فرهنگ - رمان و داستان
            "رمان معاصر": ["رنگ", "تعداد صفحه"],
            "داستان کوتاه": ["رنگ", "تعداد صفحه"],
            "مجموعه داستان": ["رنگ", "تعداد صفحه"],
            "رمان نوجوان": ["رنگ", "تعداد صفحه"],
            "رمان خارجی": ["رنگ", "تعداد صفحه"],
            "داستان فلسفی": ["رنگ", "تعداد صفحه"],
            # کتاب و فرهنگ - آموزشی
            "کتاب درسی": ["رنگ", "تعداد صفحه"],
            "مهارت‌های نرم": ["رنگ", "تعداد صفحه"],
            "زبان‌های خارجی": ["رنگ", "تعداد صفحه"],
            "برنامه‌نویسی": ["رنگ", "تعداد صفحه"],
            "کسب و کار": ["رنگ", "تعداد صفحه"],
            "موفقیت": ["رنگ", "تعداد صفحه"],
            # کتاب و فرهنگ - کودک و نوجوان
            "قصه کودکانه": ["رنگ", "تعداد صفحه"],
            "شیر کودکان": ["رنگ", "تعداد صفحه"],
            "کتاب آموزشی کودک": ["رنگ", "تعداد صفحه"],
            "کتاب مصور": ["رنگ", "تعداد صفحه"],
            "کتاب سرگرمی": ["رنگ", "تعداد صفحه"],
            "کتاب شعر نوجوان": ["رنگ", "تعداد صفحه"],
            # کتاب و فرهنگ - فرهنگی و هنری
            "هنر و نقاشی": ["رنگ", "تعداد صفحه"],
            "عکاسی": ["رنگ", "تعداد صفحه"],
            "تاریخ هنر": ["رنگ", "تعداد صفحه"],
            "معماری": ["رنگ", "تعداد صفحه"],
            "موسیقی": ["رنگ", "تعداد صفحه"],
            "طراحی داخلی": ["رنگ", "تعداد صفحه"],
            # خودرو و ابزار - لوازم جانبی خودرو
            "روکش صندلی": ["رنگ", "سایز"],
            "فرش کفی": ["رنگ", "سایز"],
            "نگهدارنده موبایل": ["رنگ", "نوع نصب"],
            "دوربین خودرو": ["رنگ", "رزولوشن"],
            "پاوربانک فندکی": ["رنگ", "ظرفیت"],
            "اسپری تمیزکننده": ["رنگ", "ظرفیت"],
            # خودرو و ابزار - ابزار دستی
            "پیچ‌گوشتی": ["رنگ", "سایز"],
            "آچار": ["رنگ", "سایز"],
            "چکش": ["رنگ", "وزن"],
            "متر": ["رنگ", "طول"],
            "انبردست": ["رنگ", "سایز"],
            "تیغ و رنده": ["رنگ", "سایز"],
            # خودرو و ابزار - ابزار برقی
            "دریل": ["رنگ", "قدرت"],
            "فرز": ["رنگ", "قدرت"],
            "اره برقی": ["رنگ", "طول تیغه"],
            "پولیش": ["رنگ", "قدرت"],
            "جاروبرقی صنعتی": ["رنگ", "قدرت"],
            "سنگ‌فرز": ["رنگ", "قدرت"],
            # خودرو و ابزار - لوازم مراقبت خودرو
            "واکس بدنه": ["رنگ", "ظرفیت"],
            "شامپو بدنه": ["رنگ", "ظرفیت"],
            "واکس داشبورد": ["رنگ", "ظرفیت"],
            "پولیش": ["رنگ", "ظرفیت"],
            "اسپری لاستیک": ["رنگ", "ظرفیت"],
            "دستمال میکروفایبر": ["رنگ", "ابعاد"],
        }

        return attributes_mapping.get(category_name, ["رنگ", "سایز"])

    def get_attribute_values(self, attribute_name):
        values_mapping = {
            "رنگ": ["مشکی", "سفید", "نقره‌ای"],
            "سایز": ["S", "M", "L"],
            "حافظه داخلی": ["64GB", "128GB", "256GB"],
            "طول کابل": ["1 متر", "1.5 متر", "2 متر"],
            "نوع اتصال": ["USB-C", "Micro-USB", "Lightning"],
            "جنس": ["پلاستیک", "فلز", "چرم"],
            "ظرفیت": ["5000mAh", "10000mAh", "20000mAh"],
            "حافظه رم": ["8GB", "16GB", "32GB"],
            "اندازه صفحه نمایش": ["6 اینچ", "6.5 اینچ", "7 اینچ"],
            "طول": ["1 متر", "1.5 متر", "2 متر"],
            "وات": ["18W", "25W", "45W"],
            "قدرت": ["50W", "100W", "200W"],
            "باتری": ["3000mAh", "4000mAh", "5000mAh"],
            "ابعاد": ["کوچک", "متوسط", "بزرگ"],
            "فرمت‌های پشتیبانی": ["MP3", "MP4", "AVI"],
            "رزولوشن": ["HD", "Full HD", "4K"],
            "تعداد تکه": ["2 تکه", "4 تکه", "6 تکه"],
            "وزن": ["1kg", "2kg", "5kg"],
            "نوع": ["نرم", "متوسط", "سفت"],
            "تعداد": ["10 عدد", "20 عدد", "30 عدد"],
            "ظرفیت": ["250ml", "500ml", "1L"],
            "تعداد صفحه": ["100 صفحه", "200 صفحه", "300 صفحه"],
            "نوع نصب": ["چسبی", "مغناطیسی", "مکشی"],
            "رزولوشن": ["720p", "1080p", "4K"],
            "طول تیغه": ["20cm", "30cm", "40cm"],
        }

        return values_mapping.get(attribute_name, ["کوچک", "متوسط", "بزرگ"])

    @transaction.atomic
    def handle(self, *args, **options):
        count_per_leaf = options["count"]

        image_list = [
            "./img/img1.jpg",
            "./img/img2.jpg",
            "./img/img3.jpg",
            "./img/img4.jpg",
            "./img/img5.jpg",
            "./img/img6.jpg",
            "./img/img7.jpg",
            "./img/img8.jpg",
        ]

        leaves = ProductCategoryModel.objects.annotate(
            child_count=Count("children")
        ).filter(child_count=0)
        total_leaves = leaves.count()
        if total_leaves == 0:
            self.stdout.write(self.style.WARNING("No final subset found."))
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Start producing {count_per_leaf} products for each of {total_leaves} end sub-sets..."
            )
        )

        created_total = 0

        for idx, leaf in enumerate(leaves, start=1):
            self.stdout.write(f"[{idx}/{total_leaves}] دسته: {leaf.name}")

            chain = []
            node = leaf
            while node:
                chain.append(node)
                node = node.parent

            features = CategoryFeatureModel.objects.filter(category__in=chain)

            attribute_names = self.get_category_attributes(leaf.name)
            variant_attributes = []

            for attr_name in attribute_names:
                try:
                    attribute = AttributeModel.objects.get(name=attr_name)
                    values = list(
                        AttributeValueModel.objects.filter(
                            attribute=attribute
                        )[:3]
                    )
                    variant_attributes.append((attribute, values))
                except AttributeModel.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Attribute '{attr_name}' not found"
                        )
                    )
                    continue

            for i in range(count_per_leaf):
                fa_word = fake_fa.word().capitalize()
                en_word = fake_en.word().capitalize()
                suffix = uuid4().hex[:6]

                name_fa = f"{leaf.name} {fa_word} {suffix}"
                name_en = f"{en_word} {suffix}"

                slug_base = slugify(name_fa, allow_unicode=True)
                slug = slug_base
                while ProductModel.objects.filter(slug=slug).exists():
                    slug = f"{slug_base}-{random.randint(1,999)}"

                now = timezone.now()
                description = fake_fa.paragraph(nb_sentences=3)

                selected_main = random.choice(image_list)
                with open(BASE_DIR / selected_main, "rb") as img_f:
                    main_file = File(img_f, name=Path(selected_main).name)
                    prod = ProductModel.objects.create(
                        category=leaf,
                        name=name_fa,
                        name_en=name_en,
                        slug=slug,
                        description=description,
                        status=ProductStatusType.PUBLISH.value,
                        published_date=now,
                        image=main_file,
                    )

                created_total += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  Product #{prod.id}: {prod.name}")
                )

                for feat in features:
                    opts = list(
                        FeatureOptionModel.objects.filter(feature=feat)
                    )
                    if opts:
                        choice = random.choice(opts)
                        ProductFeatureModel.objects.create(
                            product=prod,
                            feature=feat,
                            option=choice,
                        )
                    else:
                        val = self._generate_text_value(feat.name)
                        ProductFeatureModel.objects.create(
                            product=prod,
                            feature=feat,
                            value=val,
                        )

                if variant_attributes:
                    self._create_product_variants(prod, variant_attributes)

                for img_path in random.sample(image_list, 5):
                    with open(BASE_DIR / img_path, "rb") as extra_f:
                        extra_file = File(extra_f, name=Path(img_path).name)
                        ProductImageModel.objects.create(
                            product=prod,
                            file=extra_file,
                        )

        self.stdout.write(
            self.style.SUCCESS(f"Done! Total new products: {created_total}")
        )

    Decimal

    def _create_product_variants(self, product, variant_attributes):

        if not variant_attributes:
            return

        all_values_lists = [vals for _, vals in variant_attributes]

        all_combinations = list(itertools.product(*all_values_lists))
        if not all_combinations:
            return

        num_variants = random.randint(2, min(4, len(all_combinations)))
        chosen_combos = random.sample(all_combinations, num_variants)

        for combo in chosen_combos:
            base_price = random.uniform(100_000, 1_000_000)
            discount = random.randint(0, 30)
            final_price = Decimal(
                base_price * (100 - discount) / 100
            ).quantize(Decimal("1"))
            stock = random.randint(1, 100)

            if len(combo) == 1:
                attr_val = combo[0]
                variant = ProductVariantModel.objects.create(
                    product=product,
                    attribute_value=attr_val,
                    price=final_price,
                    discount_percent=discount,
                    stock=stock,
                )
            else:
                variant = ProductVariantModel.objects.create(
                    product=product,
                    price=final_price,
                    discount_percent=discount,
                    stock=stock,
                )
                variant.attributes.add(*combo)

            combo_display = " + ".join([v.value for v in combo])
            self.stdout.write(
                self.style.SUCCESS(
                    f" ↳ Variant: {combo_display} | "
                    f"Price: {final_price:,} | "
                    f"Discount: {discount}% | Stock: {stock}"
                )
            )
