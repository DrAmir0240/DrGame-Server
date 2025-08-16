from rest_framework import serializers

from storage.models import Game, Product, ProductCategory, ProductCompany, ProductColor, ProductImage, GameImage


class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'title']


class ProductCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCompany
        fields = ['id', 'title']


# category serializers
class ProductsForCategorySerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField(source='company.title')
    color = serializers.StringRelatedField(source='color.title')

    class Meta:
        model = Product
        fields = ['id', 'title', 'main_img', 'description', 'color', 'company',
                  'price', 'stock', 'created_at', 'updated_at', ]


class ProductCategorySerializer(serializers.ModelSerializer):
    products = ProductsForCategorySerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = ['id', 'title', 'description', 'img', 'products', 'created_at', 'updated_at', ]


# product serializers

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'img']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(source='category.title')
    company = serializers.StringRelatedField(source='company.title')
    color = serializers.StringRelatedField(source='color.title')
    images = ProductImageSerializer(many=True, read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'main_img', 'images', 'description', 'color', 'category',
                  'company', 'price', 'discounted_price', 'units_sold', 'stock', 'created_at', ]

    def get_discounted_price(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        customer = getattr(request.user, 'customer', None)
        if customer and customer.discount > 0:
            discount_percent = customer.discount
            discounted_price = int(obj.price) * (1 - discount_percent / 100)
            return int(discounted_price)
        return None


class GameImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameImage
        fields = ['id', 'img']


class GameSerializer(serializers.ModelSerializer):
    game_images = GameImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'title', 'main_img', 'game_images', 'description', 'is_trend', 'units_sold',
                  'online_ps4_price', 'online_ps5_price', 'offline_ps4_price',
                  'offline_ps5_price', 'data_ps4_price', 'data_ps5_price',
                  'xbox_price', 'nintendo_price',
                  'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('is_trend', False):
            instance_pk = self.instance.pk if self.instance else None
            trending_count = Game.objects.filter(is_trend=True).exclude(pk=instance_pk).count()

            if trending_count >= 4:
                raise serializers.ValidationError(
                    {"is_trend": "Only 4 games can be marked as trending."}
                )
        return data
