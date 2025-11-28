from common.services.base_context_builders import BaseContextBuilder
from order.models import AddressModel, ShippingMethodModel


class CheckoutShippingContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        processors = [self._add_addresses, self._add_shipping_methods]

        return processors

    def get_base_data(self):
        return {}

    def _add_addresses(self):
        self.context["addresses"] = AddressModel.objects.filter(
            user=self.request.user
        )

    def _add_shipping_methods(self):
        self.context["shipping_methods"] = ShippingMethodModel.objects.all()
