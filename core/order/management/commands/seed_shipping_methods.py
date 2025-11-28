from decimal import Decimal
from pathlib import Path
from django.core.files import File
from django.core.management.base import BaseCommand


from order.models import ShippingMethodModel

BASE_DIR = Path(__file__).resolve().parent


class Command(BaseCommand):
    help = "Create initial shipping methods"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete all existing shipping methods and recreate them",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if force:
            self.stdout.write("Deleting all existing shipping methods...")
            ShippingMethodModel.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS("All shipping methods deleted.")
            )

        gateways = [
            {
                "name": "پست",
                "image": "./shipping_method_images/post.png",
                "price": Decimal(40000),
                "estimated_days": 5,
            },
            {
                "name": "تیپاکس",
                "image": "./shipping_method_images/tipax.png",
                "price": Decimal(60000),
                "estimated_days": 3,
            },
        ]

        created_count = 0
        existing_count = 0

        for gateway_data in gateways:
            name = gateway_data["name"]

            if ShippingMethodModel.objects.filter(name=name).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"shipping methods already exists: {name}"
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

                    gateway = ShippingMethodModel(
                        name=gateway_data["name"],
                        price=gateway_data["price"],
                        estimated_days=gateway_data["estimated_days"],
                    )
                    gateway.image.save(main_file.name, main_file, save=True)

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created shipping methods: {gateway.name}"
                        )
                    )

            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(
                        f'Image file not found: {gateway_data["image"]}'
                    )
                )
                gateway = ShippingMethodModel.objects.create(
                    name=gateway_data["name"],
                    price=gateway_data["price"],
                    estimated_days=gateway_data["estimated_days"],
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted!"
                f"\n• shipping methods created: {created_count}"
                f"\n• Existing shipping methods: {existing_count}"
            )
        )
