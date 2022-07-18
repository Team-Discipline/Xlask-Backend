import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.model.crud.channel import create_channel, read_channel, read_channels, delete_channel, update_channel
from app.model.database import get_db
from app.model.schemas import Channel

router = APIRouter(prefix='/channel', tags=['channel'])


# async def channel_auth_check(name: str, auth: Session = Depends(get_auth)):
#     check_auth = auth.query(name=Channel.ChannelMember.name, auth=get_auth.name)
#     if name != auth:
#         raise HTTPException(status_code=401, detail='channel not authorized')
#     return {
#         'auth': check_auth,
#         'success': True
#     }


@router.post('/', response_model=Channel)
async def channel_create(channel: Channel, db: Session = Depends(get_db)):
    logging.info('POST /channel/')
    db_channel = await create_channel(db, channel_name=channel.channel_name)
    logging.debug(f'channel created: {db_channel}')
    if db_channel != str:
        raise HTTPException(status_code=400, detail='Invalid channel_name type error')
    if db_channel:
        raise HTTPException(status_code=400, detail='Channel already exist')
    return {
        'success': True,
        'channel': db_channel
    }


@router.get('/', response_model=Channel)
async def channel_read_by_name(channel_name: str, db: Session = Depends(get_db)):
    logging.info('GET /channel/')
    channels = await read_channel(db, channel_name=channel_name)
    logging.debug(f'channels: {channels}')
    if channel_name is None:
        raise HTTPException(status_code=404, detail='Channel_name not found')
    return {'read_channel': True,
            'channel': channels}


@router.get('/', response_model=Channel)
async def channel_read(db: Session = Depends(get_db)):
    logging.info('GET /channel/')
    all_channel = await read_channels(db)
    logging.debug(f'all channels: {all_channel}')
    return {'all_channel': all_channel}


@router.patch('/', response_model=Channel)
async def channel_update(new_channel_name: str, old_channel_name: str, db: Session = Depends(get_db)):
    logging.info('PATCH /channel/')
    channel_updated = await update_channel(db, new_channel_name=new_channel_name, old_channel_name=old_channel_name)
    logging.debug(f'updated channel name: {channel_updated}')
    if new_channel_name != str:
        raise HTTPException(status_code=401, detail='new_channel_name type error, use string')
    # if old_channel name is not in db
    if old_channel_name:
        raise HTTPException(status_code=404, detail='old_channel_name not found')
    return {'channel updated': True,
            'channel': channel_updated}


@router.delete('/', response_model=Channel)
async def delete_channel(channel_name: str, db: Session = Depends(get_db)):
    logging.info('DELTE /channel')
    deleted_channel = await delete_channel(channel_name, db=db)
    logging.debug(f'deleted channel: {deleted_channel}')
    if channel_name not in db:
        raise HTTPException(status_code=404, detail="channel_name not found")
    return {"deleted": True,
            "deleted_channel": deleted_channel
            }
