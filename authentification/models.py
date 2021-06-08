import datetime

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User as BaseUser
from django.db import models

BaseUser._meta.get_field('email')._unique = True


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    return 'user_{0}/avatar_{1}.jpg'.format(instance.user.id, str(datetime.datetime.now()))


class UserProfile(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    address = models.CharField(default='', max_length=150, blank=True)
    city = models.CharField(default='', max_length=50, blank=True)
    country = models.CharField(default='', max_length=30, blank=True)
    postalcode = models.IntegerField(default=0000, blank=True)
    avatar = models.ImageField(default='', upload_to=user_directory_path, blank=True)
