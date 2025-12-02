from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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
    def __str__(self):
        return self.name

class ChaiReview(models.Model):
    chai = models.ForeignKey(Chai, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date_reviewed = models.DateTimeField(auto_now_add=timezone.now)

    def __str__(self):
        return f'Review for {self.chai.name} by {self.user.username}'
    

## Many to Many

class Store(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    chais = models.ManyToManyField(Chai, related_name='stores')

    def __str__(self):
        return self.name
    


## One to One

class ChaiCertification(models.Model):
    chai = models.OneToOneField(Chai, on_delete=models.CASCADE, related_name='certification')
    certified_by = models.CharField(max_length=100)
    certification_date = models.DateField(default=timezone.now)
    valid_until = models.DateField()
    def __str__(self):
        return f'Certification for {self.chai.name} by {self.certified_by}'