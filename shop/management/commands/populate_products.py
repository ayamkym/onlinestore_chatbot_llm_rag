import os
import random
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker
from shop.models import Product, Category  # Adjust the import according to your app
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate the database with fake products'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Define the path to the image folder
        IMAGE_FOLDER = os.path.join(settings.BASE_DIR, 'static/images')

        # Sample product types and descriptions
        product_types = [
            ("T-Shirt", "A comfortable and casual t-shirt made from high-quality cotton."),
            ("Jeans", "Stylish denim jeans with a perfect fit for everyday wear."),
            ("Dress", "Elegant dress perfect for both casual and formal occasions."),
            ("Jacket", "Warm and trendy jacket to keep you comfortable in any weather."),
            ("Sweater", "Cozy sweater made from soft and warm materials."),
            ("Skirt", "Fashionable skirt with a flattering design for any body type."),
            ("Blouse", "Chic blouse that can be dressed up or down for any occasion."),
            ("Shorts", "Comfortable and stylish shorts ideal for summer days."),
            ("Shoes", "Trendy and comfortable shoes for everyday wear."),
            ("Hat", "Stylish hat to complete any outfit and protect you from the sun."),
        ]

        def save_image_to_product(product, image_filename):
            image_path = os.path.join(IMAGE_FOLDER, image_filename)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    content = ContentFile(image_file.read())
                    product.image.save(image_filename, content)
                    print(f"Saved {image_filename} to product {product.name}")
            else:
                print(f"Image {image_path} does not exist.")

        def create_product(name, description, price, stock, category, image_filename):
            product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category=category
            )
            product.save()
            save_image_to_product(product, image_filename)

        def create_fake_products(num_products=50):
            # Check if categories exist, and create default ones if not
            if not Category.objects.exists():
                default_categories = ["Men", "Women", "Kids", "Accessories"]
                for category_name in default_categories:
                    Category.objects.create(name=category_name)
                print(f"Created default categories: {', '.join(default_categories)}")

            categories = list(Category.objects.all())

            image_filenames = os.listdir(IMAGE_FOLDER)
            if not image_filenames:
                print(f"No images found in {IMAGE_FOLDER}. Please add some images first.")
                return

            for _ in range(num_products):
                product_type = random.choice(product_types)
                name = product_type[0] + " - " + fake.word().capitalize()
                description = product_type[1]
                price = round(random.uniform(10.0, 100.0), 2)
                stock = random.randint(1, 100)
                category = random.choice(categories)
                image_filename = random.choice(image_filenames)

                create_product(name, description, price, stock, category, image_filename)

            print(f"{num_products} fake products created successfully.")

        create_fake_products(30)
