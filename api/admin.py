from django.contrib import admin
from .models import UserProfile, SensorData, Collecte

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(SensorData)
admin.site.register(Collecte)
