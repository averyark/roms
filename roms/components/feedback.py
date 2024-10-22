from typing import Annotated, Literal, Optional
from datetime import date, datetime

from fastapi import HTTPException, status, Depends

from ..database import session
from ..database.schemas import Review, ReviewCreate
from ..database.models import ReviewModel
from ..api import app
from ..account import validate_role
from ..user import User

@app.get('/review/get', tags=['review'])
async def get_review(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Customer'])),
    ],
    review_id: int = None,
    user_id: str = None,
    item_id: int = None,
    value: int = None,
    review_datetime: datetime = None,
):
    query = session.query(ReviewModel)

    if review_id:
        query = query.filter(
            ReviewModel.review_id == review_id
        )
    if user_id:
        query = query.filter(
            ReviewModel.user_id == user_id
        )
    if item_id:
        query = query.filter(
            ReviewModel.item_id == item_id
        )
    if value:
        query = query.filter(
            ReviewModel.value == value
        )
    if review_datetime:
        query = query.filter(
            ReviewModel.review_datetime == review_datetime
        )

    reviews = query.all()

    if user.get_role() in ['Manager']:
        return reviews

    for review in reviews:
        if review.user_id == user_id:
            continue
        try:
            reviews.remove(review)
        except: pass

    return reviews

@app.post('/review/add', tags=['review'])
async def add_review(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Customer'])),
    ],
    item_id: int,
    remark: str,
    value: int,
):
    in_db_review = ReviewModel(
        user_id=user.user_id,
        item_id=item_id,
        remark=remark,
        value=value,
        review_datetime=datetime.now()
    )

    session.add(in_db_review)
    session.commit()
    session.refresh(in_db_review)

    return {
        'msg': 'Review added successfully', 'review': in_db_review
    }

@app.patch('/review/edit', tags=['review'])
async def edit_review(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Customer'])),
    ],
    review_id: int,
    remark: str = None,
    value: int = None,
):
    in_db_review = session.query(ReviewModel).filter(ReviewModel.review_id == review_id).one_or_none()

    if not in_db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found')

    if in_db_review.user_id != user.user_id:
        if not user.get_role() in ['Manager']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot edit this review")

    if remark:
        in_db_review.remark = remark
    if value:
        in_db_review.value = value

    session.commit()
    session.refresh(in_db_review)

    return {
        'msg': 'Review edited successfully', 'review': in_db_review
    }

@app.delete('/review/delete', tags=['review'])
async def delete_remark(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Customer']))
    ],
    review_id: int
):
    in_db_review = session.query(ReviewModel).filter(ReviewModel.review_id == review_id).one()

    if not in_db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if in_db_review.user_id != user.user_id:
        if not user.get_role() in ['Manager']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete this review")

    session.delete(in_db_review)
    session.commit()

    return {"msg": f"Review with ID {in_db_review} was deleted successfully"}
