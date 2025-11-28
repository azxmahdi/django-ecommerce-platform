from django.db import models
from django.db.models import Q
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel
from .managers import SearchLogManager


User = get_user_model()


class ProductStatusType(models.IntegerChoices):
    PUBLISH = 1, _("منتشر شده")
    DRAFT = 2, _("عدم انتشار")


class ProductCategoryModel(MPTTModel):
    name = models.CharField(
        max_length=255, unique=True, verbose_name=_("نام دسته")
    )
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, verbose_name=_("اسلاگ")
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("دسته والد"),
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]
        verbose_name = _("دسته‌بندی محصول")
        verbose_name_plural = _("دسته‌بندی‌های محصول")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def is_last_level(self):
        return not self.children.exists()


class ProductModel(TimeStampedModel):
    category = TreeForeignKey(
        ProductCategoryModel,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("دسته‌بندی"),
    )
    name = models.CharField(max_length=255, verbose_name=_("نام"))
    name_en = models.CharField(max_length=255, verbose_name=_("نام انگلیسی"))
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, verbose_name=_("اسلاگ")
    )
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name=_("تصویر")
    )
    status = models.IntegerField(
        choices=ProductStatusType.choices,
        default=ProductStatusType.DRAFT,
        verbose_name=_("وضعیت"),
    )
    total_sold = models.PositiveIntegerField(
        default=0, verbose_name=_("تعداد فروش")
    )
    published_date = models.DateTimeField(verbose_name=_("تاریخ انتشار"))

    class Meta:
        ordering = ["-created_date"]
        indexes = [
            models.Index(
                fields=["slug"],
                name="idx_slug_pub",
                condition=Q(status=ProductStatusType.PUBLISH.value),
            ),
        ]
        verbose_name = _("محصول")
        verbose_name_plural = _("محصولات")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CategoryFeatureModel(models.Model):
    category = models.ForeignKey(
        ProductCategoryModel,
        on_delete=models.CASCADE,
        related_name="category_features",
        verbose_name=_("دسته‌بندی"),
    )
    name = models.CharField(max_length=255, verbose_name=_("نام"))
    is_required = models.BooleanField(default=True, verbose_name=_("اجباری"))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"], name="unique_category_name"
            )
        ]
        verbose_name = _("ویژگی دسته")
        verbose_name_plural = _("ویژگی‌های دسته")

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class FeatureOptionModel(models.Model):
    feature = models.ForeignKey(
        CategoryFeatureModel,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name=_("ویژگی"),
    )
    value = models.CharField(max_length=255, verbose_name=_("مقدار"))

    class Meta:
        verbose_name = _("گزینه ویژگی")
        verbose_name_plural = _("گزینه‌های ویژگی")

    def __str__(self):
        return self.value


class ProductFeatureModel(models.Model):
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("محصول"),
    )
    feature = models.ForeignKey(
        CategoryFeatureModel, on_delete=models.CASCADE, verbose_name=_("ویژگی")
    )
    value = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("مقدار")
    )
    option = models.ForeignKey(
        FeatureOptionModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("گزینه"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "feature"], name="unique_product_feature"
            )
        ]
        verbose_name = _("ویژگی محصول")
        verbose_name_plural = _("ویژگی‌های محصول")

    def __str__(self):
        return f"{self.product.name} - {self.feature.name}"


class AttributeModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("نام"))

    class Meta:
        verbose_name = _("ویژگی")
        verbose_name_plural = _("ویژگی‌ها")

    def __str__(self):
        return self.name


class AttributeValueModel(models.Model):
    attribute = models.ForeignKey(
        AttributeModel,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("ویژگی"),
    )
    value = models.CharField(max_length=100, verbose_name=_("مقدار"))

    class Meta:
        verbose_name = _("مقدار ویژگی")
        verbose_name_plural = _("مقادیر ویژگی")

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariantModel(models.Model):
    product = models.ForeignKey(
        "shop.ProductModel",
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name=_("محصول"),
    )

    attribute_value = models.ForeignKey(
        AttributeValueModel,
        on_delete=models.PROTECT,
        related_name="variants",
        verbose_name=_("مقدار ویژگی"),
    )

    price = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name=_("قیمت")
    )
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("درصد تخفیف"),
    )

    stock = models.PositiveIntegerField(verbose_name=_("موجودی"))

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute_value"],
                name="unique_product_attribute_value",
            )
        ]

        indexes = [
            models.Index(fields=["product"], name="idx_variant_product"),
            models.Index(
                fields=["attribute_value"], name="idx_variant_attr_value"
            ),
            models.Index(fields=["price"], name="idx_variant_price"),
            models.Index(fields=["stock"], name="idx_variant_stock"),
        ]

        ordering = ["product_id", "attribute_value_id"]
        verbose_name = _("تنوع محصول")
        verbose_name_plural = _("تنوع‌های محصول")

    def __str__(self):
        return f"{self.product.name} - {self.attribute_value.attribute.name}: {self.attribute_value.value}"

    @property
    def final_price(self):
        return round(self.price * (100 - (self.discount_percent or 0)) / 100)


class ProductImageModel(TimeStampedModel):
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="product_images",
        verbose_name=_("محصول"),
    )
    file = models.ImageField(
        upload_to="product/extra-img/", verbose_name=_("فایل")
    )

    class Meta:
        verbose_name = _("تصویر محصول")
        verbose_name_plural = _("تصاویر محصول")


class SearchLogModel(TimeStampedModel):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("کاربر"),
    )
    query = models.CharField(max_length=255, verbose_name=_("عبارت جستجو"))

    objects = SearchLogManager()

    class Meta:
        verbose_name = _("لاگ جستجو")
        verbose_name_plural = _("لاگ‌های جستجو")

    def __str__(self):
        return self.query
