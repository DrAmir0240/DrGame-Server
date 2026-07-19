from django.db import models

from users.models import CustomUser


# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer', null=True)
    address = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/crm/')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return self.user.full_name()
        return f"customer :{self.id}"


class B2BProfile(models.Model):
    business_title = models.CharField(max_length=100)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='b2b_profile')
    debt_amount_max = models.PositiveIntegerField(default=0)
    uni_id = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.business_title + ': ' + self.customer.user.full_name()
