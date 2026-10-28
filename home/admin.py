from django.contrib import admin
from home.models import Contact
from .models import IPO

# Register your models here.
admin.site.register(Contact)

from django.contrib import admin
from .models import IPO

@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = ('companyName', 'status', 'openDate', 'closeDate', 'priceBand', 'issueSize')
