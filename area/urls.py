from django.urls import path
from .views import parsing_city, CityView

urlpatterns = [
    path('', CityView.as_view(), name='areacity'),
    path('parsing/city/', parsing_city),
]
