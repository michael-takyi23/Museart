from django.db import models

# Category
# Product

class Category(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField()

    def _str_(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey('category', null=True, blank=True, on_delete=models.CASCADE)
    Sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, default=0, max_digits=6)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name            
