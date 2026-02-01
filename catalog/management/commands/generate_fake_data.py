import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from catalog.models import Category, Product, Attribute, AttributeValue
from faker import Faker

User = get_user_model()


class Command(BaseCommand):
    help = 'Генерация фейковых данных для каталога'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=int,
            default=10,
            help='Количество категорий (по умолчанию: 10)'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Количество товаров (по умолчанию: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед генерацией'
        )
        parser.add_argument(  # Добавим опцию для атрибутов
            '--no-attributes',
            action='store_true',
            help='Не добавлять атрибуты к товарам'
        )

    def handle(self, *args, **options):
        fake = Faker('ru_RU')

        categories_count = options['categories']
        products_count = options['products']
        clear_existing = options['clear']
        no_attributes = options['no_attributes']

        self.stdout.write(self.style.SUCCESS(
            f'Генерация {categories_count} категорий и {products_count} товаров...'
        ))
        if no_attributes:
            self.stdout.write('Атрибуты не будут добавляться к товарам')

        if clear_existing:
            self.stdout.write('Очистка существующих данных...')

            # Сначала удаляем товары (без каскадного удаления связей)
            Product.objects.all().delete()

            # Затем значения атрибутов и атрибуты
            AttributeValue.objects.all().delete()
            Attribute.objects.all().delete()

            # Удаляем категории (MPTT автоматически перестроит дерево)
            Category.objects.all().delete()

            # Очищаем таблицу связей ManyToMany если она существует
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("DELETE FROM catalog_product_attributes")
                    self.stdout.write('Очищена таблица связей товаров с атрибутами')
                except Exception:
                    self.stdout.write('Таблица связей товаров с атрибутами не существует')

        # 1. Создаём атрибуты (всё равно создаём для будущего использования)
        self.stdout.write('Создание атрибутов...')
        attributes_data = [
            {'name': 'Цвет', 'code': 'color', 'filter_type': 'multi'},
            {'name': 'Размер', 'code': 'size', 'filter_type': 'multi'},
            {'name': 'Материал', 'code': 'material', 'filter_type': 'multi'},
            {'name': 'Бренд', 'code': 'brand', 'filter_type': 'multi'},
            {'name': 'Вес', 'code': 'weight', 'filter_type': 'range', 'unit': 'кг'},
            {'name': 'Гарантия', 'code': 'warranty', 'filter_type': 'range', 'unit': 'мес'},
        ]

        attributes = {}
        for attr_data in attributes_data:
            attr, created = Attribute.objects.get_or_create(
                code=attr_data['code'],
                defaults=attr_data
            )
            attributes[attr.code] = attr

        # 2. Создаём значения атрибутов (тоже создаём для будущего)
        self.stdout.write('Создание значений атрибутов...')
        attribute_values = {}

        # Цвета
        colors = ['Красный', 'Синий', 'Зеленый', 'Черный', 'Белый', 'Желтый', 'Фиолетовый']
        for i, color in enumerate(colors):
            val, created = AttributeValue.objects.get_or_create(
                attribute=attributes['color'],
                code=f'color_{i}',
                defaults={'value': color, 'order': i}
            )
            attribute_values.setdefault('color', []).append(val)

        # Размеры
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        for i, size in enumerate(sizes):
            val, created = AttributeValue.objects.get_or_create(
                attribute=attributes['size'],
                code=f'size_{i}',
                defaults={'value': size, 'order': i}
            )
            attribute_values.setdefault('size', []).append(val)

        # Материалы
        materials = ['Хлопок', 'Полиэстер', 'Шерсть', 'Кожа', 'Дерево', 'Металл', 'Пластик']
        for i, material in enumerate(materials):
            val, created = AttributeValue.objects.get_or_create(
                attribute=attributes['material'],
                code=f'material_{i}',
                defaults={'value': material, 'order': i}
            )
            attribute_values.setdefault('material', []).append(val)

        # Бренды
        brands = ['Nike', 'Adidas', 'Apple', 'Samsung', 'Sony', 'LG', 'Bosch', 'Philips']
        for i, brand in enumerate(brands):
            val, created = AttributeValue.objects.get_or_create(
                attribute=attributes['brand'],
                code=f'brand_{i}',
                defaults={'value': brand, 'order': i}
            )
            attribute_values.setdefault('brand', []).append(val)

        # 3. Создаём категории с иерархией
        self.stdout.write('Создание категорий...')

        # Корневые категории
        root_categories = []
        root_names = ['Электроника', 'Одежда', 'Бытовая техника', 'Мебель', 'Книги']

        for i, name in enumerate(root_names):
            cat, created = Category.objects.get_or_create(
                slug=f'category-root-{i}',
                defaults={
                    'name': name,
                    'parent': None,  # parent=None автоматически делает категорию корневой
                    'description': fake.text(max_nb_chars=200),
                }
            )
            root_categories.append(cat)

        # Подкатегории для каждой корневой
        all_categories = root_categories.copy()

        for root_cat in root_categories:
            # 3-5 подкатегорий для каждой корневой
            for j in range(random.randint(3, 5)):
                cat_name = f'{fake.word().capitalize()}'
                slug = f'{root_cat.slug}-sub-{j}'

                cat, created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': cat_name,
                        'parent': root_cat,
                        'description': fake.text(max_nb_chars=150),
                    }
                )
                all_categories.append(cat)

                # Вложенные подкатегории (уровень 3)
                if random.choice([True, False]):  # 50% chance
                    for k in range(random.randint(2, 4)):
                        sub_cat_name = f'{fake.word().capitalize()}'
                        sub_slug = f'{slug}-deep-{k}'

                        sub_cat, created = Category.objects.get_or_create(
                            slug=sub_slug,
                            defaults={
                                'name': sub_cat_name,
                                'parent': cat,
                                'description': fake.text(max_nb_chars=100),
                            }
                        )
                        all_categories.append(sub_cat)

        # 4. Создаём товары
        self.stdout.write(f'Создание {products_count} товаров...')

        product_names = [
            'Смартфон', 'Ноутбук', 'Наушники', 'Футболка', 'Джинсы', 'Куртка',
            'Холодильник', 'Телевизор', 'Стиральная машина', 'Диван', 'Кресло',
            'Стол', 'Стул', 'Книга', 'Игрушка', 'Инструмент', 'Посуда', 'Обувь'
        ]

        adjectives = [
            'Профессиональный', 'Домашний', 'Портативный', 'Умный', 'Энергосберегающий',
            'Стильный', 'Компактный', 'Мощный', 'Легкий', 'Прочный', 'Эргономичный'
        ]

        for i in range(products_count):
            # Выбираем случайную категорию
            category = random.choice(all_categories)

            # Генерируем название
            base_name = random.choice(product_names)
            adjective = random.choice(adjectives)
            model = fake.bothify(text='??-###')
            product_name = f'{adjective} {base_name} {model}'

            # Генерируем данные
            price = random.randint(100, 100000)
            has_discount = random.choice([True, False, False])  # 33% chance
            old_price = price * random.uniform(1.2, 2.0) if has_discount else None

            quantity = random.randint(0, 100)
            in_stock = quantity > 0

            # Создаём товар
            product = Product.objects.create(
                name=product_name,
                slug=f'product-{i}-{fake.lexify(text="????")}',
                category=category,
                price=price,
                old_price=old_price,
                sku=f'SKU-{fake.bothify(text="????-####")}',
                short_description=fake.text(max_nb_chars=100),
                description=fake.text(max_nb_chars=500),
                quantity=quantity,
                in_stock=in_stock,
                is_active=random.choice([True, True, True, False])  # 75% активных
            )

            # Добавляем случайные атрибуты (ТОЛЬКО если не отключено и таблица существует)
            if not no_attributes and random.choice([True, False]):  # 50% chance
                try:
                    # Цвет
                    if attribute_values.get('color'):
                        product.attributes.add(random.choice(attribute_values['color']))

                    # Размер (только для одежды/обуви)
                    if 'Одежда' in category.name or 'Обувь' in category.name:
                        if attribute_values.get('size'):
                            product.attributes.add(random.choice(attribute_values['size']))

                    # Бренд
                    if attribute_values.get('brand'):
                        product.attributes.add(random.choice(attribute_values['brand']))

                    # Материал
                    if random.choice([True, False]):
                        if attribute_values.get('material'):
                            product.attributes.add(random.choice(attribute_values['material']))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f'Не удалось добавить атрибуты к товару {product_name}: {e}'
                    ))
                    self.stdout.write(self.style.WARNING(
                        'Пропускаем атрибуты. Запустите с --no-attributes чтобы отключить их.'
                    ))

            if (i + 1) % 10 == 0:
                self.stdout.write(f'Создано {i + 1}/{products_count} товаров...')

        # 5. Сводка
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('ГЕНЕРАЦИЯ ЗАВЕРШЕНА'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Категории: {Category.objects.count()}')
        self.stdout.write(f'Товары: {Product.objects.count()}')
        self.stdout.write(f'Атрибуты: {Attribute.objects.count()}')
        self.stdout.write(f'Значения атрибутов: {AttributeValue.objects.count()}')
        self.stdout.write(self.style.SUCCESS('=' * 50))

        # Создаём тестового пользователя если нужно
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='test123',
                is_external=False
            )
            self.stdout.write(self.style.SUCCESS('Создан тестовый пользователь: testuser / test123'))