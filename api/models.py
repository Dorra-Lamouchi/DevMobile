from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_de_naissance = models.DateField()
    poids = models.FloatField()
    taille = models.FloatField()

class Collecte(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=100, blank=True)

class SensorData(models.Model):
    collecte = models.ForeignKey(Collecte, on_delete=models.CASCADE, related_name="sensor_datas", null=True)
    accelerometre_x = models.FloatField()
    accelerometre_y = models.FloatField()
    accelerometre_z = models.FloatField()
    gyroscope_x = models.FloatField()
    gyroscope_y = models.FloatField()
    gyroscope_z = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    
