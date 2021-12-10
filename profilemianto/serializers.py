from django.contrib.auth import authenticate
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from .models import ProfileMianto, ProfileFeed, ProfileMessages


class ProfileSerializer(serializers.ModelSerializer):
    """ Общий класс сериализации данных профиля. """
    class Meta:
        model = ProfileMianto
        fields = '__all__'


class RegisterProfileSerializer(serializers.ModelSerializer):
    """ Данный класс сериализует данные для регистрации пользователя.  """
    class Meta:
        model = ProfileMianto
        fields = ('login', 'password', 'email', 'dob', 'gender', 'avatar',)

    def create(self, validated_data):
        profile = ProfileMianto.objects.create_user(login=validated_data['login'], email=validated_data['email'],
                                                    password=validated_data['password'])
        if 'avatar' in validated_data:
            profile.avatar = validated_data['avatar']
        profile.gender = validated_data['gender']
        profile.dob = validated_data['dob']
        profile.save()
        return profile


class LoginProfileSerializer(serializers.Serializer):
    """  Класс для сериализации данных при авторизации пользователя. """
    login = serializers.CharField(label="Логин", max_length=255)
    password = serializers.CharField(label="Пароль", max_length=128, write_only=True)

    def validate(self, data):
        login = data.get('login')
        password = data.get('password')

        if login and password:
            user = authenticate(request=self.context.get('request'),
                                username=login, password=password)
            if not user:
                msg = _('Пользователя не существует')
                raise serializers.ValidationError(msg, code='authorization')
            elif not user.is_confirm:
                msg = _('Нет доступа к профилю.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Вы должны указать логин и пароль.')
            raise serializers.ValidationError(msg, code='authorization')

        data['login'] = user
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    """  Класс для сериализации данных при обновлении личных данных. """
    class Meta:
        model = ProfileMianto
        fields = ('login', 'email', 'gender', 'avatar',)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ProfileAdSerializer(serializers.ModelSerializer):
    """ Класс сериализующий данные об объявлениях профиля пользователя. """
    profile_login = serializers.CharField(source='profile', read_only=True)
    adding = serializers.CharField(source='ad', read_only=True)

    class Meta:
        model = ProfileFeed
        fields = ('profile', 'profile_login', 'ad', 'adding' )


class ProfileMessagesSerializer(serializers.ModelSerializer):
    """ Класс сериализующий данные об каналах профиля пользователя. """
    first_interlocutor_login = serializers.CharField(source='first_interlocutor', read_only=True)
    second_interlocutor_login = serializers.CharField(source='second_interlocutor', read_only=True)

    class Meta:
        model = ProfileMessages
        fields = ('first_interlocutor', 'first_interlocutor_login', 'second_interlocutor', 'second_interlocutor_login',
                  'uuid_channel', 'created_at', 'log_file')
