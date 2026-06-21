from django.contrib.auth.models import BaseUserManager
class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("شماره تلفن باید وارد شود")

        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_deleted', False)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("سوپریوزر باید پسورد داشته باشد")

        return self.create_user(phone, password, **extra_fields)