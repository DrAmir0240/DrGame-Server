from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command


class Command(BaseCommand):
    help = "Reset orders app"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app='orders';")

            tables = [
                "orders_productorder",
                "orders_productorderitem",
                "orders_productorderstage",
                "orders_repairorder",
                "orders_repairordercategory",
                "orders_repairorderdevice",
                "orders_repairorderstage",
                "orders_sonyaccountorder",
                "orders_sonyaccountordercategory",
                "orders_sonyaccountorderconsole",
                "orders_sonyaccountorderitem",
                "orders_sonyaccountorderstage",
            ]

            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

        call_command("makemigrations", "orders")
        call_command("migrate", "orders")

        self.stdout.write(self.style.SUCCESS("Orders app reset successfully."))