from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from .validators import *


class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None):
        if not mobile:
            raise ValueError('the mobile field is required')
        
        user = self.model(mobile=mobile)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None):
        user = self.create_user(mobile=mobile, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    # USER_TYPE_CHOICES = [
    #     ("client", "client"),
    #     ("manager", "manager"),
    # ]

    GENDER_CHOICES = [
        ("m", "male"),
        ("f", "female"),
    ]

    mobile = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    national_id = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(null=True, default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # user_type = models.CharField(
    #     max_length=7,
    #     choices=USER_TYPE_CHOICES,
    #     default="client",
    # )

    objects = UserManager()

    USERNAME_FIELD = 'mobile'

    def __str__(self):
        return self.mobile


class TempUser(models.Model):
    mobile = models.CharField(max_length=11, unique=True, db_index=True, validators=[validate_phone_number])
    token = models.IntegerField()
    is_blocked = models.BooleanField(default=False)
    try_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.mobile

    def is_expired(self):
        if self.is_blocked:
            return True
        elif datetime.now(timezone.utc) - self.created_at > timedelta(minutes=2):
            self.is_blocked = True
            self.save()
            return True
        else:
            if self.try_number > 3:
                self.is_blocked = True
            self.try_number += 1
            self.save()
            return False


class IP(models.Model):
    ip = models.CharField(max_length=255, unique=True, db_index=True)
    is_blocked = models.BooleanField(default=False)
    try_number = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.ip

    # 2min
    # 5min
    def can_access(self):

        t = datetime.now(timezone.utc) - self.updated_at

        if self.is_blocked:
            if t > timedelta(minutes=5):
                self.is_blocked = False
                self.try_number = 2
                self.save()
                return True, "you can access"
            else:
                next_t = timedelta(minutes=5) - t
                return False, "try " + str(int(next_t.total_seconds())) + " seconds later."

        else:
            if t > timedelta(minutes=2):
                self.try_number += 1
                if self.try_number > 3:
                    self.is_blocked = True
                self.save()
                return True, "you can access"
            else:
                next_t = timedelta(minutes=2) - t
                return False, "try " + str(int(next_t.total_seconds())) + " seconds later."