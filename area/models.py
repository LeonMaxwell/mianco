from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    code = models.CharField(max_length=255, verbose_name="Код")

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self):
        return self.name


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна")
    name = models.CharField(max_length=255, verbose_name="Название")
    code = models.CharField(max_length=255, verbose_name="Код")

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return f'{self.country.name}, г.{self.name}'
