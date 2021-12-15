from random import choices

from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from profilemianto.models import ProfileFeed, ProfileMianto, ProfileMessages
from .forms import ContactForm, SettingsForm, CreateAdForm, AnswerForm
from area.models import City, Country
from .models import Announcement
import locale
from django.db.models import Q
from datetime import date

from .serializers import AnnouncementSerializer, AnswerSerializer

# При данной настройке месяц выдается на русском языке.
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def get_choice():
    # функция выборки от 18 до 80
    return ((x, x) for x in range(18, 81))


class EmployeeFilter(filters.FilterSet):
    """ Класс который подключает личную фильтрацию для фильтрации возрастов. """
    from_age = filters.ChoiceFilter(method='filter_queryset', label="Возраст от", choices=get_choice)
    to_age = filters.ChoiceFilter(method='filter_queryset', label="до", choices=get_choice)

    class Meta:
        model = Announcement
        fields = ['gender', 'interlocutor', 'purpose_of_acquaintance', 'city']

    def filter_queryset(self, queryset):
        queryset = Announcement.objects.all()
        user_id = self.request.user.pk
        from_age = self.request.query_params.get('from_age')
        to_age = self.request.query_params.get('to_age')
        if from_age and to_age:
            queryset = queryset.filter(
                dob__range=(date.today().replace(year=date.today().year - int(to_age)),
                            date.today().replace(year=date.today().year - int(from_age))))
        return queryset


