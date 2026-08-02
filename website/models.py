from django.core.exceptions import ValidationError
from django.db import models
from uuid import uuid4
from slugify import slugify

from hr.models import Employee
from users.models import CustomUser
from crm.models import Customer
from inventory.models import Product


# Blog
class BlogPostCategory(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Blog Post Categories"

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to="blog/covers/", null=True, blank=True)
    category = models.ForeignKey(
        BlogPostCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    author = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class BlogPostImage(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="blog/images/")
    priority = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.post.title}"


# Game
class GameCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Game(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    category = models.ForeignKey(GameCategory, on_delete=models.CASCADE)
    main_img = models.ImageField(null=True, blank=True, upload_to="main_img/game/")
    volume = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    units_sold = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class GameImage(models.Model):
    img = models.ImageField(null=True, blank=True, upload_to="images/games/")
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, null=True, related_name="game_images"
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.game.title


# Product
class StoreProductCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class StoreProduct(models.Model):
    title = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class StoreProductImage(models.Model):
    img = models.ImageField(null=True, blank=True, upload_to="images/products/")
    product = models.ForeignKey(
        StoreProduct, on_delete=models.CASCADE, null=True, related_name="product_images"
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title


# Shopping
# Product Cart
class ProductCart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} cart"

    @property
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.cart_items.all())


class ProductCartItem(models.Model):
    cart = models.ForeignKey(
        ProductCart, on_delete=models.CASCADE, related_name="cart_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["cart", "product"]]

    @property
    def total_item_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.title} : {self.quantity} for {self.cart}"


# Game Cart
class GameCart(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} game cart"


class GameCartItem(models.Model):
    game_cart = models.ForeignKey(
        GameCart, on_delete=models.CASCADE, related_name="games"
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["game", "game_cart"]]

    def __str__(self):
        return f"{self.game.title} game cart {self.game_cart}"


# Course Models
class Video(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("private", "Private"),
    ]
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    video_file = models.FileField(
        upload_to="videos/",
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)
    duration = models.DurationField()
    priority = models.PositiveIntegerField(unique=True, verbose_name="video order")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"


# Home CMS
class HomeBanner(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title")
    image = models.ImageField(upload_to="banners/", verbose_name="Image")
    is_chosen = models.BooleanField(default=False, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, unique=True, verbose_name="Order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if (
                self.is_chosen
                and HomeBanner.objects.filter(is_chosen=True).exclude(pk=self.pk).count()
                >= 3
        ):
            raise ValidationError("At most 3 banners can be active")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class HomeSection(models.Model):
    title = models.CharField(max_length=100)
    model_content = models.CharField(
        max_length=5000,
        choices=(("game", "بازی"), ("product", "کالا"), ("blog", "بلاگ")),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class HomeSectionItem(models.Model):
    section = models.ForeignKey(
        HomeSection, on_delete=models.CASCADE, related_name="items"
    )
    item_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.section.title} : {self.item_id}"


# About Us
class AboutUs(models.Model):
    title = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logo/")
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    address = models.TextField()
    e_namaad = models.ImageField(upload_to="about_us/", null=True, blank=True)
    e_namaad_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
