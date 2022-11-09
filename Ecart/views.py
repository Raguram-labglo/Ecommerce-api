from django.shortcuts import render, redirect
from django.db.models import Q
from Ecart.forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum
from .models import pending, success, failed
import json
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


import stripe
endpoint_secret = 'whsec_66e4f8db2c43802cc38b65b57f02618cdbf8e0f5c5421491afd321a9fe66a35b'
stripe.api_key = settings.STRIPE_SECRET_KEY


def Form_in(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('show')
        else:
            form = AuthenticationForm()
            messages.info(request, 'username or password is incorrect')
            return render(request, 'log_in.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'log_in.html', {'form': form})


def Form_out(request):

    logout(request)
    return redirect('login')


@login_required(login_url='/ecommerce/')
def Product_list(request):

    all_product = Product.objects.all()
    wish, list = Wish.objects.get_or_create(user=request.user)
    wish_product = wish.favourite.all()
    alredy_wish = wish_product
    wish_product_list = []
    for product in alredy_wish:
        wish_product_list.append(product)
    return render(request, 'show.html', {'products': all_product, 'alredy': wish_product_list})


@login_required(login_url='/ecommerce/')
def Search(request):

    context = {}
    if 'need' in request.POST:
        find = request.POST.get('need')
        all = Product.objects.all()
        context['product list'] = all
        suggetions_qs = Product.objects.filter(Q(title__icontains=find) | Q(
            name__icontains=find) | Q(brand__icontains=find) & Q(in_stocks=True))
        context['data'] = suggetions_qs
    return render(request, 'search.html', context)


@login_required(login_url='/ecommerce/')
def add_to_cart(request, id):
    if request.method == "POST":
        context = {}
        product_selected = Product.objects.get(id=id)
        price_of_product = product_selected.price
        add_cart = Cart.objects.create(
            user=request.user, product=product_selected, price=price_of_product)
        context['data'] = add_cart.product
        context['pricedata'] = add_cart
    return redirect(Product_list)


@login_required(login_url='/ecommerce/')
def Show_cart(request):

    cart_list = Cart.objects.filter(Q(user=request.user) & Q(is_active=True))
    total_price = cart_list.aggregate(Sum('price'))
    cart_total_price = total_price['price__sum']
    context = {'data': cart_list, 'total_price': cart_total_price}
    return render(request, 'cart.html', context)


@login_required(login_url='/ecommerce/')
def Update_cart(request, id):
    quantity = request.POST.get('quantity')
    update_cart = Cart.objects.get(id=id)
    update_cart.quantity = quantity
    update_cart.price = int(update_cart.product.price) * \
        int(update_cart.quantity)
    update_cart.save()
    return redirect(Show_cart)


@login_required(login_url='/ecommerce/')
def Remove_cart(request, id):
    if request.method == "POST":
        cart_del = Cart.objects.get(id=id)
        cart_del.delete()
    return redirect(Show_cart)


@login_required(login_url='/ecommerce/')
def Order_details(request):

    get_order = Order.objects.filter(user=request.user.id)
    if get_order == None:
        context = {'message': 'your order page is empty'}
        return render(request, 'order_details.html', context)
    total_orders_price = Order.objects.filter(Q(user=request.user) & Q(
        order_items__status=pending)).aggregate(Sum('order_items__price'))
    price = total_orders_price['order_items__price__sum']
    if price == None:
        get_order = Order.objects.filter(user=request.user.id)
        context = {'order_product': get_order}
        return render(request, 'order_details.html', context)
    tax = int(18/100*price)
    tax_price = price + tax
    order_product = get_order
    context = {'order_product': get_order,  'price': price,
               'tax': tax, 'tax_price': tax_price}
    return render(request, 'order_details.html', context)


'''@login_required(login_url='/ecommerce/')
def current_order(request):
    get_order = Cart.objects.filter(Q(user=request.user) & Q(is_active=True))
    orders = Order.objects.create(user=request.user, order_status=pending)
    orders.order_items.add(
        *Cart.objects.filter(Q(user=request.user) & Q(is_active=True)))
    orders.save()
    prod = orders.order_items.values('price')
    inactive = Cart.objects.filter(user=request.user)
    inactive.update(is_active=False)
    if orders == None:
        context = {'message': 'your have no current orders'}
        return render(request, 'order_details.html', context)
    total_orders_price = orders.aggregate(Sum('price'))
    price = total_orders_price['price__sum']
    if price == None:
        context = {'message': 'your have no current orders'}
        return render(request, 'current_order.html', context)
    get_order.order_price = int(price)
    tax = int(18/100*price)
    total_price = int(price + tax)
    
    return render(request, 'current_order.html', {'detail': get_order, 'tax': tax, 'tax_price': tax,  'total': total_price, 'key': key})'''


@login_required(login_url='/ecommerce/')
def Create_order(request):

    orders = Order.objects.create(user=request.user, order_status=pending)
    orders.order_items.add(*Cart.objects.filter(Q(user=request.user) & Q(is_active=True)))
    orders.save()
    inactive = Cart.objects.filter(user=request.user)
    inactive.update(is_active=False)
    get_order = Order.objects.filter(
        Q(user=request.user.id) & Q(order_status=pending)).last()
    current_products = get_order.order_items.filter(status=pending).all()
    price_of_products = current_products.values(
        'price').aggregate(Sum('price'))['price__sum']

    get_order.order_price = int(price_of_products)
    tax = int(18/100*price_of_products)
    get_order.tax_price = tax + int(price_of_products)
    price = tax + int(price_of_products)
    
    get_order.save()
    # stripe.PaymentIntent.create(amount = int(price), currency = 'inr', payment_method_types = ['card'])
    return redirect(Order_payment)


@login_required(login_url='/ecommerce/')
def Cancel_order(request, cart_id, order_id):
    product = Cart.objects.get(id=cart_id)
    product.status = failed
    product.save()
    get_order = Order.objects.get(id=order_id)
    price_of_products = get_order.order_items.values(
        'price').aggregate(Sum('price'))['price__sum']
    if price_of_products == None:
        get_order.delete()
        context = {'message': 'your have no current orders'}
        return render(request, 'current_order.html', context)
    get_order.order_price = int(price_of_products)
    tax = int(18/100*price_of_products)
    get_order.tax_price = tax + int(price_of_products)
    get_order.save()
    return redirect(Order_details)


@login_required(login_url='/ecommerce/')
def Wish_list_products(request, id):
    if request.method == "POST":
        wish_product = Product.objects.get(id=id)
        obj, add_wish = Wish.objects.get_or_create(user=request.user)
        obj.favourite.add(wish_product)
        obj.save()
    return redirect(Product_list)


@login_required(login_url='/ecommerce/')
def Show_wish(request):

    wished_products = Wish.objects.get(user=request.user)
    context = {'wish_list': wished_products.favourite.all()}
    return render(request, 'wish_list.html', context)


@login_required(login_url='/ecommerce/')
def Remove_wish(request, id):

    if request.method == "POST":
        product_qs = Product.objects.get(id=id)
        wish_qs = Wish.objects.get(user=request.user)
        wish_qs.favourite.remove(product_qs)
    return redirect(Product_list)


def product_api(request):

    products_qs = list(Product.objects.values())
    product_js = json.dumps(products_qs, default=str, indent=6)
    return HttpResponse(product_js, content_type='application/json')


def cart_api(request):

    cart_product = list(Cart.objects.values())
    print(cart_product)
    product_js = json.dumps(cart_product, default=str, indent=6)
    return HttpResponse(product_js, content_type='application/json')


def search_api(request):
    suggetions_qs = []
    if 'need' in request.POST:
        find = request.POST.get('need')
        result = Product.objects.filter(Q(title__icontains=find) | Q(
            name__icontains=find) | Q(brand__icontains=find) & Q(in_stocks=True)).values()
        for i in result:
            suggetions_qs.append(i)
    suggetions = json.dumps(suggetions_qs, default=str, indent=6)
    return HttpResponse(suggetions, content_type='application/json')

def order_api(request):
    orders_qs = Order.objects.all()
    order_js = serializers.serialize('json', orders_qs)
    return JsonResponse(json.loads(order_js), safe=False)


def charge(request):
    get_order = Order.objects.filter(
        Q(user=request.user.id) & Q(order_status=pending)).last()
    orders = Order.objects.create(user=request.user, order_status=pending)
    orders.order_items.add(
        *Cart.objects.filter(Q(user=request.user) & Q(is_active=True)))
    orders.save()
    inactive = Cart.objects.filter(user=request.user)
    inactive.update(is_active=False)
    current_products = get_order.order_items.filter(status=pending).all()
    print(current_products)
    price_of_products = current_products.values(
        'price').aggregate(Sum('price'))['price__sum']
    get_order.order_price = int(price_of_products)
    tax = int(18/100*price_of_products)
    get_order.tax_price = tax + int(price_of_products)
    price = tax + int(price_of_products)
    print(price)
    current_products.update(status=success)
    get_order.save()
    stripe.PaymentIntent.create(amount=int(
        price), currency='inr', payment_method_types=['card'])
    return redirect(Order_details)


def Order_payment(request):
    orders = Order.objects.filter(user=request.user, order_status=pending).last()
    if orders == None:
        return render(request, 'current_order.html', {'message': 'order is empty'})
    get_order = orders.order_items.all()
   
    price_of_product = orders.order_items.aggregate(Sum('price'))['price__sum']
    if price_of_product == None:
        return render(request, 'current_order.html', {'message': 'order is empty'})
    orders.order_price = int(price_of_product)
    tax = int(18/100*price_of_product)
    orders.tax_price = tax + int(price_of_product)
    orders.save()
    price = tax + int(price_of_product)
    
    inactive = Cart.objects.filter(user=request.user)
    inactive.update(is_active=False)
    key = settings.STRIPE_PUBLISHABLE_KEY
    print(key)
    #stripe.PaymentIntent.create(amount=price, currency='usd', payment_method_types=['card'])
    return render(request, 'current_order.html', {'detail': get_order, 'data': orders, 'tax': tax, 'tax_price': tax,  'total': price, 'key': key})


def Payment(request):

    orders = Order.objects.filter(user=request.user, order_status=pending).last()
    products = orders.order_items.all()
    prices = []
    for item in products:
        product = stripe.Product.create(
            name=item.product.name) 
        price = stripe.Price.create(product=product.id, unit_amount=int(item.product.price + int(18/100*item.product.price))*100, currency='inr',)
        prices.append(price.id)
    line_items = []
    for item, price in zip(products, prices):
        line_items.append({'price': price, 'quantity': item.quantity})
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        metadata = {'order ID' : orders.id},
        mode='payment',
        success_url='http://127.0.0.1:8000/ecommerce/Success/',
        cancel_url='http://127.0.0.1:8000/ecommerce/Cancel/'
    )
    Paymets.objects.create(order = orders, transaction_id = session['id'])
    print('***********************************************************************',session)
    
    return redirect(session.url)

def Paymentsucess(request):
    get_order = Order.objects.filter(
        Q(user=request.user.id) & Q(order_status=pending)).last()
    orders = Order.objects.filter(user=request.user, order_status=pending).last()
    orders.order_status = success
    orders.save()
    current_products = get_order.order_items.filter(status=pending).all()
    current_products.update(status=success)
          
    return HttpResponse('Success')

def Paymentcancel(request):
    return HttpResponse('Payment failed')

charges = []
order = []
pay_status = []
@csrf_exempt
def webhook(request):

    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    if event['type'] == 'charge.succeeded':
        session = event['data']['object']['id']
        status = event['data']['object']['outcome']['seller_message']
        charges.append(session)
        #pay_status.append(status)
    
    if event['type'] == 'checkout.session.completed':
        order_id  = event['data']['object']['metadata']['order ID']
        order_status = event['data']['object']['payment_status']
        pay_status.append(order_status)
        order.append(order_id)
        print(order_status)
    if len(pay_status) == 0:
            order_obj = Paymets.objects.last()
            print(order_obj)
            order_obj.payment_satus = 'failed'
            order_obj.save()
    else:
            order_obj = Paymets.objects.last()
            order_obj.payment_satus = 'paid'
            order_obj.save()
            print(pay_status[0])

  
    print(charges)
    print(order)
   # Paymets.objects.create(order = order_obj, transaction_id = str(charges[0]), payment_satus = str(pay_status[0]))
    return HttpResponse('True', status = 200)
    

'''if len(pay_status) == 0:
            order_obj = Order.objects.get(id = int(order[0]))
            print(order_obj)
            order_obj.payment_satus = 'failed'
            order_obj.save()
        else:
            order_obj = Order.objects.get(id = int(order[0])) 
            order_obj.payment_satus = 'paid'
            order_obj.save()
            print(pay_status[0])'''

''' payment_create = Paymets.objects.create(order = order_obj, transaction_id = charges[0])
    #order_obj = Order.objects.get(id = int(order[0]))
    payment_create.payment_satus = pay_status[0]'''