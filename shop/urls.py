from django.contrib import admin
from django.urls import path
from .views import index,signup, cart, orders, signout, show_product, add_to_cart, checkout
from .views import validatePayment, OrderListView, login_required, LoginView, clear_cart

urlpatterns = [
   path('', index, name='homepage'),
   path('signup/', signup),
   path('cart/', cart, name='cartpage'),
   path('clear_cart/', clear_cart, name='clear_cart'),
  
   path('login/', LoginView.as_view(), name='login'),
   path('logout/', signout),
   path('product/<str:slug>', show_product),
   path('addtocart/<str:slug>/<str:size>', add_to_cart),
   path('checkout/', checkout),
   path('validate_payment/', validatePayment),
   path('orders/' , orders , name='orders' ), 
  


   
]
