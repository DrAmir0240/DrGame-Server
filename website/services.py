from __future__ import annotations

from django.db.models import Count, Q, QuerySet, Sum
from django.shortcuts import get_object_or_404

from crm.models import Customer
from inventory.models import Product, ProductEntity
from psn.models import SonyAccount
from website.models import (
    Game,
    GameCart,
    GameCartItem,
    ProductCart,
    ProductCartItem,
    StoreProduct,
)


def resolve_section_items(items: QuerySet) -> list[dict]:
    result = []
    from website.models import HomeSectionItem

    items = items.select_related("section")
    for item in items:
        section = item.section
        model_content = section.model_content
        resolved = {
            "item_id": item.item_id,
            "item_title": None,
            "item_description": None,
            "item_image": None,
            "item_type": model_content,
        }
        if model_content == "game":
            try:
                game = Game.objects.get(id=item.item_id, is_deleted=False)
                resolved["item_title"] = game.title
                resolved["item_description"] = game.description
                resolved["item_image"] = game.main_img.url if game.main_img else None
            except Game.DoesNotExist:
                pass
        elif model_content == "product":
            try:
                store_product = StoreProduct.objects.get(
                    id=item.item_id, is_deleted=False
                )
                product = store_product.product
                resolved["item_title"] = store_product.title
                resolved["item_description"] = product.description
                resolved["item_image"] = (
                    product.main_img.url if product.main_img else None
                )
            except StoreProduct.DoesNotExist:
                pass
        elif model_content == "blog":
            from website.models import BlogPost

            try:
                blog = BlogPost.objects.get(id=item.item_id, is_deleted=False)
                resolved["item_title"] = blog.title
                resolved["item_description"] = blog.title
                resolved["item_image"] = (
                    blog.cover_image.url if blog.cover_image else None
                )
            except BlogPost.DoesNotExist:
                pass
        result.append(resolved)
    return result


def get_product_entity_info(product_id: int) -> dict:
    entities = ProductEntity.objects.filter(product_id=product_id, is_deleted=False)
    stock_count = entities.count()
    available_colors = (
        entities.exclude(color__isnull=True)
        .exclude(color__exact="")
        .values_list("color", flat=True)
        .distinct()
    )
    return {
        "stock_count": stock_count,
        "available_colors": list(available_colors),
    }


def get_game_account_stock(game_id: int) -> int:
    from psn.models import SonyAccountGame

    return SonyAccountGame.objects.filter(game_id=game_id, is_deleted=False).count()


def add_product_to_cart(
    customer: Customer, store_product_id: int, color: str | None
) -> ProductCartItem:
    store_product = get_object_or_404(
        StoreProduct, id=store_product_id, is_deleted=False
    )
    cart, _ = ProductCart.objects.get_or_create(user=customer)
    product = store_product.product
    cart_item, created = ProductCartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1, "color": color},
    )
    if not created:
        cart_item.quantity += 1
        if color is not None:
            cart_item.color = color
        cart_item.save()
    return cart_item


def remove_product_from_cart(customer: Customer, store_product_id: int) -> None:
    try:
        cart = ProductCart.objects.get(user=customer)
    except ProductCart.DoesNotExist:
        from django.http import Http404

        raise Http404("No active cart found")

    store_product = get_object_or_404(
        StoreProduct, id=store_product_id, is_deleted=False
    )
    try:
        cart_item = ProductCartItem.objects.get(
            cart=cart, product=store_product.product
        )
    except ProductCartItem.DoesNotExist:
        from django.http import Http404

        raise Http404("Product not in cart")

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()


def get_matched_sony_accounts(customer: Customer) -> QuerySet:
    cart = GameCart.objects.filter(user=customer).first()
    if not cart:
        return SonyAccount.objects.none()

    cart_game_ids = list(
        GameCartItem.objects.filter(game_cart=cart).values_list("game_id", flat=True)
    )
    if not cart_game_ids:
        return SonyAccount.objects.none()

    total_games = len(cart_game_ids)

    accounts = (
        SonyAccount.objects.filter(
            is_deleted=False,
            account_games__game_id__in=cart_game_ids,
        )
        .annotate(
            match_count=Count(
                "account_games__game",
                filter=Q(account_games__game_id__in=cart_game_ids),
            )
        )
        .filter(match_count__gte=max(total_games - 2, 1))
        .order_by("-match_count")
        .select_related("status")
        .distinct()
    )

    return accounts


def get_cart_volume_info(customer: Customer) -> dict:
    cart = GameCart.objects.filter(user=customer).first()
    if not cart:
        return {"total_volume": 0, "volume_flag": "< 500GB"}

    total_volume = (
        GameCartItem.objects.filter(game_cart=cart).aggregate(
            total=Sum("game__volume")
        )["total"]
        or 0
    )

    if total_volume < 500:
        flag = "< 500GB"
    elif total_volume < 1024:
        flag = "> 500GB"
    else:
        flag = "> 1TB"

    return {"total_volume": total_volume, "volume_flag": flag}


def add_game_to_cart(customer: Customer, game_id: int) -> GameCartItem:
    game = get_object_or_404(Game, id=game_id, is_deleted=False)
    cart, _ = GameCart.objects.get_or_create(user=customer)

    if GameCartItem.objects.filter(game_cart=cart, game=game).exists():
        from rest_framework.exceptions import ValidationError

        raise ValidationError("Game already in cart")

    return GameCartItem.objects.create(game_cart=cart, game=game)


def get_entities_for_store_product(store_product_pk: int) -> QuerySet:
    store_product = get_object_or_404(StoreProduct, id=store_product_pk)
    return ProductEntity.objects.filter(
        product_id=store_product.product_id, is_deleted=False
    )


def remove_game_from_cart(customer: Customer, game_id: int) -> None:
    try:
        cart = GameCart.objects.get(user=customer)
    except GameCart.DoesNotExist:
        from django.http import Http404

        raise Http404("No active game cart found")

    try:
        cart_item = GameCartItem.objects.get(game_cart=cart, game_id=game_id)
    except GameCartItem.DoesNotExist:
        from django.http import Http404

        raise Http404("Game not in cart")

    cart_item.delete()
