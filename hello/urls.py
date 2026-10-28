"""
URL configuration for hello project.
"""
from django.contrib import admin
from django.urls import path,include

admin.site.site_header = "My Rehan Admin"
admin.site.site_title = "My Rehan Admin Title"
admin.site.index_title = "Welcome to My Rehan Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('home.urls'))
]