"""
Tasks for fetching and updating stock ticker data using Celery.
"""
import json
import os

import requests
from asgiref.sync import async_to_sync
from celery import Task, shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from .constants import (ALBERT_TICKERS, ALBERT_TICKERS_PRICE, REDIS_SECURITIES_KEY,
                        REDIS_SECURITY_DESCRIPTION_PREFIX, STOCK_UPDATES_GROUP)

from .models import Security
from .redis_utils import redis_conn as redis
from .serializers import SecuritySerializer

logger = get_task_logger(__name__)
channel_layer = get_channel_layer()

API_KEY_HEADER = 'Albert-Case-Study-API-Key'
API_KEY = os.environ.get('ALBERT_API_KEY')


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 180
    max_retries = 3


@shared_task(
    base=BaseTaskWithRetry,
    name='fetch_available_tickers',
    bind=True,
    ignore_result=True,
)
def fetch_available_tickers(self):
    try:
        response = requests.get(ALBERT_TICKERS, headers={API_KEY_HEADER: API_KEY})
        response.raise_for_status()
        available_tickers = response.json()
        securities_data = []
        for ticker, name in available_tickers.items():
            Security.objects.update_or_create(ticker=ticker, defaults={'name': name})
            securities_data.append({'ticker': ticker, 'name': name})
        redis.set(REDIS_SECURITIES_KEY, json.dumps(securities_data))
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch available tickers due to {str(e)}.")
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


@shared_task(
    base=BaseTaskWithRetry,
    name='update_stock_prices',
    bind=True,
    ignore_result=True,
)
def update_stock_prices(self):
    try:
        securities = redis.get(REDIS_SECURITIES_KEY)
        if securities is None:
            logger.warning("No securities in Redis. Triggering fetch_available_tickers task.")
            fetch_available_tickers.apply_async()
            return
        tickers = [security['ticker'] for security in json.loads(securities)]
        response = requests.get(ALBERT_TICKERS_PRICE + ','.join(tickers), headers={API_KEY_HEADER: API_KEY})
        response.raise_for_status()
        prices = response.json()
        securities_to_update = []
        for security in Security.objects.filter(ticker__in=prices.keys()):
            new_price = prices[security.ticker]
            if security.last_price != new_price:  # TODO: Broadcasting part could be in the separate job
                security.last_price = new_price
                # Save new Stock model to Cache
                cache_key = f'{REDIS_SECURITY_DESCRIPTION_PREFIX}/{security.ticker}'
                data = json.dumps(SecuritySerializer(security).data)
                redis.set(cache_key, data)
                # Publish to websockets
                async_to_sync(channel_layer.group_send)(
                    STOCK_UPDATES_GROUP,
                    {
                        'type': 'stock_update',
                        'message': f'{security.ticker}:{new_price}'
                    }
                )
                securities_to_update.append(security)
        Security.objects.bulk_update(securities_to_update, ['last_price'])
    except requests.RequestException as e:
        if response.status_code == 400:
            logger.warning("Received 400 status code. Triggering fetch_available_tickers task.")
            fetch_available_tickers.apply_async()
        logger.warning(f"Failed to update stock prices due to {str(e)}.")
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"An error occurred while updating stock prices: {str(e)}")
