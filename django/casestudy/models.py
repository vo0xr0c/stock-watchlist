"""
Django models for the casestudy service.
"""
from django.contrib.auth.models import User
from django.db import models


class Security(models.Model):
    """Securities universe"""

    # The security’s name (e.g. Netflix Inc)
    name = models.TextField(max_length=50, null=False, blank=False)

    # The security’s ticker (e.g. NFLX)
    ticker = models.TextField(max_length=10, unique=True, null=False, blank=False)

    # This field is used to store the last price of a security
    last_price = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=11,
    )

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ticker})"


# Watchlist Model
class Watchlist(models.Model):
    user = models.ForeignKey(User, related_name='watchlists', on_delete=models.CASCADE)
    stock = models.ForeignKey(Security, related_name='watchlists', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stock')

    def __str__(self):
        return f"{self.user.username} - {self.stock.ticker}"
