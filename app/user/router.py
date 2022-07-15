from datetime import timedelta

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..errors.jwt_error import RefreshTokenExpired, AccessTokenExpired
from ..model.crud import authorization
from ..model.crud.authorization import read_authorization
from ..model.crud.user import read_users, read_user, update_user, delete_user, create_user
from ..model.database import get_db
from ..model.schemas import UserCreate, UserUpdate
from ..utils.jwt import issue_token, check_auth_using_token

router = APIRouter(prefix='/user', tags=['user'])


@router.post('/')
async def user_create(user_info: UserCreate,
                      db: Session = Depends(get_db)):
    # Check authorization first!
    if not await authorization.read_authorization(name=user_info.authorization, db=db):
        raise HTTPException(status_code=404, detail='No such authorization.')

    # If authorization exists, create user
    try:
        await create_user(github_id=str(user_info.github_id),
                          email=user_info.email,
                          name=user_info.name,
                          authorization_name=user_info.authorization,
                          refresh_token=None,
                          thumbnail_url=user_info.thumbnail_url,
                          db=db)

        user = await read_user(db=db, email=user_info.email)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(detail=e.args[0].split('\"')[1], status_code=400)

    # And then, Issue access_token and refresh_token.
    user = {
        'user_id': user.user_id,
        'email': user.email,
        'name': user.name,
        'authorization': user.authorization,
        'created_at': str(user.created_at),
        'thumbnail_url': user.thumbnail_url
    }  # This code is inevitable to convert to `dict` object. Fucking `datetime` is not json parsable.
    access_token = issue_token(user_info=user, delta=timedelta(hours=1))
    refresh_token = issue_token(user_info=user, delta=timedelta(days=14))

    # And then, Update user info with `refresh_token`.
    await update_user(db=db,
                      user_id=str(user['user_id']),
                      email=user['email'],
                      name=user['name'],
                      authorization_name=user['authorization'],
                      thumbnail_url=user['thumbnail_url'],
                      refresh_token=refresh_token)

    return {
        'success': True,
        'message': 'Successfully created user.',
        'user': await read_user(db=db, email=user_info.email),
        'access_token': access_token,
        'refresh_token': refresh_token
    }


@router.get('/')
async def user_read(user_id: str,
                    token_payload: dict = Depends(check_auth_using_token),
                    db: Session = Depends(get_db)):
    """
    When you want to get user info from database.
    You must input `user_id` or `email`. One of them!
    The tokens are just needed to be valid.
    Don't check who's token.
    """
    if isinstance(token_payload, RefreshTokenExpired) or isinstance(token_payload, AccessTokenExpired):
        return JSONResponse(content={
            'success': False,
            'detail': token_payload.detail
        }, status_code=token_payload.status_code)

    # Check if client is `admin` or client itself.
    auth = token_payload['authorization']
    client_id = token_payload['user_id']
    if auth != 'admin' or client_id != user_id:
        raise HTTPException(detail='Not enough authorization to do this.', status_code=status.HTTP_401_UNAUTHORIZED)

    result = await read_user(user_id=user_id, db=db)

    return {
        'success': True,
        'user': result
    } if result is not None else JSONResponse(content={
        'success': False,
        'message': 'No such user.'
    }, status_code=404)


@router.get('/all')
async def get_all_users(token_payload: dict = Depends(check_auth_using_token),
                        db: Session = Depends(get_db)):
    """
    Only `admin` authorization can get this endpoint.
    """
    if isinstance(token_payload, RefreshTokenExpired) or isinstance(token_payload, AccessTokenExpired):
        return JSONResponse(content={
            'success': False,
            'detail': token_payload.detail
        }, status_code=token_payload.status_code)

    auth = token_payload['authorization']
    if auth != 'admin':
        raise HTTPException(detail='Not enough authorization to do this.', status_code=status.HTTP_401_UNAUTHORIZED)

    users = await read_users(db)
    return {
        'success': True,
        'users': users
    } if len(users) != 0 else JSONResponse(content={
        'success': False,
        'message': 'No users.'
    }, status_code=404)


@router.patch('/')
async def update_user_info(user_info: UserUpdate,
                           token_payload: dict = Depends(check_auth_using_token),
                           user_id: str | None = Query(default=None, description='One of way to select user.'),
                           db: Session = Depends(get_db)):
    """
    When you want to update user's information.
    Put user information you want to update on **request body**.
    Use `user_id`.
    """
    if isinstance(token_payload, RefreshTokenExpired) or isinstance(token_payload, AccessTokenExpired):
        return JSONResponse(content={
            'success': False,
            'detail': token_payload.detail
        }, status_code=token_payload.status_code)

    # To update user's information, Be admin or client itself.
    auth = token_payload['authorization']
    client_user_id = token_payload['user_id']
    if auth != 'admin' or user_id != client_user_id:
        raise HTTPException(detail='No authorization to do this.', status_code=status.HTTP_401_UNAUTHORIZED)

    # Check authorization first.
    if not await read_authorization(user_info.authorization, db):
        raise HTTPException(status_code=404, detail='No such authorization.')

    # If authorization exists, Fix user information.
    rows = await update_user(db=db, user_id=user_id,
                             email=user_info.email,
                             name=user_info.name,
                             thumbnail_url=user_info.thumbnail_url,
                             authorization_name=user_info.authorization,
                             refresh_token=user_info.refresh_token)

    if not rows:
        raise HTTPException(detail='Not updated.', status_code=403)

    return {
        'success': True,
        'message': 'Successfully updated.',
        'user': await read_user(db=db, user_id=user_id)
    }


@router.delete('/')
async def remove_user(user_id: str,
                      token_payload: dict = Depends(check_auth_using_token),
                      db: Session = Depends(get_db)):
    if isinstance(token_payload, RefreshTokenExpired) or isinstance(token_payload, AccessTokenExpired):
        return JSONResponse(content={
            'success': False,
            'detail': token_payload.detail
        }, status_code=token_payload.status_code)

    auth = token_payload['authorization']
    client_user_id = token_payload['user_id']
    if auth != 'admin' or user_id != client_user_id:
        raise HTTPException(detail='No authorization to do this.', status_code=status.HTTP_401_UNAUTHORIZED)

    rows = await delete_user(user_id=user_id, db=db)

    if not rows:
        raise HTTPException(detail='Not deleted.', status_code=status.HTTP_404_NOT_FOUND)

    return {
        'success': True,
        'message': 'Successfully deleted.',
        'count': rows
    }
