from django.urls import path
from . import views
# from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('cart',views.CartViewSet)
router.register('customers',views.CustomerViewSet)
router.register('orders',views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

cart_Router = routers.NestedDefaultRouter(router, 'cart', lookup='cart')
cart_Router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + cart_Router.urls
# urlpatterns =[
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/',views.ProductDetail.as_view()),
#     path('collection/', views.CollectionList.as_view()),
#     path('collection/<int:pk>',views.CollectionDetail.as_view(), name='collection-detail')
# ]