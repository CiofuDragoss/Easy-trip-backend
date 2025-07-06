from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Response, status
from beanie import PydanticObjectId
from fapi import models, schemas
from fastapi.security import OAuth2PasswordBearer
from fapi.helpers.jwt_helpers import verify_token_access
from beanie.operators import Inc, Set
from fapi.schemas import RecommendationMeta, RecommendationDetail

router = APIRouter(dependencies=[Depends(verify_token_access)])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token_access(token)
    email: str = payload.get("sub")
    user = await models.User.find_one(models.User.email == email)
    if not user:
        raise HTTPException(401, "Invalid authentication credentials")
    return user


@router.delete("/rec_operations", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_recs(current_user: models.User = Depends(get_current_user)):
    await models.Recommendation.find(
        models.Recommendation.user.id == current_user.id
    ).delete()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/add_remove_banned",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "No Content"}},
)
async def add_remove_banned(payload: schemas.TogglePayload):
    p_id = payload.place_id
    add = payload.add

    try:
        if add:

            await models.BannedPlace.find_one(
                models.BannedPlace.place_id == p_id
            ).update(Inc({models.BannedPlace.ban_count: 1}), upsert=True)

        else:
            doc = await models.BannedPlace.find_one(models.BannedPlace.place_id == p_id)
            if doc and doc.ban_count > 0:
                new_count = doc.ban_count - 1
                await doc.update(Set({models.BannedPlace.ban_count: new_count}))
    except Exception as e:
        raise

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/rec_operations", response_model=List[RecommendationMeta])
async def get_all_recs(current_user: models.User = Depends(get_current_user)):
    recs = await (
        models.Recommendation.find(models.Recommendation.user.id == current_user.id)
        .sort([("created_at", -1)])
        .project(RecommendationMeta)
        .to_list()
    )

    if not recs:
        return []
    return recs


@router.get(
    "/single_rec/{rec_id}",
    response_model=RecommendationDetail,
    summary="Fetch a single recommendation by its ID",
)
async def get_recommendation(
    rec_id: PydanticObjectId = Path(..., description="The MongoDB id of the rec"),
    current_user: models.User = Depends(get_current_user),
):

    rec = await models.Recommendation.find_one(
        {"_id": rec_id, "user.$id": current_user.id}
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.delete(
    "/single_rec/{rec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a single rec",
)
async def delete_recommendation(
    rec_id: PydanticObjectId = Path(..., description="The MongoDB id of the rec"),
    current_user: models.User = Depends(get_current_user),
):

    rec = await models.Recommendation.find_one(
        {"_id": rec_id, "user.$id": current_user.id}
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    await rec.delete()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/delete_account", status_code=status.HTTP_204_NO_CONTENT, summary="")
async def delete_account(current_user: models.User = Depends(get_current_user)):
    user_id = current_user.id

    await models.Recommendation.find(models.Recommendation.user.id == user_id).delete()

    await models.JwtTokens.find(models.JwtTokens.user.id == user_id).delete()

    await models.VisitedPlaces.find(models.VisitedPlaces.user.id == user_id).delete()

    await current_user.delete()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
