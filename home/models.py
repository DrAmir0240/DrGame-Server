from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.conf import settings
from django.db import models
from uuid import uuid4
from django.utils import timezone
from slugify import slugify

from accounts.models import CustomUser
from customers.models import Customer
from storage.models import Product, ProductColor, Game


# Shopping
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.full_name} cart'

    @property
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.cart_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['cart', 'product']]

    @property
    def total_item_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.product.title} : {self.quantity} for {self.cart}'


GAME_CART_TYPE = (
    ('online_ps4', 'online_ps4'),
    ('online_ps5', 'online_ps5'),
    ('offline_ps4', 'offline_ps4'),
    ('offline_ps5', 'offline_ps5'),
    ('data_ps4', 'data_ps4'),
    ('data_ps5', 'data_ps5'),
    ('xbox', 'xbox'),
    ('nintendo', 'nintendo'),
)

class GameCart(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=500, choices=GAME_CART_TYPE, default='online_ps4')
    price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.full_name} game cart'


class GameCartItem(models.Model):
    game_cart = models.ForeignKey(GameCart, on_delete=models.CASCADE, related_name='games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['game', 'game_cart']]

    def __str__(self):
        return f"{self.game.title} game cart {self.game_cart}"


# Blog


class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
    )

    title = models.CharField(max_length=200, unique=True, verbose_name="عنوان")
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts',
                               verbose_name="نویسنده")
    content = models.TextField(verbose_name="محتوا")
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True, verbose_name="تصویر شاخص")
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name="توضیحات متا")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="وضعیت")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    published_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# about us & contact us models

class AboutUs(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    content = models.TextField()

    # Media
    banner_image = models.ImageField(upload_to='about/banners/', null=True, blank=True)
    team_image = models.ImageField(upload_to='about/team/', null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "About Us Page"

    def __str__(self):
        return self.title


class ContactUs(models.Model):
    address = models.CharField(max_length=700)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    map_embed_code = models.TextField(blank=True, help_text="Google Maps iframe code")

    # Business Hours
    opening_hours = models.CharField(max_length=100, default="9:00 AM - 6:00 PM")

    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Contact Page Settings"

    def __str__(self):
        return f'{self.address} - {self.phone}'


class ContactSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=11)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"

    def __str__(self):
        return f'{self.email} : {self.subject}'


# Course Models

class Course(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, )
    description = models.TextField()
    course_image = models.ImageField(upload_to='course/', )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Video(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('private', 'Private'),
    ]
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/', )
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    duration = models.DurationField()
    priority = models.PositiveIntegerField(unique=True, verbose_name='video order')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} - {self.course.title}'


# Banner

class HomeBanner(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    image = models.ImageField(upload_to='banners/', verbose_name="تصویر")
    is_chosen = models.BooleanField(default=False, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, unique=True, verbose_name="ترتیب")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.is_chosen and HomeBanner.objects.filter(is_chosen=True).exclude(pk=self.pk).count() >= 3:
            raise ValidationError("حداکثر ۳ بنر می‌توانند فعال باشند")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
