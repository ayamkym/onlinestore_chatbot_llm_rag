from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

class Product(models.Model):
    name = models.CharField(max_length=255)  # Product name
    description = models.TextField()  # Detailed description of the product
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    stock = models.PositiveIntegerField()  # Number of items in stock
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # Optional product image
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')  # ForeignKey to a Category model
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the product was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the product was last updated

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_id': self.id})

class Category(models.Model):
    name = models.CharField(max_length=255)  # Category name

    def __str__(self):
        return self.name

@receiver(post_save, sender=Product)
def update_embeddings(sender, instance, **kwargs):
    from .embedding_utils import create_and_save_vectorstore
    create_and_save_vectorstore()
