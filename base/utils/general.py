import base64
import logging
import os
import random
from datetime import datetime

import jdatetime
import requests
from sentry_sdk import capture_message
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad
from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse
from djmoney.money import Money
from kavenegar import *
from django.conf import settings

logger = logging.getLogger(__name__)


def rial_to_toman(money):
    """Converts Money object from Rial to Toman."""
    return Money(money.amount / 10, money.currency)


def toman_to_rial(amount):
    if isinstance(amount, Money):
        return Money(amount.amount * 10, amount.currency)
    else:
        return Money(amount * 10, 'IRR')


def get_price(item):
    try:
        params = {
            'item': item,
            'date': jdatetime.date.today(),
        }
        url = f"{settings.PRICE_API_URL}?api_key={settings.PRICE_API_KEY}"
        response = requests.get(url, params=params)
        return response.json()
    
    except APIException as e:
        logger.error(f"Request exception for item: {item}", str(e))
        return JsonResponse({'error': 'An error occured.'}, status=503)     

    except HTTPException as e:
        logger.error(f"HTTP error for item: {item}", str(e))
        return JsonResponse({'error': 'An error occured.'}, status=503)        


def order_id_generator():
    now = datetime.now()
    random_nubmer = random.randint(100, 1000)
    order_id = f"{int(now.timestamp()*1000000)}{random_nubmer}"
    return order_id


def handle_payment_redirect(payment_category, amount, order_id, user):

    try:
        payment = payment_request(payment_category, amount, order_id)
        if payment['ResCode'] == 0:
            payment_request_token = payment['Token']

            # Store the token and user_id in cache
            cache_key = f"payment_request_token_{payment_request_token}"
            cache.set(cache_key, user.id, timeout=3600)
            success_url = f"{settings.IPG_URL}/melli/sadad.shaparak.ir/VPG/Purchase/?token={payment_request_token}"
            return HttpResponseRedirect(success_url)
        
        logger.error(f"Payment request failed for order id: {order_id} with ResCode: {payment['ResCode']}")
        capture_message("Payment request failed", level="error")
        return JsonResponse({'error': 'An error occured.'}, status=400)

    except Exception as e:
        logger.error(f"Payment request failed: {str(e)}")
        capture_message(f"Payment request failed: {e}", level="error")
        return JsonResponse({'error': 'An error occured.'}, status=503)


def des_encrypt(data):
    base64_key = settings.TERMINAL_KEY
    decoded_key = base64.b64decode(base64_key)
    key = decoded_key[:24]
    block_size = 8
    padded_data = pad(data.encode(), block_size)
    cipher = DES3.new(key, DES3.MODE_ECB)
    encrypted_data = cipher.encrypt(padded_data)
    base64_encoded_data = base64.b64encode(encrypted_data)
    return base64_encoded_data


def payment_request(payment_category, Amount, OrderId):

    TERMINAL_ID = settings.TERMINAL_ID
    MERCHANT_ID = settings.MERCHANT_ID

    sign_data_input = f"{TERMINAL_ID};{OrderId};{Amount}"
    SignData = des_encrypt(sign_data_input)

    url = f"{settings.IPG_URL}/melli/sadad.shaparak.ir/VPG/api/v0/Request/PaymentRequest"

    if payment_category in ['wallet', 'order']:
        ReturnUrl = f"{settings.APP_URL}/api/v1/{payment_category}/payment-result/"

    params = {
        "MerchantId": MERCHANT_ID,
        "TerminalId": TERMINAL_ID,
        "Amount": Amount,
        "OrderId": OrderId,
        "LocalDateTime": datetime.now(),
        "ReturnUrl": ReturnUrl,
        "SignData": SignData,
    }

    try:
        response = requests.get(url, params=params)
        
        json_response = response.json()
        if response.status_code == 200 and json_response['ResCode'] == 0:
            logger.debug(f"Payment reqeust success for order id: {OrderId}")
            return response.json()
    
        else:
            logger.error(f"Payment request failed for order id: {OrderId} with ResCode: {json_response['ResCode']}")
            return JsonResponse({'error': 'An error occured.'}, status=400)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Payment request failed for order id: {OrderId}", str(e))
        return JsonResponse({'error': 'An error occured.'}, status=503)


def verify_payment(Token):

    SignData = des_encrypt(Token)

    url = f"{settings.IPG_URL}/melli/sadad.shaparak.ir/VPG/api/v0/Advice/Verify"

    params = {
        'Token': Token,
        'SignData': SignData
    }
    try:
        response = requests.post(url, params=params)
        
        json_response = response.json()
        if response.status_code == 200 and json_response['ResCode'] == 0:
            logger.debug("Payment verification success.")
            return response.json()
        else:
            logger.error(f"Payment verification failed with ResCode: {json_response['ResCode']}")
            return JsonResponse({'error': 'An error occured.'}, status=400)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Payment verification failed.", str(e))
        return JsonResponse({'error': 'An error occured.'}, status=503)
