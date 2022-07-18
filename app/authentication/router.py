import json
import logging
import os

from fastapi import APIRouter, Request, Query, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..model.crud.user import update_user, read_user
from ..model.database import get_db
from ..utils.github_auth import exchange_code_for_access_token, get_user_data_from_github

router = APIRouter(prefix='/authentication', tags=['authentication'])


@router.get('/github_login')
async def login_github():
    """
    Get redirect response to GitHub OAuth2.
    Test code for testing backend redirect codes.
    Frontend team may not use this endpoint.

    :return:
    """
    logging.info('GET /authentication/github_login')

    client_id = os.getenv('GITHUB_CLIENT_ID')
    scope = 'read:user'
    url = f'https://github.com/login/oauth/authorize?client_id={client_id}&scope={scope}'
    logging.debug(f'url: {url}')
    return RedirectResponse(url)


@router.get('/redirect/github')
async def redirect_github(request: Request, code: str):
    """
    This function deal with after redirect from client.

    :return:
    """
    logging.info('GET /authentication/redirect/github')
    logging.debug(f'params: {request.query_params}')
    logging.debug(f'code: {code}')
    res = exchange_code_for_access_token(code)

    logging.debug(f'res: {res.content}')

    content = str(res.content)

    first_word = content.split('&')[0].split('=')[0]

    if first_word == 'b\'error':
        return {
            'success': False,
            'message': 'Failed to get access token.',
            'detail': content.split('&')[1].split('=')[1]
        }

    access_token = content.split('&')[0].split('=')[1]

    return {
        'success': True,
        'message': 'Successfully get access token from github.',
        'access_token': access_token
    }


@router.get('/user_info/github')
async def get_user_info(github_access_token: str = Query(
    alias='Access Token From Github.',
    title='github access token',
    description='You should input only GITHUB ACCESS TOKEN!!!',
    max_length=50,
    min_length=30)
):
    """
    When you get information from github directly using github access token.

    :param github_access_token:
    :return:
    """
    logging.info('GET /authentication/user_info/github')
    res = get_user_data_from_github(github_access_token)
    logging.debug(f'responses from github: {res}')
    return {
        'success': True,
        'message': 'Successfully get user information from github.',
        'github_info': json.loads(res.content)
    }


@router.get('/revoke_token/{user_id}')
async def revoke_token(user_id: str, db: Session = Depends(get_db)):
    logging.info('GET /authentication/revoke_token/{user_id}')
    user_info = await read_user(db, user_id=user_id)

    # Check `user_id` is valid first.
    if user_info is None:
        logging.info('No such user')
        raise HTTPException(detail='No such user', status_code=404)

    try:
        rows = await update_user(db=db, user_id=user_id,
                                 email=user_info.email,
                                 name=user_info.name,
                                 authorization_name=user_info.authorization,
                                 thumbnail_url=user_info.thumbnail_url)
        if not rows:
            logging.warning('Not updated!')
            raise HTTPException(detail='Not updated!', status_code=404)

    except Exception as e:
        logging.warning(f'Other Exception: {e.__str__()}')
        raise HTTPException(detail=e.__str__(), status_code=400)

    return {
        'success': True,
        'message': 'Successfully revoked refresh token.'
    }
