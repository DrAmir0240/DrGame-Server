from rest_framework import serializers
from slugify import slugify

from employees.serializers import EmployeeGameSerializer
from payments.models import CourseOrder
from storage.serializers import GameSerializer
from .models import Cart, CartItem, BlogPost, AboutUs, ContactUs, ContactSubmission, Video, \
    Course, HomeBanner, GameCart, GameCartItem
from storage.models import Product, ProductColor, Game


# cart-item
class ProductColorCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['title']


class ProductCartItemSerializer(serializers.ModelSerializer):
    color = ProductColorCartItemSerializer()

    class Meta:
        model = Product
        fields = ['title', 'main_img', 'color', 'price']


class CartItemReadSerializer(serializers.ModelSerializer):
    product = ProductCartItemSerializer(read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product', 'quantity', 'item_total', 'created_at', 'updated_at']
        read_only_fields = fields

    def get_item_total(self, obj):
        return obj.total_item_price


class CartItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

    def validate(self, data):
        product_item = data['product']
        product = Product.objects.get(pk=product_item.pk)
        if data['quantity'] > product.stock:
            raise serializers.ValidationError({'quantity': 'تعداد درخواستی بیشتر از موجودی انبار است'})
        return data

    def create(self, validated_data):
        cart = self.context['cart']
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            if (cart_item.quantity + quantity) > product.stock:
                raise serializers.ValidationError({'quantity': 'تعداد کل بیشتر از موجودی انبار می‌شود'})
            else:
                cart_item.quantity += quantity
                cart_item.save()

        self.instance = cart_item
        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance


# cart

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemReadSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'cart_items', 'total_price', 'is_deleted']
        read_only_fields = fields

    def get_total_price(self, obj):
        return obj.total_price


class GameCartChoicesSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()


class GameCartItemSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    # game = serializers.SlugRelatedField(read_only=True, slug_field='title')

    class Meta:
        model = GameCartItem
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']


class GameCartSerializer(serializers.ModelSerializer):
    games = GameCartItemSerializer(many=True)

    class Meta:
        model = GameCart
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


######################################

class BlogPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug',
                  'featured_image', 'status', 'created_at', 'published_at'
                  ]
        read_only_fields = ['id', 'published_at', 'author', 'slug']


class BlogPostDetailSerializer(BlogPostListSerializer):
    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ['content', 'meta_description', 'updated_at']


class CreateBlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'author', 'content', 'featured_image', 'meta_description',
                  'status', 'published_at', ]
        read_only_fields = ['id', 'published_at', 'author']

    def create(self, validated_data):
        blog_post = BlogPost(**validated_data)
        blog_post.slug = slugify(blog_post.title, allow_unicode=True)
        blog_post.author = self.context['user']
        blog_post.save()

        return blog_post


class UpdateBlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'author', 'content', 'featured_image', 'meta_description',
                  'status', 'published_at', ]
        read_only_fields = ['id', 'published_at', 'author']

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if 'title' in validated_data:
            instance.slug = slugify(instance.title, allow_unicode=True)

        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        return instance


# contact us & about us

class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = ['id', 'title', 'subtitle', 'content', 'banner_image', 'team_image']
        read_only_fields = ['id']

        extra_kwargs = {
            'title': {'required': False},
            'subtitle': {'required': False},
            'content': {'required': False},
            'banner_image': {'required': False},
            'team_image': {'required': False},

        }


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'address', 'phone', 'email', 'map_embed_code', 'opening_hours', 'facebook_url', 'twitter_url',
                  'instagram_url']
        read_only_fields = ['id']

        extra_kwargs = {
            'address': {'required': False},
            'phone': {'required': False},
            'email': {'required': False},
            'map_embed_code': {'required': False},
            'opening_hours': {'required': False},
            'facebook_url': {'required': False},
            'twitter_url': {'required': False},
            'instagram_url': {'required': False},

        }


class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'user', 'phone', 'email', 'subject', 'message', ]
        read_only_fields = ['user']

    def create(self, validated_data):
        user_id = self.context['user_id']
        return ContactSubmission.objects.create(user_id=user_id, **validated_data)


# Course Serializers

class VideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'slug', 'description', 'video_url', 'status', 'duration', 'priority',
                  'updated_at', ]
        read_only_fields = ['slug']

    def get_video_url(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_authenticated:
            has_purchased = self.context.get('has_purchased', False)
            if has_purchased or user.is_staff:
                if obj.video_file and hasattr(obj.video_file, 'url'):
                    return request.build_absolute_uri(obj.video_file.url)
        return None


class VideoCreateSerializer(VideoSerializer):
    class Meta(VideoSerializer.Meta):
        fields = VideoSerializer.Meta.fields + ['video_file']

    def create(self, validated_data):
        video = Video(**validated_data)
        video.slug = slugify(video.title, allow_unicode=True)
        video.course = self.context.get('course')
        video.save()
        return video


class VideoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'slug', 'description', 'status', 'duration', 'priority',
                  'video_file']
        read_only_fields = ['slug']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'video_file': {'required': False},
            'status': {'required': False},
            'duration': {'required': False},
            'priority': {'required': False},
        }

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.slug = slugify(instance.title, allow_unicode=True)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance


class CourseListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'slug', 'description', 'course_image',
                  'price', 'status', 'updated_at']
        read_only_fields = ['slug']

    def create(self, validated_data):
        course_obj = Course(**validated_data)
        course_obj.slug = slugify(course_obj.title, allow_unicode=True)
        course_obj.save()
        return course_obj


class CourseRetrieveSerializer(serializers.ModelSerializer):
    videos = serializers.SerializerMethodField()
    has_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['title', 'slug', 'description', 'course_image', 'videos', 'price',
                  'status', 'updated_at', 'has_purchased']

    def get_has_purchased(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_staff:
            return True
        if user and user.is_authenticated:
            return CourseOrder.objects.filter(
                customer=user.customer,
                payment_status='paid'
            ).exists()
        return False

    def get_videos(self, obj):
        has_purchased = self.get_has_purchased(obj)
        context = self.context.copy()
        context['has_purchased'] = has_purchased

        return VideoSerializer(
            obj.videos.all(),
            many=True,
            context=context,
        ).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class CourseUpdateSerializer(CourseListCreateSerializer):
    class Meta(CourseListCreateSerializer.Meta):
        fields = CourseListCreateSerializer.Meta.fields
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'course_image': {'required': False},
            'price': {'required': False},
            'status': {'required': False},

        }

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.slug = slugify(instance.title, allow_unicode=True)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields = ['title', 'image', 'is_chosen', 'order', 'created_at', 'updated_at', ]
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        if data.get('is_chosen', False):
            instance_pk = self.instance.pk if self.instance else None
            count_banners = HomeBanner.objects.filter(is_chosen=True).exclude(pk=instance_pk).count()
            if count_banners >= 3:
                raise serializers.ValidationError(
                    {"is_chosen": "Only 3 banners can be selected"}
                )
        return data
