from django.db import models


# Create your models here.
class Supplier(models.Model):
    TYPE_CHOICES = (
        ('real', 'حقیقی'),
        ('legal', 'حقوقی'),
    )

    # اطلاعات پایه
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='real')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # اطلاعات مالی
    account_number = models.CharField(max_length=50, blank=True, null=True, help_text="شماره حساب")
    sheba = models.CharField(max_length=30, blank=True, null=True, help_text="شماره شبا")

    # اطلاعات تجاری
    national_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="کد ملی (حقیقی) یا شناسه ملی (حقوقی)"
    )
    tax_id = models.CharField(max_length=20, blank=True, null=True, help_text="شناسه مالیاتی")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'


class ProductCategory(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    img = models.ImageField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100, unique=True)
    main_img = models.ImageField(null=True, blank=True, upload_to='main_img/products/')
    description = models.TextField(max_length=5000, null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(decimal_places=5, max_digits=20)
    stock = models.IntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0, help_text="حداقل موجودی")
    supplier = models.ManyToManyField(Supplier, related_name='products')
    units_sold = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'


class ProductImage(models.Model):
    img = models.ImageField(null=True, blank=True, upload_to='images/products/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='images')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title


class ProductEntity(models.Model):
    uni_id = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='entities')
    color = models.CharField(max_length=10, blank=True, null=True)
    main_img = models.ImageField(null=True, blank=True, upload_to='main_img/products/entities/')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.uni_id + ' ' + self.product.title


class InventoryMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    product_entity = models.ForeignKey(ProductEntity, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='inventory_movements')
    direction = models.CharField(max_length=10, choices=(('in', 'ورودی'), ('out', 'خروجی'), ('rejected', 'برگشتی')))
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.product_entity:
            return self.product_entity.uni_id
        return self.product.title
