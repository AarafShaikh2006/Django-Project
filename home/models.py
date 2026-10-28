from django.db import models
from django.contrib.auth.models import User  # For linking portfolio to users

# Existing Contact model
class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.CharField(max_length=122)
    phone = models.CharField(max_length=12)
    desc = models.TextField(blank=True, null=True)  # Now optional
    date = models.DateField(auto_now_add=True)       # Automatically set current date

    def __str__(self):
        return self.name

# New Portfolio model
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=30)  # e.g., AAPL, TCS
    quantity = models.PositiveIntegerField()
    buy_price = models.FloatField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.stock_symbol}"

    @property
    def total_investment(self):
        return self.quantity * self.buy_price
from django.db import models

class IPO(models.Model):
    STATUS_CHOICES = [
        ('open', 'Ongoing'),
        ('upcoming', 'Upcoming'),
        ('listed', 'Listed'),
    ]

    companyName = models.CharField(max_length=100)
    openDate = models.CharField(max_length=50, blank=True, null=True)
    closeDate = models.CharField(max_length=50, blank=True, null=True)
    priceBand = models.CharField(max_length=50, blank=True, null=True)
    issueSize = models.CharField(max_length=50, blank=True, null=True)
    lotSize = models.CharField(max_length=50, blank=True, null=True)
    rhpLink = models.URLField(blank=True, null=True)
    listingDate = models.CharField(max_length=50, blank=True, null=True)
    issuePrice = models.CharField(max_length=50, blank=True, null=True)
    listingPrice = models.CharField(max_length=50, blank=True, null=True)
    listingGain = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.companyName

    def __str__(self):
        return f"{self.companyName} ({self.get_status_display()})"        
