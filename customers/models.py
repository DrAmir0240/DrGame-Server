from django.db import models

from accounts.models import CustomUser


# Create your models here.

class Customer(models.Model):
    full_name = models.CharField(max_length=50)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer', null=True)
    address = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/customers/')
    is_business = models.BooleanField(default=False)
    discount = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name



