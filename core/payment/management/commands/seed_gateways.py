from django.core.management.base import BaseCommand
from django.core.files import File
from pathlib import Path
from payment.models import PaymentGateway, PaymentGatewayType

BASE_DIR = Path(__file__).resolve().parent


class Command(BaseCommand):
    help = "Create initial payment gateways"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete all existing gateways and recreate them",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if force:
            self.stdout.write("Deleting all existing payment gateways...")
            PaymentGateway.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS("All payment gateways deleted.")
            )

        gateways = [
            {
                "name": PaymentGatewayType.ZARINPAL,
                "display_name": "زرین‌پال",
                "image": "./payment_gateways/zarinpal.png",
                "is_active": True,
                "order": 1,
                "config": {
                    "merchant_id": "",
                    "sandbox": True,
                    "callback_url": "/payment/verify/",
                },
            },
        ]

        created_count = 0
        existing_count = 0

        for gateway_data in gateways:
            name = gateway_data["name"]

            if PaymentGateway.objects.filter(name=name).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Gateway already exists: {gateway_data["display_name"]}'
                    )
                )
                existing_count += 1
                continue

            try:
                image_path = BASE_DIR / gateway_data["image"]
                with open(image_path, "rb") as img_f:
                    main_file = File(
                        img_f, name=Path(gateway_data["image"]).name
                    )

                    gateway = PaymentGateway(
                        name=gateway_data["name"],
                        display_name=gateway_data["display_name"],
                        is_active=gateway_data["is_active"],
                        order=gateway_data["order"],
                        config=gateway_data["config"],
                    )
                    gateway.image.save(main_file.name, main_file, save=True)

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created gateway: {gateway.display_name}"
                        )
                    )

            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(
                        f'Image file not found: {gateway_data["image"]}'
                    )
                )
                PaymentGateway.objects.create(
                    name=gateway_data["name"],
                    display_name=gateway_data["display_name"],
                    is_active=gateway_data["is_active"],
                    order=gateway_data["order"],
                    config=gateway_data["config"],
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created gateway (without image): {gateway_data["display_name"]}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted!"
                f"\n• Gateways created: {created_count}"
                f"\n• Existing gateways: {existing_count}"
            )
        )
