from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import LoginProfileForm, RegisterProfileForm
# Create your views here.
from django.views.generic import FormView
from .models import ProfileMianto


class LoginProfileView(FormView):
    form_class = LoginProfileForm
    template_name = 'feed/parts/login_profile.html'

    def form_valid(self, form):
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(login=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active and user.is_confirm:
                    login(self.request, user)
                    return HttpResponse("Успешно вошел в профиль.")
                else:
                    return HttpResponse("Нет доступа к профилю.")
            else:
                return HttpResponse("Пользователя такого не существует.")


class RegisterProfileView(FormView):
    form_class = RegisterProfileForm
    template_name = 'feed/parts/register_profile.html'

    def form_valid(self, form):
        if form.is_valid():
            profile = ProfileMianto.objects.create_user(
                login=form.data['login'],
                email=form.data['email'],
                password=form.data['password'],

            )
            profile.avatar = form.data['avatar']
            profile.gender = form.data['gender']
            profile.dob = form.data['dob']
            profile.save()
            return HttpResponseRedirect("/")


def profileConfirm(request, pk, profile_uuid):
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

