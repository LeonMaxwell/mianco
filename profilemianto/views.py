from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import update_last_login
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import LoginProfileForm, RegisterProfileForm, UpdateProfileForm
from .serializers import LoginProfileSerializer, RegisterProfileSerializer, ProfileSerializer, UpdateProfileSerializer, \
    ProfileAdSerializer, ProfileMessagesSerializer
from django.views.generic import FormView, UpdateView
from .models import ProfileMianto, ProfileFeed, ProfileMessages
from django.forms.models import model_to_dict


# API

class LoginAPIView(APIView):
    """ Авторизация пользователя в системе. """
    queryset = ProfileMianto
    serializer_class = LoginProfileSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginProfileSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['login']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"status": status.HTTP_200_OK, "Token": token.key})


class LogoutAPIView(APIView):
    """ Выход пользователя из системы """
    def get(self, request, format=None):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class RegisterProfileAPIVIew(generics.CreateAPIView):
    """ Регистрация пользователя """
    queryset = ProfileMianto
    serializer_class = RegisterProfileSerializer


class ProfileAPIDetail(APIView):
    """  Вывод детальной информации о пользователе по личному ключу. С возможностью обновления и удаления профиля. """
    serializer_class = UpdateProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get_object(pk):
        try:
            return ProfileMianto.objects.get(pk=pk)
        except ProfileMianto.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        if request.user.pk == pk:
            profile = self.get_object(pk=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        else:
            return Response("Войдите в свой профиль")

    def put(self, request, pk, *args, **kwargs):
        if request.user.pk == pk:
            profile = self.get_object(pk=pk)
            serializer = UpdateProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Войдите в свой профиль")

    def delete(self, request, pk, *args, **kwargs):
        if request.user == pk:
            profile = self.get_object(pk=pk)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("Войдите в свой профиль")


class ProfileFeedAPIView(APIView):
    """ Вывод информации о объявлениях которые принадлежать профилю пользователя. """
    serializer_class = ProfileAdSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get_object(pk):
        try:
            profile = ProfileMianto.objects.get(pk=pk)
            return ProfileFeed.objects.filter(profile=profile)
        except ProfileFeed.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        if request.user.pk == pk:
            profile = self.get_object(pk=pk)
            serializer = ProfileAdSerializer(profile, many=True)
            return Response(serializer.data)
        else:
            return Response("Войдите в свой профиль")


class ProfileMessagesAPIView(APIView):
    """ Вывод информации о каналах которые принадлежать профилю пользователя. """
    serializer_class = ProfileMessagesSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get_object(pk):
        try:
            profile = ProfileMianto.objects.get(pk=pk)
            return ProfileMessages.objects.filter(first_interlocutor=profile)
        except ProfileMessages.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        if request.user.pk == pk:
            profile = self.get_object(pk=pk)
            serializer = ProfileMessagesSerializer(profile, many=True)
            return Response(serializer.data)
        else:
            return Response("Войдите в свой профиль")


class LoginProfileView(FormView):
    """ Класс для входа пользователя в профиль с переадресацией.  """
    form_class = LoginProfileForm
    template_name = 'feed/parts/login_profile.html'

    def form_valid(self, form):
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(login=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_admin:
                    login(self.request, user)
                    return HttpResponseRedirect("/profile/admin/")
                elif user.is_active and user.is_confirm:
                    login(self.request, user)
                    return HttpResponseRedirect(f"/profile/{user.pk}/feed/")
                else:
                    form.add_error("username", "Нет доступа к профилю.")
                    return render(self.request, self.template_name, {"form": form})
            else:
                form.add_error("username", "Такого пользователя не существует")
                return render(self.request, self.template_name, {"form": form})


class RegisterProfileView(FormView):
    """ Класс регистрации пользователей на сайт.  """
    form_class = RegisterProfileForm
    template_name = 'feed/parts/register_profile.html'

    def form_valid(self, form):
        if form.is_valid():
            profile = ProfileMianto.objects.create_user(
                login=form.data['login'],
                email=form.data['email'],
                password=form.data['password'],
            )
            if 'avatar' in form.files:
                profile.avatar = form.files['avatar']
            profile.gender = form.data['gender']
            profile.dob = form.data['dob']
            profile.save()
            return HttpResponseRedirect("/")


class SettingsProfileView(UpdateView):
    """ Класс предоставляющий зарегистрированным пользователям изменять личные данные. """
    model = ProfileMianto
    form_class = UpdateProfileForm
    template_name = "feed/parts/settings_profile.html"

    def get(self, request, *args, **kwargs):
        profile = ProfileMianto.objects.get(pk=self.kwargs['pk'])
        form = self.form_class(initial=model_to_dict(profile))
        return render(request, self.template_name, {'form': form, 'prof': profile})

    def form_valid(self, form):
        if form.is_valid():
            cur_email = self.request.user.email
            profile = ProfileMianto.objects.get(pk=self.kwargs['pk'])
            form = self.form_class(self.request.POST, instance=profile)
            form.save()
            if cur_email != form.data['email']:
                profile.is_confirm = False
                profile.save()
            return HttpResponseRedirect("/")


def profile_feed(request, pk):
    # функция вывода информации о пользователе
    if request.user.is_authenticated and request.user.pk == pk:
        profile = ProfileMianto.objects.get(pk=pk)
        try:
            profile_ad = ProfileFeed.objects.filter(profile=profile)[::-1]
            context = {
                "prof": profile,
                "profile_ad": profile_ad,
            }
            return render(request, "feed/parts/feed_profile.html", context=context)
        except ProfileFeed.DoesNotExist:
            return render(request, "feed/parts/feed_profile.html", context={"prof": profile})
    else:
        return HttpResponseRedirect("/profile/")


def profile_logout(request, pk):
    # функция для выхода из системы
    if request.user.pk == pk:
        logout(request)
    return HttpResponseRedirect("/")


def chat_list(request, pk):
    # функция вывода чатов пользователя
    profile = ProfileMianto.objects.get(pk=pk)
    channels = ProfileMessages.objects.filter(first_interlocutor=profile)[::-1]
    return render(request, 'feed/parts/channels_profile.html', {'prof': profile, 'channel': channels})


def room(request, pk, id_messages):
    # функция которая предоставляет информацию потребителям о канале
    if request.user.is_authenticated:
        if request.user.pk == pk:
            profile = ProfileMianto.objects.get(pk=pk)
            channels = ProfileMessages.objects.get(uuid_channel=id_messages, first_interlocutor=profile)
            return render(request, 'feed/parts/room_profile.html', {
                'room_name': id_messages,
                'channel': channels,
                'prof': profile,
            })
    return HttpResponseRedirect("/profile/")


def profileConfirm(request, pk, profile_uuid):
    # функция для подтверждения профиля
    profile = ProfileMianto.objects.get(pk=pk, profile_uuid=profile_uuid)
    if request.method == "GET":
        return render(request, "feed/parts/confirm_profile.html", context={"prof": profile})
    elif request.method == "POST":
        conf_btn = request.POST.get('btnconfirm')
        if conf_btn == "confirm":
            profile.is_confirm = True
            profile.save()
        elif conf_btn == "delete":
            profile.delete()
        return HttpResponseRedirect("/")


def branch_profile(request):
    # основная view которая переадресует пользователя исходя из его прав на соответствующую страницу.
    if request.user.is_authenticated:
        if request.user.is_admin:
            return HttpResponseRedirect("admin/")
        elif not request.user.is_confirm:
            return HttpResponse("У вас нет доступа к личному профилю, кренитесь на главную страницу.")
        else:
            return HttpResponseRedirect(f'{request.user.pk}/feed/')
    else:
        return HttpResponseRedirect('login/')
