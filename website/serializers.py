# from rest_framework import serializers
# from slugify import slugify
#
# from platform_settings.serializers import SoftDeleteSerializerMixin
# from website.models import (
#     ProductCart,
#     ProductCartItem,
#     BlogPost,
#     Video,
#     HomeBanner,
#     GameCart,
#     GameCartItem,
#     Game,
#     GameImage,
# )
# from inventory.models import Product
#
#
# # cart-item
# class ProductCartItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ["title", "main_img", "price"]
#
#
# class CartItemReadSerializer(serializers.ModelSerializer):
#     product = ProductCartItemSerializer(read_only=True)
#     item_total = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ProductCartItem
#         fields = [
#             "id",
#             "product_id",
#             "product",
#             "quantity",
#             "item_total",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = fields
#
#     def get_item_total(self, obj):
#         return obj.total_item_price
#
#
# class CartItemWriteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductCartItem
#         fields = ["product", "quantity"]
#         extra_kwargs = {"quantity": {"min_value": 1}}
#
#     def validate(self, data):
#         product_item = data["product"]
#         product = Product.objects.get(pk=product_item.pk)
#         if data["quantity"] > product.stock:
#             raise serializers.ValidationError(
#                 {"quantity": "تعداد درخواستی بیشتر از موجودی انبار است"}
#             )
#         return data
#
#     def create(self, validated_data):
#         cart = self.context["cart"]
#         product = validated_data.get("product")
#         quantity = validated_data.get("quantity")
#
#         cart_item, created = ProductCartItem.objects.get_or_create(
#             cart=cart, product=product, defaults={"quantity": quantity}
#         )
#         if not created:
#             if (cart_item.quantity + quantity) > product.stock:
#                 raise serializers.ValidationError(
#                     {"quantity": "تعداد کل بیشتر از موجودی انبار می‌شود"}
#                 )
#             else:
#                 cart_item.quantity += quantity
#                 cart_item.save()
#
#         self.instance = cart_item
#         return cart_item
#
#     def update(self, instance, validated_data):
#         instance.quantity = validated_data.get("quantity", instance.quantity)
#         instance.save()
#         return instance
#
#
# # cart
#
#
# class CartSerializer(serializers.ModelSerializer):
#     cart_items = CartItemReadSerializer(many=True, read_only=True)
#     total_price = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ProductCart
#         fields = ["id", "created_at", "cart_items", "total_price", "is_deleted"]
#         read_only_fields = fields
#
#     def get_total_price(self, obj):
#         return obj.total_price
#
#
# class GameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Game
#         fields = "__all__"
#
#
# class GameCartChoicesSerializer(serializers.Serializer):
#     key = serializers.CharField()
#     value = serializers.CharField()
#
#
# class GameCartItemSerializer(serializers.ModelSerializer):
#     game = GameSerializer(read_only=True)
#
#     class Meta:
#         model = GameCartItem
#         fields = "__all__"
#         read_only_fields = ["id", "created_at", "updated_at"]
#
#
# class GameCartSerializer(serializers.ModelSerializer):
#     games = GameCartItemSerializer(many=True)
#     volume = serializers.SerializerMethodField(read_only=True)
#
#     class Meta:
#         model = GameCart
#         fields = "__all__"
#         read_only_fields = ["is_deleted", "created_at", "updated_at"]
#
#     def get_volume(self, obj):
#         volume = sum(game.game.volume for game in obj.games.all())
#         return volume
#
#
# ######################################
#
#
# class BlogPostListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BlogPost
#         fields = [
#             "id",
#             "title",
#             "slug",
#             "featured_image",
#             "status",
#             "created_at",
#             "published_at",
#         ]
#         read_only_fields = ["id", "published_at", "author", "slug"]
#
#
# class BlogPostDetailSerializer(BlogPostListSerializer):
#     class Meta(BlogPostListSerializer.Meta):
#         fields = BlogPostListSerializer.Meta.fields + [
#             "content",
#             "meta_description",
#             "updated_at",
#         ]
#
#
# class CreateBlogPostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BlogPost
#         fields = [
#             "id",
#             "title",
#             "author",
#             "content",
#             "featured_image",
#             "meta_description",
#             "status",
#             "published_at",
#         ]
#         read_only_fields = ["id", "published_at", "author"]
#
#     def create(self, validated_data):
#         blog_post = BlogPost(**validated_data)
#         blog_post.slug = slugify(blog_post.title, allow_unicode=True)
#         blog_post.author = self.context["user"]
#         blog_post.save()
#
#         return blog_post
#
#
# class UpdateBlogPostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BlogPost
#         fields = [
#             "id",
#             "title",
#             "author",
#             "content",
#             "featured_image",
#             "meta_description",
#             "status",
#             "published_at",
#         ]
#         read_only_fields = ["id", "published_at", "author"]
#
#     def update(self, instance, validated_data):
#         tags_data = validated_data.pop("tags", None)
#
#         for field, value in validated_data.items():
#             setattr(instance, field, value)
#
#         if "title" in validated_data:
#             instance.slug = slugify(instance.title, allow_unicode=True)
#
#         instance.save()
#
#         if tags_data is not None:
#             instance.tags.set(tags_data)
#
#         return instance
#
#
# # Course Serializers
#
#
# class VideoSerializer(serializers.ModelSerializer):
#     video_url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Video
#         fields = [
#             "id",
#             "title",
#             "slug",
#             "description",
#             "video_url",
#             "status",
#             "duration",
#             "priority",
#             "updated_at",
#         ]
#         read_only_fields = ["slug"]
#
#     def get_video_url(self, obj):
#         request = self.context.get("request")
#         user = request.user if request else None
#
#         if user and user.is_authenticated:
#             has_purchased = self.context.get("has_purchased", False)
#             if has_purchased or user.is_staff:
#                 if obj.video_file and hasattr(obj.video_file, "url"):
#                     return request.build_absolute_uri(obj.video_file.url)
#         return None
#
#
# class VideoCreateSerializer(VideoSerializer):
#     class Meta(VideoSerializer.Meta):
#         fields = VideoSerializer.Meta.fields + ["video_file"]
#
#     def create(self, validated_data):
#         video = Video(**validated_data)
#         video.slug = slugify(video.title, allow_unicode=True)
#         video.course = self.context.get("course")
#         video.save()
#         return video
#
#
# class VideoUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = [
#             "id",
#             "title",
#             "slug",
#             "description",
#             "status",
#             "duration",
#             "priority",
#             "video_file",
#         ]
#         read_only_fields = ["slug"]
#         extra_kwargs = {
#             "title": {"required": False},
#             "description": {"required": False},
#             "video_file": {"required": False},
#             "status": {"required": False},
#             "duration": {"required": False},
#             "priority": {"required": False},
#         }
#
#     def update(self, instance, validated_data):
#         instance.title = validated_data.get("title", instance.title)
#         instance.slug = slugify(instance.title, allow_unicode=True)
#
#         for field, value in validated_data.items():
#             setattr(instance, field, value)
#
#         instance.save()
#         return instance
#
#
#
#
#
#
# class HomeBannerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HomeBanner
#         fields = [
#             "title",
#             "image",
#             "is_chosen",
#             "order",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = ("created_at", "updated_at")
#
#     def validate(self, data):
#         if data.get("is_chosen", False):
#             instance_pk = self.instance.pk if self.instance else None
#             count_banners = (
#                 HomeBanner.objects.filter(is_chosen=True)
#                 .exclude(pk=instance_pk)
#                 .count()
#             )
#             if count_banners >= 3:
#                 raise serializers.ValidationError(
#                     {"is_chosen": "Only 3 banners can be selected"}
#                 )
#         return data
#
#
# class EmployeeGameImageSerializer(
#     SoftDeleteSerializerMixin, serializers.ModelSerializer
# ):
#     # برای اینکه بتوانیم در آپدیت، id را از ورودی بخوانیم
#     id = serializers.IntegerField(required=False)
#
#     class Meta:
#         model = GameImage
#         # game را از ورودی حذف می‌کنیم؛ اتصال را خودمان انجام می‌دهیم
#         exclude = ["game"]
#
#
# class EmployeeGameSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
#     game_images = EmployeeGameImageSerializer(many=True, required=False)
#
#     class Meta:
#         model = Game
#         fields = "__all__"
#         read_only_fields = ["is_deleted", "created_at", "updated_at"]
#
#     def create(self, validated_data):
#         images_data = validated_data.pop("game_images", [])
#         game = Game.objects.create(**validated_data)
#         # ساخت تصاویر جدید (بدون نیاز به game در ورودی)
#         for img_data in images_data:
#             img_data.pop("id", None)  # ورودی id برای ساخت لازم نیست
#             img_data.pop("game", None)  # امنیت بیشتر
#             # اگر کاربر به اشتباه is_deleted=true فرستاد، ایجاد نکن
#             if img_data.get("is_deleted"):
#                 continue
#             GameImage.objects.create(game=game, **img_data)
#         return game
#
#     def update(self, instance, validated_data):
#         images_data = validated_data.pop("game_images", None)
#
#         # آپدیت فیلدهای خود Game
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         if images_data is not None:
#             # حذف همه عکس‌های قبلی
#             instance.game_images.all().delete()
#             # ساخت عکس‌های جدید
#             for img_data in images_data:
#                 img_data.pop("id", None)
#                 img_data.pop("game", None)
#                 if img_data.get("is_deleted"):
#                     continue
#                 GameImage.objects.create(game=instance, **img_data)
#
#         return instance
#
#
# class GameBulkPriceUpdateSerializer(serializers.Serializer):
#     TYPE_CHOICES = [
#         ("online_ps4", "Online PS4"),
#         ("online_ps5", "Online PS5"),
#         ("offline_ps4", "Offline PS4"),
#         ("offline_ps5", "Offline PS5"),
#         ("data_ps4", "Data PS4"),
#         ("data_ps5", "Data PS5"),
#         ("xbox", "Xbox"),
#         ("nintendo", "Nintendo"),
#     ]
#
#     type = serializers.ChoiceField(choices=TYPE_CHOICES)
#     price = serializers.IntegerField(min_value=0)
#
#     def get_db_field(self):
#         """
#         تبدیل ورودی کاربر به اسم واقعی فیلد دیتابیس
#         """
#         type_map = {
#             "online_ps4": "online_ps4_price",
#             "online_ps5": "online_ps5_price",
#             "offline_ps4": "offline_ps4_price",
#             "offline_ps5": "offline_ps5_price",
#             "data_ps4": "data_ps4_price",
#             "data_ps5": "data_ps5_price",
#             "xbox": "xbox_price",
#             "nintendo": "nintendo_price",
#         }
#         return type_map[self.validated_data["type"]]
#
#
# class EmployeeBlogSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
#     class Meta:
#         model = BlogPost
#         fields = "__all__"
#         read_only_fields = ["created_at", "updated_at"]
#
#
# class GameSearchSerializer(serializers.ModelSerializer):
#     type = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Game
#         fields = ["id", "title", "type"]
#
#     def get_type(self, obj):
#         return "game"
#
#
# class StoreProductSerializer(serializers.ModelSerializer):
#     category_title = serializers.CharField(source="category.title", read_only=True)
#     is_in_wishlist = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Product
#         fields = [
#             "id",
#             "title",
#             "main_img",
#             "price",
#             "stock",
#             "category_id",
#             "category_title",
#             "is_in_wishlist",
#         ]
#
#     def get_is_in_wishlist(self, obj):
#         request = self.context.get("request")
#         if not request or not request.user.is_authenticated:
#             return None
#         try:
#             from crm.models import CustomerWishlist
#             from django.contrib.contenttypes.models import ContentType
#
#             customer = request.user.customer
#             ct = ContentType.objects.get_for_model(obj)
#             return CustomerWishlist.objects.filter(
#                 customer=customer, content_type=ct, object_id=obj.id, is_deleted=False
#             ).exists()
#         except Exception:
#             return None
#
#
# class StoreGameSerializer(serializers.ModelSerializer):
#     is_in_wishlist = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Game
#         fields = [
#             "id",
#             "title",
#             "main_img",
#             "volume",
#             "description",
#             "is_trend",
#             "is_in_wishlist",
#         ]
#
#     def get_is_in_wishlist(self, obj):
#         request = self.context.get("request")
#         if not request or not request.user.is_authenticated:
#             return None
#         try:
#             from crm.models import CustomerWishlist
#             from django.contrib.contenttypes.models import ContentType
#
#             customer = request.user.customer
#             ct = ContentType.objects.get_for_model(obj)
#             return CustomerWishlist.objects.filter(
#                 customer=customer, content_type=ct, object_id=obj.id, is_deleted=False
#             ).exists()
#         except Exception:
#             return None
