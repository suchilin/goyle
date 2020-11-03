from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import meli
from meli.rest import ApiException
from pprint import pprint
import json
import os
from .models import MLToken, MLState
from django.contrib.auth.models import User
from django.contrib.auth import login, logout as do_logout
import secrets
from django.utils import timezone

configuration = meli.Configuration(
    host="https://api.mercadolibre.com"
)


@login_required
def index(request):
    return render(request, 'index.html')


def login_ml(request):
    return render(request, 'login.html')


def to_mercadolibre(request):
    token = secrets.token_hex()
    mltoken = MLState(token=token)
    mltoken.save()
    redirect_uri = 'https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id={client_id}&state={state}&redirect_uri=https://goyleventas.suchil.link/auth/callback'.format(
        client_id=os.environ["ML_APP_ID"], state=token)
    return redirect(redirect_uri)


def logout(request):
    do_logout(request)
    return redirect("auth:login")


@csrf_exempt
def callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state', '123456')

    try:
        token_state = MLState.objects.get(token=state)
        seconds = (timezone.now() - token_state.created).total_seconds()
        if seconds>3:
            raise Exception("too late :'(")
        token_state.delete()
    except Exception as e:
        print("INVALID STATE ", e)
        return redirect("auth:login")

    with meli.ApiClient() as api_client:
        api_instance = meli.OAuth20Api(api_client)
        grant_type = 'authorization_code'
        client_id = os.environ.get('ML_APP_ID')
        client_secret = os.environ.get('ML_APP_SECRET')
        redirect_uri = "http://localhost:8000/auth/callback"
        code = code
        refresh_token = ''

    try:
        # Request Access Token
        api_response = api_instance.get_token(
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            code=code,
            refresh_token=refresh_token
        )
        resource = '/users/me'
        access_token = api_response["access_token"]
        refresh_token = api_response["refresh_token"]
        ml_user_id = api_response["user_id"]
        api_instance = meli.RestClientApi(api_client)
        api_response = api_instance.resource_get(resource, access_token)
        user, created = User.objects.get_or_create(
            username=api_response["nickname"])
        if created:
            user.ml_user_id = ml_user_id
            user.first_name = api_response["first_name"]
            user.last_name = api_response["last_name"]
            user.email = api_response["email"]
            user.is_active = True
            user.is_staff = False
            user.save()
        MLToken.objects.filter(user=user).delete()
        mltoken = MLToken()
        mltoken.user_id = user.pk
        mltoken.ml_user_id = ml_user_id
        mltoken.access_token = access_token
        mltoken.refresh_token = refresh_token
        mltoken.save()
        print("USER: ", user)
        login(request, user)
        return redirect('auth:index')
    except ApiException as e:
        print("Exception when calling OAuth20Api->get_token: %s\n" % e)
    return redirect('auth:login')
