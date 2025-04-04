from django.db import models
from django.contrib.auth.models import *

class UserInfoManager(BaseUserManager):
    def create_user(self, email, name, phone, type, password=None):
        if not phone:
            raise ValueError('Users must have an phone number')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            type=type,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, type, password):
        user = self.create_user(
            email=email,
            password=password,
            name=name,
            phone=phone,
            type=type,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Addition info of a User
class UserInfo(AbstractUser):
    username = None
    first_name = None
    last_name = None
    image = models.ImageField(upload_to='profile/images', null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20,unique=True)
    type = models.CharField(max_length=100,choices=[('superadmin','superadmin'),('admin','admin'),('employee','employee')])
    block = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name','type','email']

    objects = UserInfoManager()