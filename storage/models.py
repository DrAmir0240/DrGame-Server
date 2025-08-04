from django.core.exceptions import ValidationError
from django.db import models

from customers.models import Customer
from employees.models import Employee


# Create your models here.

class ProductCategory(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    img = models.ImageField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    title = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductCompany(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100, unique=True)
    main_img = models.ImageField(null=True, blank=True, upload_to='main_img/products/')
    description = models.TextField(max_length=5000, null=True, blank=True)
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    company = models.ForeignKey(ProductCompany, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(decimal_places=5, max_digits=20)
    stock = models.IntegerField(default=0)
    units_sold = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} {self.color.title}'


class ProductImage(models.Model):
    img = models.ImageField(null=True, blank=True, upload_to='images/products/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='images')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title


class SonyAccountStatus(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SonyAccountBank(models.Model):
    title = models.CharField(max_length=200, unique=True, null=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Game(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    main_img = models.ImageField(null=True, blank=True, upload_to="main_img/game/")
    online_ps4_price = models.IntegerField(null=True, blank=True)
    online_ps5_price = models.IntegerField(null=True, blank=True)
    offline_ps4_price = models.IntegerField(null=True, blank=True)
    offline_ps5_price = models.IntegerField(null=True, blank=True)
    data_ps4_price = models.IntegerField(null=True, blank=True)
    data_ps5_price = models.IntegerField(null=True, blank=True)
    xbox_price = models.IntegerField(null=True, blank=True)
    nintendo_price = models.IntegerField(null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    is_trend = models.BooleanField(default=False)
    units_sold = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.is_trend:
            games_count = Game.objects.filter(is_trend=True).exclude(pk=self.pk).count()
            if games_count >= 4:
                raise ValidationError("حداکثر ۴ بازی می‌توانند ترند باشند")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GameImage(models.Model):
    img = models.ImageField(null=True, blank=True, upload_to='images/games/')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, related_name='game_images')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.game.title


class SonyAccount(models.Model):
    username = models.CharField(max_length=100, unique=True, null=True)
    password = models.CharField(max_length=100, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='employee_accounts')
    two_step = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(SonyAccountStatus, on_delete=models.SET_NULL, null=True, blank=True)
    bank_account_status = models.BooleanField(null=True, blank=True)
    bank_account = models.ForeignKey(SonyAccountBank, on_delete=models.SET_NULL, null=True, blank=True)
    plus = models.BooleanField(null=True, blank=True)
    games = models.ManyToManyField(Game, through='SonyAccountGame', related_name='accounts')
    region = models.CharField(max_length=100, null=True, blank=True, choices=(
        ('America', 'america'),
        ('Europe', 'europe'),
        ('Asia', 'asia'),
        ('Mix', 'mix'),
    ))
    is_owned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class SonyAccountGame(models.Model):
    sony_account = models.ForeignKey(SonyAccount, on_delete=models.CASCADE, related_name='account_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_accounts')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sony_account', 'game']
        indexes = [
            models.Index(fields=['sony_account', 'game']),
        ]

    def __str__(self):
        return f"{self.sony_account} - {self.game}"


class DocCategory(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Document(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='docs/')
    category = models.ForeignKey(DocCategory, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
