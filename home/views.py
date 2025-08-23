from unicodedata import category

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from accounts.auth import CustomJWTAuthentication
from accounts.permissions import IsCustomer, IsEmployee, IsMainManager
from customers.models import Customer
from employees.models import EmployeeHire
from employees.serializers import EmployeeHireSerializer
from payments.models import GAME_ORDER_CONSOLE_TYPE
from storage.models import Game, Product, ProductCategory
from storage.serializers import GameSerializer, ProductSerializer, ProductCategorySerializer
from .serializers import CartSerializer, UpdateBlogPostSerializer, \
    CreateBlogPostSerializer, AboutUsSerializer, ContactUsSerializer, ContactSubmissionSerializer, \
    BlogPostDetailSerializer, BlogPostListSerializer, CourseRetrieveSerializer, \
    CourseListCreateSerializer, CourseUpdateSerializer, VideoSerializer, VideoCreateSerializer, VideoUpdateSerializer, \
    HomeBannerSerializer, CartItemWriteSerializer, GameCartSerializer, GameCartChoicesSerializer
from .models import Cart, CartItem, BlogPost, AboutUs, ContactUs, ContactSubmission, Course, \
    Video, HomeBanner, GameCart, GameCartItem


# trending games

class GameTrendListAPIView(generics.ListAPIView):
    serializer_class = GameSerializer
    queryset = Game.objects.filter(is_trend=True).all()
    permission_classes = [AllowAny]


class GameTrendRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = GameSerializer
    queryset = Game.objects.filter(is_trend=True).all()
    permission_classes = [AllowAny]


# store

class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('color', 'category', 'company').prefetch_related('images').filter(
        is_deleted=False).order_by('-created_at').all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'color', 'company', 'is_deleted']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    ordering = ['-created_at']


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('color', 'category', 'company').prefetch_related('images').filter(
        is_deleted=False).all()
    permission_classes = [AllowAny]


# Game products
class GameListAPIView(generics.ListAPIView):
    serializer_class = GameSerializer
    queryset = Game.objects.filter(is_deleted=False).prefetch_related('game_images').order_by('-created_at').all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'is_trend']
    ordering = ['-created_at']
    permission_classes = [AllowAny]


class GameRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = GameSerializer
    queryset = Game.objects.filter(is_deleted=False).prefetch_related('game_images').all()
    permission_classes = [AllowAny]


# category
class ProductCategoryListAPIView(generics.ListAPIView):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.filter(is_deleted=False).prefetch_related(
        Prefetch('products',
                 queryset=Product.objects.select_related('company', 'color', 'category'))
    ).all()
    filter_backends = [SearchFilter]
    search_fields = ['title', 'products__title']
    permission_classes = [AllowAny]


class ProductCategoryRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.filter(is_deleted=False).prefetch_related(
        Prefetch('products',
                 queryset=Product.objects.select_related('company', 'color', 'category'))
    ).all()
    permission_classes = [AllowAny]


class ProductByCategoryRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cat_id = self.kwargs.get('pro_category')
        return Product.objects.select_related('color', 'category', 'company').prefetch_related('images').filter(
            is_deleted=False, category_id=cat_id).all()


# The most sold games and products

class MostSoldProductsListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Product.objects.select_related('color', 'category', 'company').prefetch_related('images').filter(
            is_deleted=False).order_by('-units_sold')[:10]


class MostSoldGamesListAPIView(generics.ListAPIView):
    serializer_class = GameSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Game.objects.filter(is_deleted=False).prefetch_related('game_images').order_by('-units_sold')[:2]


# cart
class CartAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user.customer, is_deleted=False).prefetch_related(
            'cart_items__product__color')

    def get_object(self):
        cart = self.get_queryset().first()
        if not cart:
            return Cart.objects.create(user=self.request.user.customer)
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        if not cart.cart_items.exists():
            return Response({"detail": "سبد خرید شما خالی است."}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToCartAPIView(generics.CreateAPIView):
    serializer_class = CartItemWriteSerializer
    queryset = CartItem.objects.select_related('cart', 'product__color').none()
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(
            user=request.user.customer,
            is_deleted=False
        )
        serializer = self.get_serializer(data=request.data, context={'cart': cart})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "محصول با موفقیت به سبد خرید اضافه شد.", "data": serializer.data},
                        status=status.HTTP_201_CREATED)


