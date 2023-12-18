from .models import UserProfile, SensorData, Collecte
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'], 
            password=validated_data['password']
        )
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'nom', 'prenom', 'date_de_naissance', 'poids', 'taille']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Identifiants incorrects.")


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['collecte', 'accelerometre_x', 'accelerometre_y', 'accelerometre_z', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z', 'latitude', 'longitude']

class CollecteSerializer(serializers.ModelSerializer):
    sensor_datas = SensorDataSerializer(many=True, read_only=True)

    class Meta:
        model = Collecte
        fields = ['id', 'timestamp', 'label', 'sensor_datas']

    def create(self, validated_data):
        # Récupérer l'utilisateur du contexte
        user = self.context['request'].user
        collecte = Collecte.objects.create(user=user, **validated_data)
        return collecte


