from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from .signals import order_created
from .models import Product, Collection, Review, Cart, CartItem,Customer, Order, OrderItem, ProductImage

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    
    products_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id','title','slug','inventory','price','description','discounted_price','collection', 'images']

    discounted_price = serializers.SerializerMethodField(method_name='calculate_discount')

    def calculate_discount(self, produt:Product):
        return produt.price * Decimal(0.7)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)    


class SimpleProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'price']   


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cartitem: CartItem):
        return cartitem.quantity * cartitem.product.price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'total_price', 'items']


class AddCartItemSerilizer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No Product with given Id is found")
        return value


    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
           cart_item =  CartItem.objects.get(cart_id=cart_id, product_id=product_id)
           cart_item.quantity += quantity
           cart_item.save()
           self.instance = cart_item
        except: 
           self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']  


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

class OrederItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrederItemSerializer(many=True)
    class Meta: 
        model = Order
        fields = ['id', 'placed_at', 'payment_status', 'customer', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No Cart with given id is found")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The Cart is Empty")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=self.validated_data['cart_id'])

            order_items = [OrderItem(order=order, product=item.product, unit_price=item.product.price, quantity=item.quantity) for item in cart_items]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()
            
            order_created.send_robust(self.__class__, order=order)

            return order




        

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6,decimal_places=2)
#     discounted_price = serializers.SerializerMethodField(method_name='calculate_discount')
#     # collection = serializers.StringRelatedField()
#     # collection = CollectionSerializer()
#     collection =  serializers.HyperlinkedRelatedField(
#         queryset = Collection.objects.all(),
#         view_name= 'collection-detail'
#     )

#     def calculate_discount(self, produt:Product):
#         return produt.price * Decimal(0.7)