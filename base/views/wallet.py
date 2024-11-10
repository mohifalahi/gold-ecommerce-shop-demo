import decimal
import logging

from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from rest_framework import status
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from base.forms import WalletDepositForm
from base.models import Order, Wallet
from base.utils.general import (handle_payment_redirect,
                                      order_id_generator, toman_to_rial,
                                      verify_payment)
from base.utils.order import get_user_id_by_token
from base.utils.wallet import (create_buy_transaction,
                                     create_deposit_transaction,
                                     update_order_on_pay,
                                     update_product_stock_on_pay,
                                     update_user_asset_on_pay,
                                     update_wallet_on_deposit,
                                     update_wallet_on_pay)

precision = decimal.Decimal('0.0')
logger = logging.getLogger(__name__)


class WalletDepositView(FormView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    form_class = WalletDepositForm
    template_name = 'wallet-deposit.html'

    def form_valid(self, form):
        wallet_id = self.kwargs.get('pk')
        user = self.request.user
        wallet = get_object_or_404(Wallet, id=wallet_id, user=user.id)

        deposit = form.cleaned_data['deposit']
        order_id = order_id_generator()
        deposit_in_rial = toman_to_rial(deposit)
        
        redirect_response = handle_payment_redirect("wallet", deposit_in_rial.amount, order_id, user)
        if redirect_response:
            return redirect_response

        return super().form_valid(form)
    
    def get_success_url(self):
        return self.success_url


class WalletPayOrderAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wallet_id = self.kwargs.get('pk')
        id = self.kwargs.get('id')

        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user)
            order = Order.objects.get(id=id, user=request.user)
        except Wallet.DoesNotExist:
            return Response({'detail': 'Wallet not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        total_price = order.total_price

        if wallet.balance >= total_price:
            try:
                with transaction.atomic():

                    update_user_asset_on_pay(order)
                    
                    update_order_on_pay(order)

                    update_wallet_on_pay(wallet, total_price)

                    create_buy_transaction(order, total_price)

                    update_product_stock_on_pay(order)
                    
                    balance_data = {
                        "amount": str(wallet.balance.amount), 
                        "currency": str(wallet.balance.currency)
                    }

                    return Response({"message": "Order Payment Successful!",
                                    "balance": balance_data,
                                    "description": "Payment via wallet"
                                    }, status=status.HTTP_200_OK)
            
            except IntegrityError as e:
                return Response({"error": f"Transaction failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"error": "Not enough balance."}, status=status.HTTP_400_BAD_REQUEST)


class WalletPaymentResultAPIView(APIView):

    def post(self, request):
        try:
            data = request.POST

            order_id = data.get("OrderId")
            token = data.get("Token")
            res_code = data.get("ResCode")

            if res_code == '0':
                payment = verify_payment(token)
                if payment['ResCode'] == 0:

                    try:
                        with transaction.atomic():

                            user_id = get_user_id_by_token(token)

                            wallet = update_wallet_on_deposit(Wallet, payment, user_id)

                            create_deposit_transaction(wallet, payment)
                            
                            balance_data = {
                                "amount": str(wallet.balance.amount),
                                "currency": str(wallet.balance.currency)
                            }

                            return Response({"message": "Wallet Payment Successful!",
                                        "balance": balance_data,
                                        "description": payment['Description']
                                        }, status=status.HTTP_200_OK)
                        
                    except IntegrityError as e:
                        logger.error(f"Transaction failed for wallet {wallet.id}: {e}")
                        return Response({"error": "Transaction could not be completed. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": "Payment failed."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(f"An error occurred. {e}")
            return Response({"error": "An error occurred. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)