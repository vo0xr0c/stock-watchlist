"""
Websocket consumer for real-time stock updates.
"""
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from casestudy.constants import STOCK_UPDATES_GROUP

logger = logging.getLogger(__name__)


class StockConsumer(AsyncWebsocketConsumer):
    """
    A WebSocket consumer that listens for updates about a specific stock's price
    and sends them to the client.

    Methods:
        - connect: Subscribes the client to a specific stock's updates group.
        - disconnect: Unsubscribes the client from the stock's updates group.
        - receive: Handles received messages from the WebSocket (not used here).
        - stock_update: Sends received stock update messages to the client.
    """

    async def connect(self):
        """
        Connects the consumer to the WebSocket and subscribes them to the
        specific stock's updates group.
        """
        self.ticker = self.scope['url_route']['kwargs']['ticker']
        logger.info(f"Connect websocket for ticker: {self.ticker}")

        # Subscribe to the stock's specific update group.
        await self.channel_layer.group_add(
            STOCK_UPDATES_GROUP,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnects the consumer from the WebSocket and unsubscribes them from the
        specific stock's updates group.

        Args:
            close_code (int): A code denoting the reason for disconnection.
        """
        # Unsubscribe from the stock's specific update group.
        logger.info(f"Disconnect websocket for ticker: {self.ticker}")
        await self.channel_layer.group_discard(
            "stock_updates_group",
            self.channel_name
        )

    async def receive(self, text_data):
        # Messages are ignored in this case.
        pass

    async def stock_update(self, event):
        """
        Handles messages of type 'stock_update' by sending them to the clients.

        Args:
            event (dict): An event containing message "ticker:price"
        """
        if not event['message'].lower().startswith(self.ticker.lower() + ':'):
            return

        price = event['message'][len(self.ticker) + 1:]
        logger.debug(f"StockConsumer: event_message = {event['message']}, stock_update {self.ticker} = {price}")

        await self.send(text_data=json.dumps({
            'price': price
        }))
