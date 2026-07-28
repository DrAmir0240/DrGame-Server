from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.permissions import IsCustomer, IsEmployee
from website.filters import (
    BlogCategoryFilter,
    CustomerBlogFilter,
    EmployeeBlogFilter,
    EmployeeGameFilter,
    EmployeeStoreProductFilter,
    EmployeeVideoFilter,
    GameFilter,
    StoreProductFilter,
)
from website.models import (
    AboutUs,
    BlogPost,
    BlogPostCategory,
    BlogPostImage,
    Game,
    GameCart,
    GameCartItem,
    GameCategory,
    GameImage,
    HomeBanner,
    HomeSection,
    HomeSectionItem,
    ProductCart,
    ProductCartItem,
    StoreProduct,
    StoreProductCategory,
    StoreProductImage,
    Video,
)
from website.serializers import (
    AboutUsSerializer,
    CustomerBlogCategorySerializer,
    CustomerBlogDetailSerializer,
    CustomerBlogImageSerializer,
    CustomerBlogListSerializer,
    CustomerVideoDetailSerializer,
    CustomerVideoListSerializer,
    EmployeeAboutUsSerializer,
    EmployeeBlogCategorySerializer,
    EmployeeBlogDetailSerializer,
    EmployeeBlogImageSerializer,
    EmployeeBlogListSerializer,
    EmployeeBlogSearchSerializer,
    EmployeeGameCategorySerializer,
    EmployeeGameDetailSerializer,
    EmployeeGameImageSerializer,
    EmployeeGameListSerializer,
    EmployeeGameSearchSerializer,
    EmployeeHomeBannerSerializer,
    EmployeeHomeSectionItemSerializer,
    EmployeeHomeSectionSerializer,
    EmployeeProductEntitySerializer,
    EmployeeStoreProductCategorySerializer,
    EmployeeStoreProductDetailSerializer,
    EmployeeStoreProductImageSerializer,
    EmployeeStoreProductListSerializer,
    EmployeeStoreProductSearchSerializer,
    EmployeeVideoDetailSerializer,
    EmployeeVideoListSerializer,
    EmployeeVideoSearchSerializer,
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
    StoreProductSearchSerializer,
    StoreProductCategorySerializer,
    GameCategorySerializer,
)
from website.services import (
    add_game_to_cart,
    add_product_to_cart,
    get_cart_volume_info,
    get_entities_for_store_product,
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


# ============================================================
# CUSTOMER SECTION — BLOG
# ============================================================


class CustomerBlogCategoryListView(generics.ListAPIView):
    serializer_class = CustomerBlogCategorySerializer
    queryset = BlogPostCategory.objects.filter(is_deleted=False)

    @extend_schema(
        tags=["Website — Customer: Blog"],
        summary="List blog categories",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomerBlogListView(generics.ListAPIView):
    serializer_class = CustomerBlogListSerializer
    queryset = BlogPost.objects.filter(is_deleted=False, status="published")
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomerBlogFilter

    @extend_schema(
        tags=["Website — Customer: Blog"],
        summary="List published blog posts",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomerBlogDetailView(generics.RetrieveAPIView):
    serializer_class = CustomerBlogDetailSerializer
    queryset = BlogPost.objects.filter(is_deleted=False, status="published")

    @extend_schema(
        tags=["Website — Customer: Blog"],
        summary="Retrieve blog post detail",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomerBlogImageListView(generics.ListAPIView):
    serializer_class = CustomerBlogImageSerializer

    @extend_schema(
        tags=["Website — Customer: Blog"],
        summary="List images for a blog post",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        blog_pk = self.kwargs["blog_pk"]
        return BlogPostImage.objects.filter(post_id=blog_pk)


# ============================================================
# CUSTOMER SECTION — VIDEO
# ============================================================


class CustomerVideoListView(generics.ListAPIView):
    serializer_class = CustomerVideoListSerializer
    queryset = Video.objects.filter(status="published").order_by("priority")

    @extend_schema(
        tags=["Website — Customer: Video"],
        summary="List published videos",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomerVideoDetailView(generics.RetrieveAPIView):
    serializer_class = CustomerVideoDetailSerializer
    queryset = Video.objects.filter(status="published")

    @extend_schema(
        tags=["Website — Customer: Video"],
        summary="Retrieve video detail with file URL",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ============================================================
# EMPLOYEE SECTION — HOME
# ============================================================


class EmployeeHomeBannerListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeHomeBannerSerializer
    queryset = HomeBanner.objects.all()
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create home banners",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create home banners",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeHomeBannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeHomeBannerSerializer
    queryset = HomeBanner.objects.all()
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home banner",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home banner",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home banner",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home banner",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EmployeeHomeSectionListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeHomeSectionSerializer
    queryset = HomeSection.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create home sections",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create home sections",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeHomeSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeHomeSectionSerializer
    queryset = HomeSection.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class EmployeeHomeSectionItemListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeHomeSectionItemSerializer
    queryset = HomeSectionItem.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create home section items",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create home section items",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        qs = HomeSectionItem.objects.filter(is_deleted=False)
        section_id = self.request.query_params.get("section_id")
        if section_id:
            qs = qs.filter(section_id=section_id)
        return qs


class EmployeeHomeSectionItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeHomeSectionItemSerializer
    queryset = HomeSectionItem.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section item",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section item",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section item",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete a home section item",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class EmployeeAboutUsListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeAboutUsSerializer
    queryset = AboutUs.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create about-us entries",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="List or create about-us entries",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeAboutUsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeAboutUsSerializer
    queryset = AboutUs.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete an about-us entry",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete an about-us entry",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete an about-us entry",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Home"],
        summary="Retrieve, update or delete an about-us entry",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


# ============================================================
# EMPLOYEE SECTION — PRODUCT STORE
# ============================================================


class EmployeeStoreProductSearchView(generics.ListAPIView):
    serializer_class = EmployeeStoreProductSearchSerializer
    queryset = StoreProduct.objects.filter(is_deleted=False).select_related("product")
    filter_backends = [SearchFilter]
    search_fields = [
        "title",
        "product__title",
        "product__description",
        "product__category__title",
    ]
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Search store products (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeStoreProductCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeStoreProductCategorySerializer
    queryset = StoreProductCategory.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="List or create product categories",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="List or create product categories",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeStoreProductCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeStoreProductCategorySerializer
    queryset = StoreProductCategory.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a product category",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a product category",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a product category",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a product category",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EmployeeStoreProductListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeStoreProductListSerializer
    queryset = StoreProduct.objects.all().select_related("product")
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeStoreProductFilter
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="List or create store products (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="List or create store products (employee)",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeStoreProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeStoreProductDetailSerializer
    queryset = StoreProduct.objects.all()
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class EmployeeProductEntityListView(generics.ListAPIView):
    serializer_class = EmployeeProductEntitySerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="List product entities for a store product",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        store_product_pk = self.kwargs["store_product_pk"]
        return get_entities_for_store_product(store_product_pk)


class EmployeeStoreProductImageListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeStoreProductImageSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="List or create images for a store product",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="List or create images for a store product",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        store_product_pk = self.kwargs["store_product_pk"]
        return StoreProductImage.objects.filter(
            product_id=store_product_pk, is_deleted=False
        )

    def perform_create(self, serializer) -> None:
        store_product_pk = self.kwargs["store_product_pk"]
        serializer.save(product_id=store_product_pk)


class EmployeeStoreProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeStoreProductImageSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product image",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product image",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product image",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Product Store"],
        summary="Retrieve, update or delete a store product image",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        store_product_pk = self.kwargs["store_product_pk"]
        return StoreProductImage.objects.filter(product_id=store_product_pk)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


# ============================================================
# EMPLOYEE SECTION — GAME STORE
# ============================================================


class EmployeeGameSearchView(generics.ListAPIView):
    serializer_class = EmployeeGameSearchSerializer
    queryset = Game.objects.filter(is_deleted=False)
    filter_backends = [SearchFilter]
    search_fields = ["title", "description", "category__title"]
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Search games (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeGameCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeGameCategorySerializer
    queryset = GameCategory.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="List or create game categories",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="List or create game categories",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeGameCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeGameCategorySerializer
    queryset = GameCategory.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game category",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game category",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game category",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game category",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class EmployeeGameListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeGameListSerializer
    queryset = Game.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeGameFilter
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="List or create games (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="List or create games (employee)",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeGameDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeGameDetailSerializer
    queryset = Game.objects.all()
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game (employee)",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game (employee)",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game (employee)",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        account_stock = get_game_account_stock(instance.id)
        serializer = self.get_serializer(instance)
        data = serializer.data
        data["account_stock"] = account_stock
        return Response(data)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class EmployeeGameImageListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeGameImageSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="List or create game images",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="List or create game images",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        game_pk = self.kwargs["game_pk"]
        return GameImage.objects.filter(game_id=game_pk, is_deleted=False)

    def perform_create(self, serializer) -> None:
        game_pk = self.kwargs["game_pk"]
        serializer.save(game_id=game_pk)


class EmployeeGameImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeGameImageSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game image",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game image",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game image",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Game Store"],
        summary="Retrieve, update or delete a game image",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        game_pk = self.kwargs["game_pk"]
        return GameImage.objects.filter(game_id=game_pk)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


# ============================================================
# EMPLOYEE SECTION — BLOG
# ============================================================


class EmployeeBlogSearchView(generics.ListAPIView):
    serializer_class = EmployeeBlogSearchSerializer
    queryset = BlogPost.objects.filter(is_deleted=False)
    filter_backends = [SearchFilter]
    search_fields = [
        "title",
        "body",
        "slug",
        "author__first_name",
        "author__last_name",
        "category__title",
    ]
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Search blog posts (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeBlogCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeBlogCategorySerializer
    queryset = BlogPostCategory.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = BlogCategoryFilter
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="List or create blog categories",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="List or create blog categories",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeBlogCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeBlogCategorySerializer
    queryset = BlogPostCategory.objects.all()
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog category",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog category",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog category",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog category",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class EmployeeBlogListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeBlogListSerializer
    queryset = BlogPost.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeBlogFilter
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="List or create blog posts",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="List or create blog posts",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user.employee)


class EmployeeBlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeBlogDetailSerializer
    queryset = BlogPost.objects.all()
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class EmployeeBlogImageListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeBlogImageSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="List or create blog post images",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="List or create blog post images",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        blog_pk = self.kwargs["blog_pk"]
        return BlogPostImage.objects.filter(post_id=blog_pk)

    def perform_create(self, serializer) -> None:
        blog_pk = self.kwargs["blog_pk"]
        serializer.save(post_id=blog_pk)


class EmployeeBlogImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeBlogImageSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post image",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post image",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post image",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Blog"],
        summary="Retrieve, update or delete a blog post image",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        blog_pk = self.kwargs["blog_pk"]
        return BlogPostImage.objects.filter(post_id=blog_pk)


# ============================================================
# EMPLOYEE SECTION — VIDEO
# ============================================================


class EmployeeVideoSearchView(generics.ListAPIView):
    serializer_class = EmployeeVideoSearchSerializer
    queryset = Video.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ["title", "description", "slug"]
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Video"],
        summary="Search videos (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeVideoListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeVideoListSerializer
    queryset = Video.objects.all().order_by("priority")
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeVideoFilter
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Video"],
        summary="List or create videos (employee)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Video"],
        summary="List or create videos (employee)",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeVideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeVideoDetailSerializer
    queryset = Video.objects.all()
    permission_classes = [IsEmployee]

    @extend_schema(
        tags=["Website — Employee: Video"],
        summary="Retrieve, update or delete a video",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Video"],
        summary="Retrieve, update or delete a video",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Video"],
        summary="Retrieve, update or delete a video",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["Website — Employee: Video"],
        summary="Retrieve, update or delete a video",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
