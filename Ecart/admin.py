from django.contrib import admin
from Ecart.models import *
class Select_for(admin.StackedInline):
    model = Cart

class Product_list(admin.ModelAdmin):
    list_display = ('id', 'title', 'brand', 'price')
    search_fields = ('name',)
    inlines = [Select_for]
    list_editable = ('price',)
    list_filter = ('brand',)

admin.site.register(Product, Product_list)

class Cart_list(admin.ModelAdmin):
    list_display = ('id','user', 'product', 'price', 'quantity', 'status')
    search_fields = ('status','product__name')
    list_editable = ('price',)
   
admin.site.register(Cart, Cart_list)
class Order_list(admin.ModelAdmin):
    list_display = ('id','user', 'order_price', 'order_status')
admin.site.register(Order, Order_list)

admin.site.register(Wish)