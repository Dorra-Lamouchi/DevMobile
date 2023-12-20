from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, SensorData, Collecte
from .serializers import UserProfileSerializer, SensorDataSerializer, LoginSerializer, CollecteSerializer
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.authtoken.models import Token
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import random
import string

# Create your views here.
@api_view(['POST'])
def register(request):
    if request.method == "POST":
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_profile = serializer.save()
            return Response({
                "email": user_profile.user.email,
                "nom": user_profile.nom,
                "prenom": user_profile.prenom,
                "date_de_naissance": user_profile.date_de_naissance,
                "poids": user_profile.poids,
                "taille": user_profile.taille,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return Response({'error': 'utilisateur inexistant'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileSerializer(user_profile, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user_profile = request.user.userprofile
    serializer = UserProfileSerializer(user_profile)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_data(request):
    serializer = CollecteSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        collecte = serializer.save()
        sensor_data_serializer = SensorDataSerializer(data=request.data.get('sensor_datas', []), many=True)
        if sensor_data_serializer.is_valid():
            sensor_data_serializer.save(collecte=collecte)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(sensor_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data_by_id(request, id):
    try:
        collecte = Collecte.objects.get(id=id, user=request.user)
    except Collecte.DoesNotExist:
        return Response({'error': 'Collecte inexistante'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CollecteSerializer(collecte)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_data_history(request):
    collectes = Collecte.objects.filter(user=request.user)
    serializer = CollecteSerializer(collectes, many=True)
    return Response(serializer.data)


# les vues de l'interface graphique

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                auth_login(request, user)
                return redirect('user-list')  
            else:
                form.add_error(None, "Vous n'êtes pas autorisé à accéder à cette page.")
    else:
        form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})


def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.filter(is_superuser=False).prefetch_related('userprofile') 
    return render(request, 'user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.success(request, "Utilisateur supprimé avec succès.")
    return redirect('user-list')

@login_required
@user_passes_test(is_admin)
def toggle_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "activé" if user.is_active else "désactivé"
    messages.success(request, f"Utilisateur {status} avec succès.")
    return redirect('user-list')

@login_required
@user_passes_test(is_admin)
def reset_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user.set_password(new_password)
    user.save()
    messages.success(request, "Mot de passe réinitialisé avec succès.")
    return redirect('user-list')


@login_required
@user_passes_test(is_admin)
def user_stat(request):
    users_stats = Collecte.objects.values(
        'user__id', 
        'user__userprofile__nom', 
        'user__userprofile__prenom'
    ).annotate(
        total_collectes=Count('id'), 
        total_labels_distincts=Count('label', distinct=True)
    ).order_by('user__id')

    return render(request, 'user_stat.html', {'users_stats': users_stats})