import threading
import time
import logging

from django.apps import AppConfig

from .utils.general import get_price, toman_to_rial
logger = logging.getLogger(__name__)


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        def update_price():
            from .models import Product
            while True:
                time.sleep(24*3600) #TODO: https://github.com/jd/tenacity
                price = get_price('18ayar')
                logger.info('getting price.')
                products = Product.objects.filter(category='18ayar')
                
                for product in products:
                    price_in_toman = int(price['18ayar']['value']) * (1 + product.buy_commission/100)
                    price_in_rial = toman_to_rial(price_in_toman)
                    product.price = price_in_rial
                    product.save()


        t = threading.Thread(target=update_price)
        t.daemon = True
        t.start()
