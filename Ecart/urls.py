from django.urls import URLPattern, path
from sympy import cancel
from . import views

urlpatterns = [path('show/', views.Product_list, name = 'show'),
               path('search/', views.search_api, name = 'search'),
               path('', views.Form_in, name = 'login'),
               path('logout/', views.Form_out, name = 'logout'),
               path('add_to_cart/<int:id>', views.add_to_cart, name = 'add_to_cart'),
               path('cart/',views.Show_cart, name = 'cart'),
               path('del_cart/<int:id>',views.Remove_cart, name = 'del_cart'),
               path('orders/', views.Order_details, name = 'orders'),
               path('cancel_order/<int:cart_id>/<int:order_id>',views.Cancel_order, name = 'cancel_order'),
               path('update_cart/<int:id>', views.Update_cart, name = 'update_cart'),
               path('create_order/', views.Create_order, name = 'create_order'),
               path('wish/<int:id>', views.Wish_list_products, name = 'wish'),
               path('wish_list/', views.Show_wish, name = 'wish_list'),
               path('remove_wish/<int:id>', views.Remove_wish, name = 'remove_wish'),
               path('current_order/', views.current_order, name = 'current_order'),
               path('product_api/', views.product_api, name = 'product_api' ),
               path('cart_api/', views.cart_api, name = 'cart_api' ),
               path('home/', views.charge, name = 'home'),
               path('order_api/', views.order_api, name = 'order_api')
               ]

'''path('search_api/', views.search_api, name = 'search_api' ),'''