from django.urls import path, include
from django.contrib import admin
from main import views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('main.urls')),
]
