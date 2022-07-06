import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..model.crud import user, authorization
from ..model.crud.authorization import read_authorization
from ..model.crud.user import read_users, read_user, update_user, delete_user
from ..model.database import get_db
from ..model.schemas import UserCreate, UserInformation

router = APIRouter(prefix='/user', tags=['user'])


@router.post('/')
async def create_user(user_info: UserCreate,
                      db: Session = Depends(get_db)):
    # Check authorization first!
    if not await authorization.read_authorization(name=user_info.authorization, db=db):
        raise HTTPException(status_code=404, detail='No such authorization.')

    try:
        # TODO: Handle error.
        # If authorization exists, create user.
        result = await user.create_user(github_id=user_info.github_id,
                                        email=user_info.email,
                                        name=user_info.name,
                                        authorization_name=user_info.authorization,
                                        refresh_token=None,  # TODO: Include refresh token.
                                        db=db)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(detail=e.args[0].split('\"')[1], status_code=400)

    # TODO: Issue access token and refresh token.
    return {
        'success': True,
        'message': 'Successfully created user.',
        'user': await read_user(db=db, email=user_info.email)
    }


# TODO: Should adjust auth middleware.
@router.get('/')
async def read_user_info(user_id: str | None = None,
                         email: str | None = None,
                         db: Session = Depends(get_db)):
    result = await read_user(user_id=user_id, email=email, db=db)

    return {
        'success': True,
        'user': result
    } if result is not None else JSONResponse(content={
        'success': False,
        'message': 'No such user.'
    }, status_code=404)


# TODO: Should adjust auth middleware.
@router.get('/all')
async def get_all_users(db: Session = Depends(get_db)):
    users = await read_users(db)
    return {
        'success': True,
        'users': users
    } if len(users) != 0 else JSONResponse(content={
        'success': False,
        'message': 'No users.'
    }, status_code=404)


# TODO: Should adjust auth middleware.
@router.patch('/')
async def update_user_info(user_info: UserInformation,
                           user_id: str | None = Query(default=None, description='One of way to select user.'),
                           db: Session = Depends(get_db)):
    """
    When you want to update user's information.
    Put user information you want to update on **request body**.
    Use `user_id`.

    :param user_info:
    :param user_id:
    :param db:
    :return:
    """

    # Check authorization first.
    if not await read_authorization(user_info.authorization, db):
        raise HTTPException(status_code=404, detail='No such authorization.')

    # If authorization exists, Fix user information.
    rows = await update_user(db=db, user_id=user_id,
                             email=user_info.email,
                             name=user_info.name,
                             authorization_name=user_info.authorization)

    if not rows:
        raise HTTPException(detail='Not updated.')

    return {
        'success': True,
        'message': 'Successfully updated.',
        'user': await read_user(db=db, user_id=user_id)
    }


# TODO: Should adjust auth middleware.
@router.delete('/')
async def remove_user(user_id: str, db: Session = Depends(get_db)):
    rows = await delete_user(user_id=user_id, db=db)

    if not rows:
        raise HTTPException(detail='Not deleted.')

    return {
        'success': True,
        'message': 'Successfully deleted.',
        'count': rows
    }
