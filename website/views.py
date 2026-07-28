from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.permissions import IsCustomer
from website.filters import GameFilter, StoreProductFilter
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
    StoreProductImage, StoreProductCategory, GameCategory,
)
from website.serializers import (
    AboutUsSerializer,
    GameCartAddItemInputSerializer,
    GameCartAddItemOutputSerializer,
    GameCartDetailSerializer,
    GameCartVolumeSerializer,
    GameDetailSerializer,
    GameImageSerializer,
    GameListSerializer,
    GameSearchSerializer,
    HomeBannerSerializer,
    HomeSectionItemSerializer,
    HomeSectionSerializer,
    MatchedSonyAccountSerializer,
    ProductCartAddItemInputSerializer,
    ProductCartAddItemOutputSerializer,
    ProductCartDetailSerializer,
    ProductCartItemListSerializer,
    StoreProductDetailSerializer,
    StoreProductImageSerializer,
    StoreProductListSerializer,
    StoreProductSearchSerializer, StoreProductCategorySerializer, GameCategorySerializer,
)
from website.services import (
    add_game_to_cart,
    add_product_to_cart,
    get_cart_volume_info,
    get_game_account_stock,
    get_matched_sony_accounts,
    get_product_entity_info,
    remove_game_from_cart,
    remove_product_from_cart,
    resolve_section_items,
)
from drf_spectacular.utils import extend_schema


# ============================================================
# CUSTOMER SECTION — HOME / LANDING
# ============================================================


