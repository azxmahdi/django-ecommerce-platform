import logging
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist

from shop.models import ProductVariantModel, ProductStatusType

logger = logging.getLogger(__name__)


class VariantValidator:
    @staticmethod
    def validate(variant_id: str) -> Optional[ProductVariantModel]:
        try:
            return ProductVariantModel.objects.select_related("product").get(
                id=variant_id, product__status=ProductStatusType.PUBLISH.value
            )
        except ObjectDoesNotExist:
            logger.warning(
                "Variant validation failed - not found or not published",
                extra={
                    "variant_id": variant_id,
                    "reason": "not_found_or_not_published",
                },
            )
            return None
        except Exception as e:
            logger.error(
                "Unexpected error in variant validation",
                extra={
                    "variant_id": variant_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return None
