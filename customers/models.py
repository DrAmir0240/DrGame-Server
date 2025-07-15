from django.db import models

from accounts.models import CustomUser


# Create your models here.

class Customer(models.Model):
    full_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer', null=True)
    address = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/customers/')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.full_name) if self.full_name else f"Customer {self.id}"

class BusinessCustomer(models.Model):
    full_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='business_customer', null=True)
    license = models.FileField(null=True, blank=True, upload_to='business/license/')
    address = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/customers/')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.full_name) if self.full_name else f"Customer {self.id}"
