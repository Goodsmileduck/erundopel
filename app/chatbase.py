# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import json
from settings import CHATBASE_API
import os, logging

CHATBASE_URL = 'https://chatbase.com/api/message'
CHATBASE_URL_CLICK = 'https://chatbase.com/api/click'
PLATFORM = 'alisa'

timeout = aiohttp.ClientTimeout(total=60)
session = aiohttp.ClientSession(timeout=timeout)

def track_message(user_id, session_id, intent, message, not_handled):
    """
    Track message using http://chatbase.com
    """
    logging.debug("Track message {}".format(message))
    asyncio.ensure_future(_track_message(user_id, session_id, intent, message, not_handled))

def track_click(user_id, url):
    """
    Track click using http://chatbase.com
    """
    logging.debug("Track url {}".format(url))
    asyncio.ensure_future(_track_click(user_id, url))


async def _track_message(user_id, session_id, intent, message, not_handled):
    response = await session.post(
        CHATBASE_URL,
        data=json.dumps(
            {
                "api_key": CHATBASE_API,
                "type": "user",
                "message": message,
                "platform": PLATFORM,
                "user_id": user_id,
                "session_id": session_id,
                "version": "1.0",
                "intent": intent,
                "not_handled": not_handled
            }
        ),
    )
    if response.status != 200:
        logger.info("error submiting stats %d", response.status)
    await response.release()

async def _track_click(user_id, url):
    response = await session.post(
        CHATBASE_URL_CLICK,
        data=json.dumps(
            {
                "api_key": CHATBASE_API,
                "url": url,
                "platform": PLATFORM,
                "user_id": user_id,
                "version": "1.0"
            }
        ),
    )
    if response.status != 200:
        logger.info("error submiting stats %d", response.status)
    await response.release()