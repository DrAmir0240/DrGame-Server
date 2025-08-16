# sony_accounts/services.py
from decimal import Decimal
from typing import Iterable

from django.db.models import Prefetch
from django.utils.html import escape

from storage.models import SonyAccount, SonyAccountGame, Game

def get_game_price(game: Game) -> Decimal:
    """
    انعطاف‌پذیر: اگر فیلد قیمت متفاوت بود اینجا تغییر بده.
    اولویت به ترتیب: price, selling_price, final_price, base_price
    """
    for attr in ("price", "selling_price", "final_price", "base_price"):
        if hasattr(game, attr) and getattr(game, attr) is not None:
            return Decimal(getattr(game, attr))
    return Decimal("0")


def humanize_price(amount: Decimal) -> str:
    """
    تبدیل عدد به نمایش انسانی. (ساده)
    اگر واحد ارزی خاص می‌خوای اینجا اضافه کن.
    """
    # مثال: 1250000 -> 1,250,000
    s = f"{int(amount):,}"
    return f"{s} تومان"


def fetch_account_with_games(account_id: int) -> SonyAccount:
    """
    اکانت را با prefetch بازی‌ها (فقط لینک‌های حذف‌نشده) می‌کشد.
    """
    games_qs = Game.objects.all().only("id", "title")  # اگر خواستی فیلدهای دیگری اضافه کن
    return (
        SonyAccount.objects
        .select_related("status", "bank_account", "employee")
        .prefetch_related(
            Prefetch(
                "account_games",
                queryset=SonyAccountGame.objects.filter(is_deleted=False).select_related("game"),
                to_attr="account_games_active",
            ),
            Prefetch(
                "games",
                queryset=games_qs,
            ),
        )
        .get(id=account_id, is_deleted=False)
    )


def build_account_message(account: SonyAccount) -> str:
    """
    پیام HTML-safe برای تلگرام می‌سازد.
    """
    # استفاده از escape برای امن‌سازی HTML
    username = escape(account.username or "-")
    region_display = escape(account.get_region_display() or "-")  # چون choices دارد
    plus = "✅ دارد" if account.plus else "❌ ندارد"
    owned = "✅ بله" if account.is_owned else "❌ خیر"
    bank_acc_status = "✅ تایید" if account.bank_account_status else "❌ نامشخص/عدم تایید"

    status_label = escape(getattr(account.status, "title", None) or getattr(account.status, "name", None) or "-")
    bank_label = escape(getattr(account.bank_account, "title", None) or getattr(account.bank_account, "name", None) or "-")
    employee_name = escape(getattr(account.employee, "full_name", None) or getattr(account.employee, "name", None) or "-")

    # جمع کردن بازی‌ها از لینک‌های فعال
    games: Iterable[Game] = (ag.game for ag in getattr(account, "account_games_active", []))

    lines = []
    lines.append(f"<b>اکانت سونی:</b> {username}")
    lines.append(f"<b>ریجن:</b> {region_display}")
    lines.append(f"<b>وضعیت اکانت:</b> {status_label}")
    lines.append(f"<b>پلِی‌استیشن پلاس:</b> {plus}")
    lines.append(f"<b>مالکیت:</b> {owned}")
    lines.append(f"<b>وضعیت حساب بانکی:</b> {bank_acc_status}")
    lines.append(f"<b>بانک متصل:</b> {bank_label}")
    lines.append(f"<b>کارمند مسئول:</b> {employee_name}")
    lines.append("")  # خط خالی

    total = Decimal("0")
    game_lines = []
    for i, game in enumerate(games, start=1):
        title = escape(game.title or f"بازی #{game.id}")
        price = get_game_price(game)
        total += price
        game_lines.append(f"{i}. {title} — {humanize_price(price)}")

    if game_lines:
        lines.append("<b>بازی‌ها:</b>")
        lines.extend(game_lines)
        lines.append("")  # خط خالی
        lines.append(f"<b>جمع کل:</b> {humanize_price(total)}")
    else:
        lines.append("<i>هیچ بازی فعالی برای این اکانت ثبت نشده است.</i>")

    # در صورت نیاز: هش‌تگ‌ها/توضیحات اضافه
    # lines.append("\n#PlayStation #PSN")

    return "\n".join(lines)