class RemoveFromCartAPIView(generics.DestroyAPIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user.customer)

    def delete(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user.customer, is_deleted=False).first()
        if not cart:
            return Response(
                {"detail": "هیچ سبد خرید فعالی پیدا نشد."},
                status=status.HTTP_404_NOT_FOUND
            )

        product_id = kwargs.get('product_id')
        if not product_id:
            return Response(
                {"detail": "شناسه محصول معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id
            )

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return Response({"detail": "محصول با موفقیت از سبد خرید کم شد."}, status=status.HTTP_204_NO_CONTENT)

            else:
                cart_item.delete()
                return Response({"detail": "محصول با موفقیت از سبد خرید حذف شد."}, status=status.HTTP_204_NO_CONTENT)

        except CartItem.DoesNotExist:
            return Response(
                {"detail": "محصولی در سبد خرید یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": "یک خطا رخ داده است.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# game cart
class GameCartTypeChoices(generics.GenericAPIView):
    serializer_class = GameCartChoicesSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        data = [{'key': k, 'value': v} for k, v in GAME_ORDER_CONSOLE_TYPE]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)


class GameCartRetrieveCreateView(generics.RetrieveAPIView):
    serializer_class = GameCartSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self):
        customer = self.request.user.customer
        cart, created = GameCart.objects.get_or_create(user=customer)
        return cart

    def retrieve(self, request, *args, **kwargs):
        cart = self.get_object()
        serializer = self.get_serializer(cart)

        response_data = serializer.data

        if not cart.games.exists():
            response_data["message"] = "سبد خرید شما خالی است."

        return Response(response_data, status=status.HTTP_200_OK)


class AddGameToCartView(generics.UpdateAPIView):
    serializer_class = GameCartSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self):
        customer = self.request.user.customer
        cart, _ = GameCart.objects.get_or_create(user=customer)
        return cart

    def update(self, request, *args, **kwargs):
        game_id = kwargs.get('game_id')

        if not game_id:
            return Response({'detail': 'شناسه بازی نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            game = Game.objects.get(id=game_id, is_deleted=False)
        except Game.DoesNotExist:
            return Response({'detail': 'بازی یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        cart = self.get_object()

        # بررسی تکراری نبودن آیتم
        if GameCartItem.objects.filter(game_cart=cart, game=game).exists():
            return Response({'detail': 'بازی قبلاً به سبد خرید اضافه شده است.'}, status=status.HTTP_400_BAD_REQUEST)

        # افزودن آیتم به کارت
        GameCartItem.objects.create(
            game_cart=cart,
            game=game,
        )

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveGameFromCartView(generics.DestroyAPIView):
    serializer_class = GameCartSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def delete(self, request, *args, **kwargs):
        customer = request.user.customer
        game_id = kwargs.get('game_id')

        if not game_id:
            return Response({"detail": "شناسه بازی نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

        cart = GameCart.objects.filter(user=customer, is_deleted=False).first()
        if not cart:
            return Response({"detail": "سبد خریدی برای کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({"detail": "بازی مورد نظر وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)

        # حذف رکورد از جدول میانی (GameCartItem)
        cart_item = GameCartItem.objects.filter(game_cart=cart, game=game).first()
        if cart_item:
            cart_item.delete()
            return Response({"detail": "بازی با موفقیت از سبد خرید حذف شد."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "این بازی در سبد خرید وجود ندارد."}, status=status.HTTP_400_BAD_REQUEST)


# blog-post

class BlogPostListAPIView(generics.ListAPIView):
    queryset = BlogPost.objects.select_related('author').filter(
        status='published').all()
    serializer_class = BlogPostListSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at']
    permission_classes = [AllowAny]


class BlogPostRetrieveAPIView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.select_related('author').filter(
        status='published').all()
    serializer_class = BlogPostDetailSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]


class BlogPostCreateAPIView(generics.CreateAPIView):
    queryset = BlogPost.objects.select_related('author').filter(
        status='published').all()
    serializer_class = CreateBlogPostSerializer

    def post(self, request, *args, **kwargs):
        created_serializer = self.serializer_class(data=request.data, context={'user': self.request.user})
        created_serializer.is_valid(raise_exception=True)
        created_item = created_serializer.save()
        serializer = BlogPostDetailSerializer(created_item)
        return Response(serializer.data)


class BlogPostUpdateAPIView(generics.UpdateAPIView):
    queryset = BlogPost.objects.select_related('author').all()
    serializer_class = UpdateBlogPostSerializer
    lookup_field = 'slug'

    # http_method_names = ['patch']
    def put(self, request, *args, **kwargs):
        post_slug = self.kwargs.get('slug')
        post = BlogPost.objects.get(slug=post_slug)
        updated_serializer = self.serializer_class(post, data=request.data)
        updated_serializer.is_valid(raise_exception=True)
        updated_item = updated_serializer.save()
        serializer = BlogPostDetailSerializer(updated_item)
        return Response(serializer.data)


class BlogPostDeleteAPIView(generics.DestroyAPIView):
    queryset = BlogPost.objects.select_related('author').all()
    serializer_class = BlogPostDetailSerializer
    lookup_field = 'slug'


# contact us & about us

class AboutUsRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = AboutUsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        obj = get_object_or_404(AboutUs.objects.filter(is_deleted=False))
        return obj


class AboutUsCreateAPIView(generics.CreateAPIView):
    serializer_class = AboutUsSerializer

    queryset = AboutUs.objects.all()

    def create(self, request, *args, **kwargs):
        if AboutUs.objects.count() >= 1:
            return Response(
                {'error': 'Only one AboutUs entry allowed. Please delete existing entries first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class AboutUsDeleteAPIView(generics.DestroyAPIView):
    serializer_class = AboutUsSerializer

    def get_object(self):
        obj = get_object_or_404(AboutUs.objects.filter(is_deleted=False))
        return obj


class AboutUsUpdateAPIView(generics.UpdateAPIView):
    serializer_class = AboutUsSerializer
    http_method_names = ['put']

    def get_object(self):
        obj = get_object_or_404(AboutUs.objects.filter(is_deleted=False))
        return obj


class ContactUsRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ContactUsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        obj = get_object_or_404(ContactUs.objects.filter(is_deleted=False))
        return obj


class ContactUsCreateAPIView(generics.CreateAPIView):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()

    def create(self, request, *args, **kwargs):
        if ContactUs.objects.count() >= 1:
            return Response(
                {'error': 'Only one ContactUs entry allowed. Please delete existing entries first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class ContactUsUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ContactUsSerializer
    http_method_names = ['put']

    def get_object(self):
        obj = get_object_or_404(ContactUs.objects.filter(is_deleted=False))
        return obj


class ContactUsDeleteAPIView(generics.DestroyAPIView):
    serializer_class = ContactUsSerializer

    def get_object(self):
        obj = get_object_or_404(ContactUs.objects.filter(is_deleted=False))
        return obj


class ContactSubmissionCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]
    serializer_class = ContactSubmissionSerializer
    queryset = ContactSubmission.objects.select_related('user').all()

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}


# Video Course

class CourseListAPIView(generics.ListAPIView):
    serializer_class = CourseListCreateSerializer
    queryset = Course.objects.filter(status='published').prefetch_related('videos')
    permission_classes = [AllowAny]


class CourseRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CourseRetrieveSerializer
    queryset = Course.objects.filter(status='published').prefetch_related(Prefetch(
        'videos',
        queryset=Video.objects.filter(status='published').order_by('priority')
    )).all()
    lookup_field = 'slug'
    permission_classes = [AllowAny]


class CourseCreateAPIView(generics.CreateAPIView):
    serializer_class = CourseListCreateSerializer
    queryset = Course.objects.all()
    permission_classes = [IsEmployee, IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class CourseUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CourseUpdateSerializer
    queryset = Course.objects.all()
    permission_classes = [IsEmployee, IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'slug'


class CourseDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CourseListCreateSerializer
    queryset = Course.objects.all()
    permission_classes = [IsEmployee, IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'slug'


# Video

class VideoListAPIView(generics.ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        queryset = Video.objects.filter(
            course__slug=course_slug,
            status='published'
        ).select_related('course').order_by('priority')

        user = self.request.user
        # بررسی اگر کاربر لاگین کرده و Customer هست
        if hasattr(user, 'customer'):
            customer = user.customer
            if not customer.has_access_to_course:
                return queryset.filter(priority=1)
        return queryset


class VideoRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = VideoSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        queryset = Video.objects.filter(
            course__slug=course_slug,
            status='published'
        ).select_related('course').order_by('priority')

        user = self.request.user
        if hasattr(user, 'customer'):
            customer = user.customer
            if not customer.has_access_to_course:
                return queryset.filter(priority=1)
        return queryset


class VideoCreateAPIView(generics.CreateAPIView):
    serializer_class = VideoCreateSerializer
    permission_classes = [IsEmployee, IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Video.objects.select_related('course').filter(course__slug=course_slug).all()

    def get_serializer_context(self):
        course_slug = self.kwargs.get('course_slug')
        return {'course': Course.objects.get(slug=course_slug)}


class VideoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = VideoUpdateSerializer
    permission_classes = [IsEmployee, IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'slug'

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Video.objects.select_related('course').filter(course__slug=course_slug).all()


class VideoDeleteAPIView(generics.DestroyAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsEmployee, IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'slug'

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Video.objects.select_related('course').filter(course__slug=course_slug).all()


# Banners

class HomeBannerListView(generics.ListAPIView):
    serializer_class = HomeBannerSerializer
    queryset = HomeBanner.objects.all().order_by('order')
    permission_classes = [AllowAny]


class HomeBannerCreateView(generics.CreateAPIView):
    serializer_class = HomeBannerSerializer
    queryset = HomeBanner.objects.all().order_by('order')

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.full_clean()


class HomeBannerDetailView(generics.RetrieveAPIView):
    serializer_class = HomeBannerSerializer
    queryset = HomeBanner.objects.all().order_by('order')
    permission_classes = [AllowAny]


class HomeBannerUpdateView(generics.UpdateAPIView):
    serializer_class = HomeBannerSerializer
    queryset = HomeBanner.objects.all().order_by('order')

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.full_clean()


class HomeBannerDeleteView(generics.DestroyAPIView):
    serializer_class = HomeBannerSerializer
    queryset = HomeBanner.objects.all().order_by('order')


class SendResume(generics.CreateAPIView):
    queryset = EmployeeHire.objects.all()
    serializer_class = EmployeeHireSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]
