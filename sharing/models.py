import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse


def short_uuid():
    return uuid.uuid4().hex[:6]


def long_uuid():
    return uuid.uuid4().hex[:8]


class User(AbstractUser):
    user_agent = models.CharField(max_length=500, default='')


class SharedUrl(models.Model):
    EXPIRATION_TIME = 24*60*60  # seconds

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    url = models.CharField(max_length=100, unique=True, default=long_uuid)
    password = models.CharField(max_length=100, default=short_uuid)
    created = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)

    @property
    def full_url(self):
        return reverse('open', kwargs={'url': self.url})

    @property
    def full_api_url(self):
        return reverse('api-open', kwargs={'url': self.url})

    def is_fresh(self):
        return (timezone.now() - self.created).seconds < self.EXPIRATION_TIME

    def is_password_valid(self, password):
        return password == self.password

    def check_password(self, password):
        valid = self.is_password_valid(password) and self.is_fresh()
        if valid:
            self.views += 1
            self.save()
        return valid

    def __str__(self):
        return '[%d] %s' % (self.views, self.url)


class SharedLink(models.Model):
    url = models.OneToOneField(SharedUrl, related_name='shared_link', on_delete=models.CASCADE)
    link = models.URLField()

    def __str__(self):
        return "%s -> %s" % (self.url, self.link)


class SharedFile(models.Model):
    url = models.OneToOneField(SharedUrl, related_name='shared_file', on_delete=models.CASCADE)
    file = models.FileField()

    def __str__(self):
        return "%s -> %s" % (self.url, self.file)