class AnnouncementListView(generics.ListAPIView):
    """
        Класс для генерации списка из всех объявлений. С фильтрацией по полу, предпочтениям, целям, городам и возрасту
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeFilter
    ordering = ['-created_at']


class AnnouncementDetail(APIView):
    """ Класс предоставляет более подробную информацию об объявлении, так же с возможностью его удалить и ответить.
     Доступно только авторизированным пользователям."""
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    @staticmethod
    def get_object(pk):
        try:
            return Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        announcement = self.get_object(pk=pk)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data)

    def post(self, request, pk, *args, **kwargs):
        an_email = Announcement.objects.get(pk=self.kwargs['pk']).email
        an_text = Announcement.objects.get(pk=self.kwargs['pk']).text

        send_mail('Mianto Love',
                  f"На ваше сообщение '{an_text}' ответили '{request.data['answer']}', вы и дальше можете "
                  f"общаться, вот email пользователя который вам ответил {request.data['email']}",
                  f"leo.urabaros@gmail.com", [f'{an_email}'], fail_silently=False)

        return Response({'email': request.data['email'], 'text': request.data['answer']})

    def delete(self, request, pk, *args, **kwargs):
        announcement = self.get_object(pk=pk)
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConfirmView(FormView):
    """
    Класс который представляет в шаблоне проверку на капчу и возраст пользователя.
    При проверке перенаправляет на главную страницу. Происходит только первый раз
    когда пользователь заходит на сайт.
    """
    form_class = ContactForm
    template_name = 'feed/parts/confirms.html'

    def form_valid(self, form):
        # проверка валидности reCAPTCHA
        if form.is_valid():
            if form.data['access'] == "allowed":
                self.request.session[0] = 'confirm'
                self.request.session['confirm'] = 'access'
                return HttpResponseRedirect("/")
            else:
                return render(self.request, 'feed/parts/toyoungesters.html')
        else:
            return HttpResponse("УПС засекли робота")


def formation_of_ad_repository(gander=None, interlocutor=None,
                               from_age=None, to_age=None, id_purpose=None, code_country=None, code_city=None):
    # Функция которая формирует словарь хранилища объявлений по признакам премиума и дат.
    ad_store = dict()
    ad_premium = list()
    ad_common = list()
    ad_data = list()
    filter_is = False
    if gander is None and interlocutor is None and from_age is None and to_age is None and id_purpose is None and \
            code_country is None and code_city is None:
        ads = Announcement.objects.order_by("-created_at")
    else:
        # Блок кода при котором производится фильтрация объявлений по указанным значениям в настройках
        if id_purpose == 1:
            name_purpose = "ROM"
        elif id_purpose == 2:
            name_purpose = "TRV"
        elif id_purpose == 3:
            name_purpose = "VTL"
        elif id_purpose == 4:
            name_purpose = "SEX"
        else:
            name_purpose = "UNT"
        ads = Announcement.objects.order_by("-created_at")
        city = City.objects.get(code=code_city).name
        ads = ads.filter(
            dob__range=(date.today().replace(year=date.today().year - to_age),
                        date.today().replace(year=date.today().year - from_age)),
            gender=gander, interlocutor=interlocutor,
            purpose_of_acquaintance=name_purpose, city=city)
        filter_is = True

    # Конструкция при которой мы перебираем все проверенные и активные объявления
    for ad in ads:
        if ad.is_active:
            if ad.is_prime:
                # В отдельный список перемещаем объявления оплаченные
                ad_premium.append(ad)
            else:
                # Обычные добавляем в отдельный список с правильным форматом даты
                # Так же исключаем повтор дат
                ad_common.append(ad)
                if ad.created_at.strftime("%d %B %Y") not in ad_data:
                    ad_data.append(ad.created_at.strftime("%d %B %Y"))

    # Блок кода для формирования хранилища объявлений
    if ad_premium:
        ad_store.update({"premium": ad_premium})
    for data in ad_data:
        for ad in ad_common:
            if ad.created_at.strftime("%d %B %Y") == data:
                if filter_is:
                    if len(ad_store) == 0:
                        ad_store.update({"data": {data: [ad]}})
                    elif data in ad_store['data']:
                        ad_store['data'][data].append(ad)
                    else:
                        ad_store['data'].update({data: [ad]})
                else:
                    if len(ad_store) == 1 or len(ad_store) == 0:
                        ad_store.update({"data": {data: [ad]}})
                    elif data in ad_store['data']:
                        ad_store['data'][data].append(ad)
                    else:
                        ad_store['data'].update({data: [ad]})
    return ad_store


class SettingView(FormView):
    """
    Класс настроек. Выдает форму для того что бы пользователь указал данные о том какие объявления хочет найти.
    После чего по указанным значения формируется URL который заносится в куки как и метка о том что была
    произведена фильтрация объявлений. После чего производится переадресация на главную страницу.

     """
    form_class = SettingsForm
    template_name = 'feed/parts/settings.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class,
                                                    'req': self.request.META.get('HTTP_REFERER')})

    def form_valid(self, form):
        if form.is_valid():
            city_code = City.objects.get(name=form.data['city']).code
            country_code = Country.objects.get(pk=City.objects.get(name=form.data['city']).country.pk).code
            if form.data['purpose_of_acquaintance'] == "ROM":
                code_purpose = 1
            elif form.data['purpose_of_acquaintance'] == "TRV":
                code_purpose = 2
            elif form.data['purpose_of_acquaintance'] == "VTL":
                code_purpose = 3
            elif form.data['purpose_of_acquaintance'] == "SEX":
                code_purpose = 4
            else:
                code_purpose = 0
            url = f"{form.data['gender']}-{form.data['interlocutor']}/{int(form.data['from_age'])}" \
                  f"-{int(form.data['to_age'])}/{code_purpose}/{country_code}-{city_code}/"
            self.request.session['confirm'] = "filter"
            self.request.session[1] = "url"
            self.request.session['url'] = url
            return HttpResponseRedirect("/")


def discharge_settings(request):
    if request.session['confirm'] == "filter":
        request.session['confirm'] = "access"
        request.session['url'] = ""
    return HttpResponseRedirect("/")


class CreateAdView(FormView):
    """ Класс при котором выводится форма для создания объявления. После успешного создания переадресовывается на
     предыдущую страницу."""
    form_class = CreateAdForm
    template_name = 'feed/parts/create_ad.html'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class,
                                                    'req': self.request.META.get('HTTP_REFERER')})

    def form_valid(self, form):
        if form.is_valid():
            ad = Announcement()
            ad.email = form.data['email']
            ad.dob = form.data['dob']
            ad.text = form.data['text']
            ad.gender = form.data['gender']
            ad.interlocutor = form.data['interlocutor']
            ad.city = form.data['city']
            ad.save()
            if self.request.user.is_authenticated:
                profile_feed = ProfileFeed()
                profile_feed.profile = self.request.user
                profile_feed.ad = ad
                profile_feed.save()
            return render(self.request, 'feed/parts/notification.html', {'is_things': "crete_ad"})


def create_chat(request, pk):
    # Функция view для создания чата между пользователями. Повторное создания чата между пользователями невозможна.
    an_companion = Announcement.objects.get(pk=pk)
    profile = ProfileFeed.objects.get(ad=an_companion).profile
    second_companion = ProfileMianto.objects.get(pk=request.user.pk)
    if not ProfileMessages.objects.filter(first_interlocutor=profile, second_interlocutor=second_companion) or not \
            ProfileMessages.objects.filter(first_interlocutor=second_companion, second_interlocutor=profile):
        messages_to = ProfileMessages()
        messages_to.first_interlocutor = profile
        messages_to.second_interlocutor = second_companion
        messages_to.save()
        messages_from = ProfileMessages()
        messages_from.first_interlocutor = second_companion
        messages_from.second_interlocutor = profile
        messages_from.uuid_channel = messages_to.uuid_channel
        messages_from.save()
    return HttpResponseRedirect(f"/profile/{request.user.pk}/feed/messages/")


def checkAdView(request, pk, uuid_ad=None):
    # Функция view которая выводит объявления для его подтверждения или удаления
    ads = Announcement.objects.get(pk=pk, uuid_ad=uuid_ad)
    if request.method == 'GET':
        return render(request, 'feed/parts/announcementEdit.html', context={'ads': ads})
    elif request.method == "POST":
        conf_btn = request.POST.get('btnconfirm')
        if conf_btn == "confirm":
            ads.is_confirm = True
            ads.save()
        elif conf_btn == "delete":
            ads.delete()
        return HttpResponseRedirect("/")


def city_auto_complete(request):
    # Функция к которой отправляется запрос в базу данных для получения городов совпадающих по введенным буквам в форму.
    # После чего полученные города заносятся в список и выводится в виде JSON
    if "term" in request.GET:
        city = City.objects.filter(Q(name__iregex=request.GET.get("term")))[:10]
        city_list = list()
        for name_city in city:
            city_list.append(name_city.name)
        return JsonResponse(city_list, safe=False)


def filterAdView(request, gander, interlocutor, from_age, to_age, id_purpose, code_country, code_city):
    # Данная View становится домашней после того как пользователь указал данные в настройках.
    try:
        context = {
            'premium': formation_of_ad_repository(gander, interlocutor, from_age,
                                                  to_age, id_purpose, code_country, code_city)['premium'],
            'data': formation_of_ad_repository(gander, interlocutor, from_age,
                                               to_age, id_purpose, code_country, code_city)['data']
        }
        return render(request, 'feed/parts/feed.html', context=context)
    except KeyError:
        if 'premium' in formation_of_ad_repository(gander, interlocutor, from_age,
                                                   to_age, id_purpose, code_country, code_city):
            context = {
                'premium': formation_of_ad_repository(
                    gander,
                    interlocutor,
                    from_age,
                    to_age,
                    id_purpose,
                    code_country,
                    code_city
                )['premium']
            }
            return render(request, 'feed/parts/feed.html', context)
        elif 'data' in formation_of_ad_repository(gander, interlocutor, from_age,
                                                  to_age, id_purpose, code_country, code_city):
            return render(request, 'feed/parts/feed.html',
                          {'data': formation_of_ad_repository(gander, interlocutor, from_age,
                                                              to_age, id_purpose, code_country, code_city)['data']})
        else:
            return render(request, 'feed/parts/feed.html')


class AdView(FormView):
    """ Класс выводящий информацию об объявлении который выбрал пользователь на главной странице.
        Так же для ответа выводит форму, при отправке ответа, отправляется сообщение создателю объявлению
        об ответе.
     """
    form_class = AnswerForm
    template_name = 'feed/parts/announcement.html'

    def get(self, request, *args, **kwargs):
        checks = False
        an = Announcement.objects.get(pk=self.kwargs['pk'])
        try:
            profile = ProfileFeed.objects.get(ad=an)
            if request.user.is_authenticated:
                if profile.profile.pk != request.user.pk:
                    checks = True
        except ProfileFeed.DoesNotExist:
            checks = False
        return render(request, self.template_name, {'model': an, 'form': self.form_class, 'check': checks})

    def form_valid(self, form):
        if form.is_valid():
            an_email = Announcement.objects.get(pk=self.kwargs['pk']).email
            an_text = Announcement.objects.get(pk=self.kwargs['pk']).text

            send_mail('Mianto Love',
                      f"На ваше сообщение '{an_text}' ответили '{form.data['answer']}', вы и дальше можете "
                      f"общаться, вот email пользователя который вам ответил {form.data['email']}",
                      f"leo.urabaros@gmail.com", [f'{an_email}'], fail_silently=False)

            return render(self.request, 'feed/parts/notification.html', {'is_things': "create_profile"})


def index(request):
    # View главной страницы. Где и происходит вывод всех объявлений как платных так и обычных.
    # Так же данная view выполняет проверку на посещение сайта используя сессии.
    try:
        if request.session['confirm']:
            if request.session['confirm'] == 'filter':
                return HttpResponseRedirect(request.session['url'])
            else:
                try:
                    context = {
                        'premium': formation_of_ad_repository()['premium'],
                        'data': formation_of_ad_repository()['data']
                    }
                    return render(request, 'feed/parts/feed.html', context=context)
                except KeyError:
                    try:
                        if formation_of_ad_repository()['premium']:
                            return render(request, 'feed/parts/feed.html',
                                          {'premium': formation_of_ad_repository()['premium']})
                    except KeyError:
                        try:
                            if formation_of_ad_repository()['data']:
                                return render(request, 'feed/parts/feed.html',
                                              {'data': formation_of_ad_repository()['data']})
                        except KeyError:
                            return render(request, 'feed/parts/feed.html')
    except KeyError:
        return HttpResponseRedirect('confirm-ages/')
