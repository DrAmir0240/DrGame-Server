from rest_framework import serializers

from website.models import (
    AboutUs,
    Game,
    GameCart,
    GameCartItem,
    GameImage,
    HomeBanner,
    HomeSection,
    HomeSectionItem,
    ProductCart,
    ProductCartItem,
    StoreProduct,
    StoreProductImage, GameCategory, StoreProductCategory, BlogPost,
)


# ============================================================
# CUSTOMER SECTION — HOME / LANDING
# ============================================================


class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields = ["id", "title", "image", "order"]


class HomeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSection
        fields = ["id", "title", "model_content"]


class HomeSectionItemSerializer(serializers.ModelSerializer):
    section_title = serializers.SerializerMethodField()
    item_title = serializers.SerializerMethodField()
    item_description = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()
    item_image = serializers.SerializerMethodField()

    class Meta:
        model = HomeSectionItem
        fields = ["section", "section_title", "item_id",
                  "item_title", "item_description", "item_image",
                  "item_type", "is_active"]

    def get_model(self, obj):
        if obj.section.type == "game":
            qs = Game.objects.filter(id=obj.item_id)
        if obj.section.type == "product":
            qs = StoreProduct.objects.filter(id=obj.item_id)
        if obj.section.type == "blog":
            qs = BlogPost.objects.filter(id=obj.item_id)
        else:
            qs = None
        return qs

    def get_section_title(self, obj):
        return obj.section.title if obj.section else None

    def get_item_title(self, obj):
        model = self.get_model(obj)
        if hasattr(model, "title"):
            return model.title
        return None

    def get_item_description(self, obj):
        model = self.get_model(obj)
        if hasattr(model, "description"):
            return model.description
        return None

    def get_item_image(self, obj):
        model = self.get_model(obj)
        if hasattr(model, "image"):
            if hasattr(model.image, "url"):
                return model.image.url
        return None

    def get_item_type(self, obj):
        return obj.section.type if obj.section else None


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = [
            "id",
            "title",
            "logo",
            "phone_number",
            "email",
            "address",
            "e_namaad",
            "e_namaad_url",
        ]


# ============================================================
# CUSTOMER SECTION — PRODUCT STORE
# ============================================================
class StoreProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProductCategory
        fields = ["id", "title"]


class StoreProductSearchSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title")
    product_main_img = serializers.ImageField(source="product.main_img")

    class Meta:
        model = StoreProduct
        fields = ["id", "title", "product_id", "product_title", "product_main_img"]


class StoreProductListSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title")
    product_main_img = serializers.ImageField(source="product.main_img")
    product_price = serializers.DecimalField(
        source="product.price", max_digits=20, decimal_places=5
    )
    product_stock = serializers.IntegerField(source="product.stock")

    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "title",
            "product_id",
            "product_title",
            "product_main_img",
            "product_price",
            "product_stock",
        ]


class StoreProductDetailSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id")
    product_title = serializers.CharField(source="product.title")
    product_main_img = serializers.ImageField(source="product.main_img")
    product_description = serializers.CharField(source="product.description")
    product_price = serializers.DecimalField(
        source="product.price", max_digits=20, decimal_places=5
    )
    product_category_id = serializers.IntegerField(source="product.category_id")
    product_category_title = serializers.CharField(
        source="product.category.title", allow_null=True
    )
    stock_count = serializers.IntegerField(read_only=True)
    available_colors = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )

    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "title",
            "product_id",
            "product_title",
            "product_main_img",
            "product_description",
            "product_price",
            "product_category_id",
            "product_category_title",
            "stock_count",
            "available_colors",
        ]


class StoreProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProductImage
        fields = ["id", "img", "product_id"]


# ============================================================
# CUSTOMER SECTION — GAME STORE
# ============================================================
class GameCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GameCategory
        fields = ["id", "title"]


class GameSearchSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source="category.title", allow_null=True)

    class Meta:
        model = Game
        fields = ["id", "title", "main_img", "category_id", "category_title"]


class GameListSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source="category.title", allow_null=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "title",
            "main_img",
            "description",
            "volume",
            "units_sold",
            "category_id",
            "category_title",
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source="category.title", allow_null=True)
    account_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "title",
            "main_img",
            "description",
            "volume",
            "units_sold",
            "category_id",
            "category_title",
            "account_stock",
        ]


class GameImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameImage
        fields = ["id", "img", "game_id"]


# ============================================================
# CUSTOMER SECTION — PRODUCT CART
# ============================================================


class ProductCartItemDetailSerializer(serializers.ModelSerializer):
    store_product_id = serializers.SerializerMethodField()
    store_product_title = serializers.SerializerMethodField()
    product_title = serializers.CharField(source="product.title")
    product_main_img = serializers.ImageField(source="product.main_img")
    unit_price = serializers.DecimalField(
        source="product.price", max_digits=20, decimal_places=5
    )
    total_item_price = serializers.DecimalField(
        max_digits=20, decimal_places=5, read_only=True
    )

    class Meta:
        model = ProductCartItem
        fields = [
            "id",
            "product_id",
            "store_product_id",
            "store_product_title",
            "product_title",
            "product_main_img",
            "unit_price",
            "quantity",
            "total_item_price",
            "color",
        ]

    def get_store_product_id(self, obj):
        sp = StoreProduct.objects.filter(product=obj.product, is_deleted=False).first()
        return sp.id if sp else None

    def get_store_product_title(self, obj):
        sp = StoreProduct.objects.filter(product=obj.product, is_deleted=False).first()
        return sp.title if sp else None


class ProductCartDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(
        max_digits=20, decimal_places=5, read_only=True
    )
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCart
        fields = ["id", "created_at", "items", "total_price", "item_count"]

    def get_items(self, obj):
        items = obj.cart_items.filter(is_deleted=False)
        return ProductCartItemDetailSerializer(items, many=True).data

    def get_item_count(self, obj):
        return obj.cart_items.filter(is_deleted=False).count()


class ProductCartItemListSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title")
    total_item_price = serializers.DecimalField(
        max_digits=20, decimal_places=5, read_only=True
    )

    class Meta:
        model = ProductCartItem
        fields = [
            "id",
            "product_id",
            "product_title",
            "quantity",
            "total_item_price",
            "color",
        ]


class ProductCartAddItemInputSerializer(serializers.Serializer):
    store_product_id = serializers.IntegerField()
    color = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ProductCartAddItemOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCartItem
        fields = ["id", "product_id", "quantity", "color"]


# ============================================================
# CUSTOMER SECTION — GAME CART
# ============================================================


class GameCartItemGameSerializer(serializers.ModelSerializer):
    game_id = serializers.IntegerField(source="game.id")
    game_title = serializers.CharField(source="game.title")
    game_main_img = serializers.ImageField(source="game.main_img")
    game_volume = serializers.IntegerField(source="game.volume")

    class Meta:
        model = GameCartItem
        fields = ["id", "game_id", "game_title", "game_main_img", "game_volume"]


class GameCartDetailSerializer(serializers.ModelSerializer):
    games = GameCartItemGameSerializer(many=True, read_only=True)
    total_volume = serializers.SerializerMethodField()
    volume_flag = serializers.SerializerMethodField()

    class Meta:
        model = GameCart
        fields = ["id", "created_at", "games", "total_volume", "volume_flag"]

    def get_total_volume(self, obj):
        from website.services import get_cart_volume_info

        customer = self.context.get("request").user.customer
        info = get_cart_volume_info(customer)
        return info["total_volume"]

    def get_volume_flag(self, obj):
        from website.services import get_cart_volume_info

        customer = self.context.get("request").user.customer
        info = get_cart_volume_info(customer)
        return info["volume_flag"]


class MatchedSonyAccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    price = serializers.IntegerField(allow_null=True)
    plus = serializers.BooleanField(allow_null=True)
    region = serializers.CharField(allow_null=True)
    status_id = serializers.SerializerMethodField()
    status_title = serializers.SerializerMethodField()
    match_count = serializers.IntegerField()

    def get_status_id(self, obj):
        return obj.status_id if hasattr(obj, "status_id") else None

    def get_status_title(self, obj):
        return obj.status.title if obj.status else None


class GameCartVolumeSerializer(serializers.Serializer):
    total_volume = serializers.IntegerField()
    volume_flag = serializers.CharField()


class GameCartAddItemInputSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()


class GameCartAddItemOutputSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source="game.title")

    class Meta:
        model = GameCartItem
        fields = ["id", "game_id", "game_title"]
