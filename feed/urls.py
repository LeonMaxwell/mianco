from django.urls import path
from feed.views import ConfirmView, SettingView, CreateAdView, AdView, checkAdView, filterAdView, city_auto_complete, \
    index

urlpatterns = [
    path('', index, name="mianto"),
    path('confirm-ages/', ConfirmView.as_view(), name='miantoconfirm'),
    path('settings/', SettingView.as_view(), name='miantosettings'),
    path('announce/add/', CreateAdView.as_view(), name='miantocreatead'),
    path('announce/id<int:pk>/', AdView.as_view(), name='miantoviewid'),
    path('announce/id<int:pk>/active/<uuid:uuid_ad>/', checkAdView, name='checkadview'),
    path('autocomplate-city/', city_auto_complete, name='autocomplate-city'),
    path('<str:gander>-<str:interlocutor>/<int:from_age>-<int:to_age>/<int:id_purpose>'
         '/<int:code_country>-<int:code_city>/', filterAdView, name='miantofilterad')

    # TODO: Забабахать API
]