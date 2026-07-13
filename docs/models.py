from django.db import models

from hr.models import Employee


# Create your models here.
class DocCategory(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DocSubCategory(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    category = models.ForeignKey(DocCategory, on_delete=models.SET_NULL, null=True,
                                 related_name='sub_cats')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Document(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='docs/')
    category = models.ForeignKey(DocSubCategory, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class RealAssetsCategory(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class RealAssetsSubCategory(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    category = models.ForeignKey(RealAssetsCategory, on_delete=models.SET_NULL, null=True,
                                 related_name='sub_cats')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class RealAssets(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to='real_assets/photos/', blank=True, null=True)
    category = models.ForeignKey(RealAssetsSubCategory, on_delete=models.SET_NULL, null=True,
                                 related_name='real_assets')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='real_assets')
    price = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
