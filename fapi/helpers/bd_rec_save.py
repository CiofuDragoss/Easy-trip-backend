from fapi.helpers.jwt_helpers import verify_token_access
from beanie import Link
from fastapi import HTTPException, status
from fapi.models import User, Recommendation, VisitedPlaces, BannedPlace
import asyncio
import random


async def save_recs(token, rec_data, type, loc_bd):
    token = token.split(" ")[1].strip()

    try:
        payload = verify_token_access(token)
    except Exception as e:
        raise Exception("Token invalid")

    email: str = payload.get("sub")

    user = await User.find_one(User.email == email)
    if not user:
        raise Exception("Nu Avem user")

    rec = Recommendation(
        type=type,
        user=user,
        data=rec_data,
        location=loc_bd,
    )

    await rec.insert()


async def get_visited_set(token):
    print("am obtinut visited set")
    token = token.split(" ")[1].strip()

    try:
        payload = verify_token_access(token)
    except Exception as e:
        raise Exception("Token invalid")

    email: str = payload.get("sub")

    user = await User.find_one(User.email == email)
    if not user:
        raise Exception("Nu Avem user")

    visited = await VisitedPlaces.find_one(VisitedPlaces.user.id == user.id)
    if not visited:
        visited = VisitedPlaces(user=user, place_ids=[])
        await visited.insert()

    if visited.update_index > 5:
        visited.place_ids = []
        visited.update_index = 0
        await visited.save()
    return visited, set(visited.place_ids)


async def add_to_visited(global_visited_set, local_set):
    existing = set(global_visited_set.place_ids)
    new_ids = local_set - existing
    if new_ids:
        global_visited_set.place_ids.extend(new_ids)

        global_visited_set.update_index += 1

        await global_visited_set.save()


async def filter_banned_places(possible_banned, chance=1):

    async def check_and_maybe_keep(pid):

        doc = await BannedPlace.find_one(BannedPlace.place_id == pid)
        if not doc:
            return None

        if random.random() < (doc.ban_count / chance):
            return pid
        return None

    results = await asyncio.gather(
        *(check_and_maybe_keep(pid) for pid in possible_banned), return_exceptions=False
    )

    final_set = {pid for pid in results if pid is not None}
    return final_set
