from rest_framework import serializers

from feed.models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    # Класс сериализирующий данные об объявлениях
    class Meta:
        model = Announcement
        fields = '__all__'


class AnswerSerializer(serializers.Serializer):
    # Класс для сериализации ответа на объявление
    email = serializers.EmailField(label="Введите вашу почту")
    answer = serializers.CharField(label="Напишите ответ")