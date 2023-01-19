from django.urls import path
from . import views

urlpatterns =[
    path('hello/', views.say_hello),
    path('hi/', views.HiView.as_view()),
    # path('hi/', views.say_hi)
]