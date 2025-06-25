from django.contrib import admin
from django.urls import path
from routing.views import RouteFuelView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/route-fuel/', RouteFuelView.as_view()),
]
