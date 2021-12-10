from django.http import HttpResponse
import requests
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City, Country


def parse_areas():
    # Парсинг городов по JSON. По окончанию паркинга создаются объекты в базе данных.
    country_all = Country.objects.all()
    city_all = City.objects.all()
    r_json = requests.get('https://api.hh.ru/areas').json()
    for country in r_json:
        if country['name'] == "Россия" or country['name'] == "Беларусь" or country['name'] == "Украина":
            if not country_all.filter(name=country['name']).exists():
                country_object = Country()
                country_object.name = country['name']
                country_object.code = country['id']
                country_object.save()
            for areas_country in country['areas']:
                if areas_country['areas']:
                    for areas_resp in areas_country['areas']:
                        if not city_all.filter(name=areas_resp['name']).exists():
                            city_object = City()
                            country_pk = country_all.get(name=country['name'])
                            city_object.country = country_pk
                            if areas_country['name'] in areas_resp['name']:
                                city_object.name = f"{country['name']} г.{areas_resp['name']}"
                            else:
                                city_object.name = f"{country['name']} г.{areas_resp['name']}({areas_country['name']})"
                            city_object.code = areas_resp['id']
                            city_object.save()
                else:
                    if not city_all.filter(name=areas_country['name']).exists():
                        city_object = City()
                        country_pk = country_all.get(name=country['name'])
                        city_object.country = country_pk
                        city_object.name = f"{country['name']} г.{areas_country['name']}"
                        city_object.code = areas_country['id']
                        city_object.save()
    return "Ок!"


def parsing_city(request):
    # функция которая запускает парсинг городов
    result = parse_areas()
    return HttpResponse(result)


class CityView(APIView):
    # Класс View при котором можно посмотреть сформированный JSON из базы данных городов

    @staticmethod
    def get(request, format=None):
        city_all = City.objects.all().values()
        content = city_all
        return Response(content)
