from .zarinpal import ZarinPalSandboxFactory, ZarinPalProductionFactory


class PaymentFactoryCreator:
    @staticmethod
    def get_factory(gateway_name="zarinpal", sandbox=True):
        factories = {
            "zarinpal": {
                True: ZarinPalSandboxFactory,
                False: ZarinPalProductionFactory,
            }
        }

        factory_class = factories.get(gateway_name, {}).get(sandbox)
        if not factory_class:
            raise ValueError(
                f"Unknown payment gateway: {gateway_name} (sandbox: {sandbox})"
            )

        return factory_class()
