from __future__ import annotations

from psn.models import SonyAccountGame


def bulk_add_games_to_account(
    account_pk: int, game_ids: list[int]
) -> list[SonyAccountGame]:
    created = []
    for game_id in game_ids:
        _, was_created = SonyAccountGame.objects.get_or_create(
            sony_account_id=account_pk,
            game_id=game_id,
        )
        if was_created:
            created.append(
                SonyAccountGame.objects.get(sony_account_id=account_pk, game_id=game_id)
            )
    return created
