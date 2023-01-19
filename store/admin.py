from django.contrib import admin
from . import models
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ['title', 'price','inventory_status', 'collection']
    list_editable = ['price']
    list_per_page = 10
    search_fields = ['title__istartswith']
    list_filter = ['collection', 'last_update']
    #list_select_related = ['collection']

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    
    # def collection_title(self, product):
    #     return product.collection.title

    class Media:
        css ={
            'all' : ['store/styles.css']
        }


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id',  'placed_at', 'customer']    

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',  'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    autocomplete_fields = ['featured_product']

    def products_count(self, collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({'collection__id': collection.id})
        return format_html('<a href="{}">{}</a>',url, collection.products_count)
        #return collection.products_count
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count = Count('products'))
