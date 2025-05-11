from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

# Automatically create a UserProfile when a new User is created















# MikroTik Router configuration model
class MikroTikRouter(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    api_port = models.IntegerField(default=8728)

    def __str__(self):
        return self.name

# Plan model (for internet packages)
class Plan(models.Model):
    name = models.CharField(max_length=100)
    bandwidth_limit = models.CharField(max_length=100)  # Example: "2M/2M"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

# Access ticket model for customers
class AccessTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_code = models.CharField(max_length=100, unique=True)
    plan_name = models.CharField(max_length=100)
    data_limit_mb = models.PositiveIntegerField()
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    router_password = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Ticket {self.ticket_code} for {self.user.username}"

    def calculate_expiry(self, duration_months):
        return timezone.now() + timezone.timedelta(weeks=4*duration_months)

    def set_ticket_duration(self, duration_months):
        self.expiry_date = self.calculate_expiry(duration_months)
        self.save()

    def generate_random_password(self, length=8):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))

    def create_router_user(self):
        from .mikrotik_api import connect_router
        router = MikroTikRouter.objects.first()
        if not router:
            print("No MikroTik router configured.")
            return
        try:
            password = self.generate_random_password()
            api = connect_router(router.ip_address, router.username, router.password)
            api.path("ip", "hotspot", "user").add(
                name=self.ticket_code,
                password=password,
                profile=self.plan_name
            )
            print(f"User {self.ticket_code} created with password {password}")
        except Exception as e:
            print(f"Router sync error: {e}")

    def remove_from_router(self):
        from .mikrotik_api import connect_router
        router = MikroTikRouter.objects.first()
        if not router:
            print("No MikroTik router configured.")
            return
        try:
            api = connect_router(router.ip_address, router.username, router.password)
            users = api.path("ip", "hotspot", "user").get()
            for user in users:
                if user.get('name') == self.ticket_code:
                    api.path("ip", "hotspot", "user").remove(id=user['.id'])
                    print(f"Removed {self.ticket_code} from router.")
                    break
        except Exception as e:
            print(f"Router removal error: {e}")