class HomeBannerListView(generics.ListAPIView):
    serializer_class = HomeBannerSerializer
    queryset = HomeBanner.objects.filter(is_chosen=True).order_by("order")

    @extend_schema(
        tags=["Website — Customer: Home"],
        summary="List active home banners",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HomeSectionListView(generics.ListAPIView):
    serializer_class = HomeSectionSerializer
    queryset = HomeSection.objects.filter(is_deleted=False)

    @extend_schema(
        tags=["Website — Customer: Home"],
        summary="List home sections",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HomeSectionItemListView(generics.ListAPIView):
    serializer_class = HomeSectionItemSerializer

    @extend_schema(
        tags=["Website — Customer: Home"],
        summary="List items for a home section",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        section_id = self.request.query_params.get("section_id")
        if not section_id:
            raise ValidationError("section_id is required")
        return HomeSectionItem.objects.filter(
            section_id=section_id, is_deleted=False, is_active=True
        ).select_related("section")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        resolved = resolve_section_items(queryset)
        serializer = self.get_serializer(resolved, many=True)
        return Response(serializer.data)


class AboutUsListView(generics.ListAPIView):
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.filter(is_deleted=False, is_active=True)

    @extend_schema(
        tags=["Website — Customer: Home"],
        summary="List AboutUs objects",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ============================================================
# CUSTOMER SECTION — PRODUCT STORE
# ============================================================
class StoreProductCategoryList(generics.ListAPIView):
    serializer_class = StoreProductCategorySerializer
    queryset = StoreProductCategory.objects.filter(is_deleted=False)
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Website — Customer: Product Store"],
        summary="List of Product Categories",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StoreProductSearchView(generics.ListAPIView):
    serializer_class = StoreProductSearchSerializer
    queryset = StoreProduct.objects.filter(is_deleted=False).select_related("product")
    filter_backends = [SearchFilter]
    search_fields = [
        "title",
        "product__title",
        "product__description",
        "product__category__title",
    ]

    @extend_schema(
        tags=["Website — Customer: Product Store"],
        summary="Search store products",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StoreProductListView(generics.ListAPIView):
    serializer_class = StoreProductListSerializer
    queryset = StoreProduct.objects.filter(is_deleted=False).select_related("product")
    filter_backends = [DjangoFilterBackend]
    filterset_class = StoreProductFilter

    @extend_schema(
        tags=["Website — Customer: Product Store"],
        summary="List store products with filters",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StoreProductDetailView(generics.RetrieveAPIView):
    serializer_class = StoreProductDetailSerializer
    queryset = StoreProduct.objects.filter(is_deleted=False).select_related(
        "product__category"
    )

    @extend_schema(
        tags=["Website — Customer: Product Store"],
        summary="Retrieve store product detail with stock and color info",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        service_info = get_product_entity_info(instance.product_id)
        serializer = self.get_serializer(instance)
        data = serializer.data
        data["stock_count"] = service_info["stock_count"]
        data["available_colors"] = service_info["available_colors"]
        return Response(data)


class StoreProductImageListView(generics.ListAPIView):
    serializer_class = StoreProductImageSerializer

    @extend_schema(
        tags=["Website — Customer: Product Store"],
        summary="List images for a store product",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        store_product_id = self.request.query_params.get("store_product_id")
        if not store_product_id:
            raise ValidationError("store_product_id is required")
        return StoreProductImage.objects.filter(
            product_id=store_product_id, is_deleted=False
        )


# ============================================================
# CUSTOMER SECTION — GAME STORE
# ============================================================
class GameCategoryList(generics.ListAPIView):
    serializer_class = GameCategorySerializer
    queryset = GameCategory.objects.filter(is_deleted=False)
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Website — Customer: Game Store"],
        summary="List of Game Categories",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GameSearchView(generics.ListAPIView):
    serializer_class = GameSearchSerializer
    queryset = Game.objects.filter(is_deleted=False)
    filter_backends = [SearchFilter]
    search_fields = ["title", "description", "category__title"]

    @extend_schema(
        tags=["Website — Customer: Game Store"],
        summary="Search games",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GameListView(generics.ListAPIView):
    serializer_class = GameListSerializer
    queryset = Game.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend]
    filterset_class = GameFilter

    @extend_schema(
        tags=["Website — Customer: Game Store"],
        summary="List games with filters",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GameDetailView(generics.RetrieveAPIView):
    serializer_class = GameDetailSerializer
    queryset = Game.objects.filter(is_deleted=False)

    @extend_schema(
        tags=["Website — Customer: Game Store"],
        summary="Retrieve game detail with sony account stock count",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        account_stock = get_game_account_stock(instance.id)
        serializer = self.get_serializer(instance)
        data = serializer.data
        data["account_stock"] = account_stock
        return Response(data)


class GameImageListView(generics.ListAPIView):
    serializer_class = GameImageSerializer

    @extend_schema(
        tags=["Website — Customer: Game Store"],
        summary="List images for a game",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        game_id = self.request.query_params.get("game_id")
        if not game_id:
            raise ValidationError("game_id is required")
        return GameImage.objects.filter(game_id=game_id, is_deleted=False)


# ============================================================
# CUSTOMER SECTION — PRODUCT CART
# ============================================================


class ProductCartDetailView(generics.RetrieveAPIView):
    serializer_class = ProductCartDetailSerializer
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Product Cart"],
        summary="Get full product cart with totals",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        cart, _ = ProductCart.objects.get_or_create(user=self.request.user.customer)
        return cart


class ProductCartItemListView(generics.ListAPIView):
    serializer_class = ProductCartItemListSerializer
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Product Cart"],
        summary="List items in the customer's product cart",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return ProductCartItem.objects.filter(
            cart__user=self.request.user.customer,
            is_deleted=False,
        ).select_related("product")


class ProductCartAddItemView(generics.CreateAPIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Product Cart"],
        summary="Add product to cart or increment quantity",
        request=ProductCartAddItemInputSerializer,
        responses={201: ProductCartAddItemOutputSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCartAddItemInputSerializer
        return ProductCartAddItemInputSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = ProductCartAddItemInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        customer = request.user.customer
        item = add_product_to_cart(
            customer,
            store_product_id=input_serializer.validated_data["store_product_id"],
            color=input_serializer.validated_data.get("color"),
        )

        output_serializer = ProductCartAddItemOutputSerializer(item)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ProductCartRemoveItemView(generics.DestroyAPIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Product Cart"],
        summary="Remove product from cart or decrement quantity",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        store_product_id = request.query_params.get("store_product_id")
        if not store_product_id:
            raise ValidationError("store_product_id is required")

        remove_product_from_cart(request.user.customer, int(store_product_id))
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# CUSTOMER SECTION — GAME CART
# ============================================================


class GameCartDetailView(generics.RetrieveAPIView):
    serializer_class = GameCartDetailSerializer
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Game Cart"],
        summary="Get full game cart with volume info",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        cart, _ = GameCart.objects.get_or_create(user=self.request.user.customer)
        return cart


class MatchedSonyAccountListView(generics.ListAPIView):
    serializer_class = MatchedSonyAccountSerializer
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Game Cart"],
        summary="List sony accounts matching customer game cart",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return get_matched_sony_accounts(self.request.user.customer)


class GameCartVolumeView(generics.RetrieveAPIView):
    serializer_class = GameCartVolumeSerializer
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Game Cart"],
        summary="Get total volume and size flag for game cart",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return get_cart_volume_info(self.request.user.customer)


class GameCartAddItemView(generics.CreateAPIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Game Cart"],
        summary="Add game to game cart",
        request=GameCartAddItemInputSerializer,
        responses={201: GameCartAddItemOutputSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        input_serializer = GameCartAddItemInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        item = add_game_to_cart(
            request.user.customer,
            game_id=input_serializer.validated_data["game_id"],
        )

        output_serializer = GameCartAddItemOutputSerializer(item)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GameCartRemoveItemView(generics.DestroyAPIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Website — Customer: Game Cart"],
        summary="Remove game from game cart",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        game_id = request.query_params.get("game_id")
        if not game_id:
            raise ValidationError("game_id is required")

        remove_game_from_cart(request.user.customer, int(game_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
