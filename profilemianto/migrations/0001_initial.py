# Generated by Django 3.2.9 on 2021-12-07 18:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import feed.models
import profilemianto.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileMianto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('login', models.CharField(max_length=255, unique=True, verbose_name='Логин')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Электронная почта')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=profilemianto.models.get_file_path, verbose_name='Аватар')),
                ('dob', models.DateField(blank=True, null=True, validators=[feed.models.MinAgeValidator(18)], verbose_name='Дата рождения')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Парень'), ('F', 'Девушка')], max_length=20, null=True, verbose_name='Пол')),
                ('profile_uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('is_confirm', models.BooleanField(default=False, verbose_name='Статус подтверждения')),
                ('is_active', models.BooleanField(default=True, verbose_name='Статус активности')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Права администратора')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Права доступа')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
                'db_table': 'profile',
                'ordering': ('-created_at', '-updated_at'),
            },
        ),
        migrations.CreateModel(
            name='ProfileFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feed.announcement', verbose_name='Объявление')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Стена профиля',
                'verbose_name_plural': 'Стены профиля',
            },
        ),
    ]