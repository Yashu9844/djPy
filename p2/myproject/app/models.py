from django.db import models
from django.utils import timezone

# Create your models here.
class Chai(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='chai_images/')
    date_added = models.DateTimeField(auto_now_add=timezone.now)
    CHAI_TYPE = (
        ('ML', 'Milk'),
        ('GR', 'Grass'),
        ('CH', 'Chai'),
    )
    type = models.CharField(max_length=2, choices=CHAI_TYPE, default='ML')
