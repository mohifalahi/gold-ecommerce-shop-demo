import os

# from celery import shared_task
from django.conf import settings
from kavenegar import *


# @shared_task
def send_sms(receptor, token):
    try:
        key = settings.SMS_API_KEY
        api = KavenegarAPI(key)
        params = {
            'receptor': receptor,
            'template': 'metahome',
            'token': token,
            'type': 'sms',
        }   
        response = api.verify_lookup(params)
        print(response)
    except APIException as e: 
        print(e)
    except HTTPException as e: 
        print(e)


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
