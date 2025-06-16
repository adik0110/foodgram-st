import json
from django.core.management.base import BaseCommand

from api.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from JSON file (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to ingredients.json')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        with open(json_file_path, encoding='utf-8') as file:
            ingredients = json.load(file)

        created = 0
        skipped = 0

        for item in ingredients:
            name = item.get("name")
            unit = item.get("measurement_unit")
            obj, is_created = Ingredient.objects.get_or_create(name=name, measurement_unit=unit)
            if is_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Готово. Добавлено: {created}, пропущено (уже есть): {skipped}."
        ))
