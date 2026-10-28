# D:\Django\hello\home\urls.py

from django.urls import path
from home import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Core pages
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("news/", views.news, name="news"),
    path("ipo/", views.ipo_view, name="ipo"),
    path("predict/", views.predict_stock, name="predict_stock"),


    # Portfolio Views
    path("portfolio/", views.portfolio, name="portfolio"),
    path("portfolio/update_prices/", views.update_prices, name="update_prices"),
    path("delete_stock/<int:pk>/", views.delete_stock, name="delete_stock"),
    
    # Symbol search autocomplete (REMOVED to fix AttributeError)
    path("symbol_search/", views.symbol_search, name="symbol_search"), 


    # Authentication
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]