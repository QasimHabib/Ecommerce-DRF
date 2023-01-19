from django.shortcuts import render
from django.core.mail import send_mail, EmailMessage, mail_admins, BadHeaderError
from templated_mail.mail import BaseEmailMessage
from django.http import HttpResponse
from store.models import Customer, Product, Order,Collection, OrderItem
from tags.models import TaggedItem
from django.db.models import Value, F, Count, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from time import sleep
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .tasks import notify_customers
from rest_framework.views import APIView
import requests
import logging

logger = logging.getLogger(__name__)

# for class based views
class HiView(APIView):
    @method_decorator(cache_page(5 * 60))
    def get(self, request):
        try:
            logger.info("calling httpbin")
            response = requests.get('https://httpbin.org/delay/2')
            data = response.json()
        except request.ConnectionError:
            logger.critical("httpbin is offline")    
        return render(request, 'hello.html', {'name': data})




#for function based views
@cache_page(5 * 60) # all the cache get and set key work is automatically done by cache_page
def say_hi(request):
    response = requests.get('https://httpbin.org/delay/2')
    data = response.json()
    return render(request, 'hello.html', {'name': data})

# def say_hi(request):
#     key = 'httpbin_result' #key name can be anything
#     if cache.get(key) is None:
#         response = requests.get('https://httpbin.org/delay/2')
#         data = response.json()
#         cache.set(key, data)
#     return render(request, 'hello.html', {'name': cache.get(key)})

def say_hello(request):
    notify_customers.delay('Hellooo')

    # try:
    #     # meessage = EmailMessage('subject','message','info@qasimhabib.com', ['john.wick46301@gmail.com'])
    #     # meessage.attach_file('playground/static/images/dog.jpg')
    #     # meessage.send()
    #     message = BaseEmailMessage(template_name='emails/hello.html', context={'name': 'Qasim'})
    #     message.send(['john.wick46301@gmail.com'])
    # except BadHeaderError:
    #     pass    

    return render(request, 'hello.html', {'name': 'Qasim'})
    # cus = Customer.objects.only('first_name', 'email')[0:10]
    # print("my name is qasim")

    #Select_realted   for selecting the related felids(Relationship Fields)   used in one to may  products=> collection.
    #prefetch_realted   for selecting the related felids(Relationship Fields)   used in many to may or reverse ForeignKeys. products=> Promotions.

    # prod = Product.objects.prefetch_related('promotions').select_related('collection').all()
    #Get the last 5 orders with their Custoners and items (includig Product)
    # order = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    
    # # queryset = Customer.objects.annotate(new_id = F('id') + 1 )
    # queryset = Customer.objects.annotate(full_name = Concat('first_name', Value(' '), 'last_name'))

    #Count number of orders for each Coustmer
    # queryset = Customer.objects.annotate(total_orders = Count('order'))

    # discount_price = ExpressionWrapper(F('price') * 0.7, output_field=DecimalField())
    # queryset = Product.objects.annotate(discounted_price=discount_price)

    #Query the Generic Relationships
    # content_type = ContentType.objects.get_for_model(Product)
    # queryset = TaggedItem.objects.select_related('tag').filter(content_type = content_type, object_id = 1)

    # collection = Collection()
    # collection.title = 'Video Games'
    # collection.featured_product = Product(pk=1)
    # # collection.featured_product_id = 1   can also use this
    # collection.save()

    # collection = Collection.objects.get(pk=11)
    # collection.featured_product_id = 2
    # collection.save()
    # # This approach executed 2 queries 1st for get the specific id 2nd for the update

    # Collection.objects.filter(pk=11).update(featured_product=None)
    # # This above approach executed just upate Query

    # collection = Collection(pk=11)
    # collection.delete()

    # Here we wrap Order and OrderItem in Transaction. so Either both of the operations Commited together.
    # Or If one of Operation fails then both changes will rollback.
    # with transaction.atomic():
    #     order = Order()
    #     order.customer_id = 1
    #     order.save()

    #     item = OrderItem()
    #     item.order = order
    #     item.product_id = 1
    #     item.quantity = 1
    #     item.unit_price = 10
    #     item.save()

    

    