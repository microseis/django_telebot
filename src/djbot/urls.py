
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path(route='admin/', view=admin.site.urls),
]
