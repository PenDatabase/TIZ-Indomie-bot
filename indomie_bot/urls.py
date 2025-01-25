"""
URL configuration for indomie_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, include

admin.site.index_title = format_html("<span style='color: yellow;'>CU Indomie Guy | TIZ Administration 😁</span>")
admin.site.site_header = format_html("<span style='color: white;'>Hi Admin 👋 </span>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("bot.urls")),
]
