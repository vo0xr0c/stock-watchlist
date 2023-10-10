"""
API views to handle user authentication, securities listing, and watchlist operations.
"""
import json
import logging

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .constants import REDIS_SECURITIES_KEY, REDIS_SECURITY_DESCRIPTION_PREFIX
from .models import Security, User, Watchlist
from .serializers import SecuritySerializer
from .redis_utils import redis_conn as redis


logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    Login view for the API.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        """
        Login view for the API.
        """
        username = request.data['username']
        user = User.objects.get(username=username)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        logging.info(f"User {user.username} logged in.")
        return Response(user_data)


class SecurityViewSet(viewsets.ViewSet):
    """
    View to list all securities in the system.

    * If 'query' parameter is present, it will return securities whose names or tickers start with the query.
    * First checks Redis cache, if not present, queries the database and updates the cache.
    """

    def list(self, request):
        query = self.request.query_params.get('query', '').lower()
        securities = redis.get(REDIS_SECURITIES_KEY)
        if securities:
            securities = json.loads(securities)
            if query:
                securities = [
                    sec for sec in securities if
                    sec['ticker'].lower().startswith(query) or sec['name'].lower().startswith(query)
                ]
            return Response(securities, status=status.HTTP_200_OK)
        # If not in cache, fetch from database and set to Redis
        securities = Security.objects.all()
        dump_securities = list(securities.values('ticker', 'name'))
        redis.set(REDIS_SECURITIES_KEY, json.dumps(dump_securities))
        if query:
            securities = securities.filter(
                name__istartswith=query) | securities.filter(ticker__istartswith=query)
        securities = list(securities.values('ticker', 'name'))
        return Response(securities, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        GET /stocks/{id}/
        Retrieve a stock by ID.
        """
        stock = redis.get(f'{REDIS_SECURITY_DESCRIPTION_PREFIX}/{pk}')
        if stock:
            stock = json.loads(stock)
            return Response(stock)
        stock = Security.objects.get(ticker=pk)
        serializer = SecuritySerializer(stock)
        cache_key = f'{REDIS_SECURITY_DESCRIPTION_PREFIX}/{stock.ticker}'
        redis.set(cache_key, json.dumps(serializer.data))
        return Response(serializer.data)


class WatchlistViewSet(viewsets.ViewSet):
    """
    A ViewSet for a user's watchlist operations.
    """

    def list(self, request):
        """
        GET /watchlist/
        List the user's watchlist.
        """
        # FIXME Login is made incorrect way here, could not be used in production
        user = User.objects.get(username=request.headers['Username'])
        securities = Security.objects.filter(watchlists__user=user)
        serializer = SecuritySerializer(securities, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        POST /watchlist/
        Add a stock to the user's watchlist.
        """
        user = User.objects.get(username=request.headers['Username'])
        stock_id = request.data.get('ticker')
        try:
            stock = Security.objects.get(ticker=stock_id)
            Watchlist.objects.create(user=user, stock=stock)
            return Response({'message': 'Stock added to watchlist'}, status=status.HTTP_201_CREATED)
        except Security.DoesNotExist:
            return Response({'error': 'Stock does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        DELETE /watchlist/{ticker}/
        Remove a stock from the user's watchlist.
        """
        user = User.objects.get(username=request.headers['Username'])
        stock = Security.objects.get(ticker=pk)
        watchlist_item = get_object_or_404(Watchlist.objects.filter(stock=stock, user=user))
        watchlist_item.delete()
        return Response({'message': 'Stock removed from watchlist'}, status=status.HTTP_204_NO_CONTENT)
