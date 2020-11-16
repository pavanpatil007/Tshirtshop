from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from shop.models import Customer, Tshirt, SizeVariant, Cart

from shop.forms.authform import CustomerCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as loginuser, logout
from shop.models import Tshirt, SizeVariant, OrderItem, Order, Color, Payment, Occasion, Brand, Sleeve, NeckType, IdealFor
from math import floor
from shop.templatetags.tshirt_tags import min_price, sale_price
from shop.forms.checkout_form import CheckForm
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView

from django.core.paginator import Paginator
from urllib.parse import urlencode

from django.views.generic.base import View

from .forms.authform import CustomerAuthForm



from django.shortcuts import render, HttpResponse, redirect
from django.shortcuts import render, HttpResponse, redirect

from instamojo_wrapper import Instamojo
API_KEY="test_8ae61cb145b7edb37b01806374c"
AUTH_TOKEN="test_0a1a23705c1024395442cad8c43"
API = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')


# Create your views here.
class LoginView(View):  
    def get(self , request):
        form = CustomerAuthForm()
        print('LOGIN VIEW CLASS')
        next_page = request.GET.get('next')
        if next_page is not None:
            request.session['next_page'] = next_page
        return render(request,
                      template_name='login.html',
                      context={'form': form})

    def post(self , request):
        add = request.session.get('plusItem')
        form = CustomerAuthForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                loginuser(request, user)

                session_cart = request.session.get('cart')
                if session_cart is None:
                    session_cart = []
                else:
                    for c in session_cart:
                        size = c.get('size')
                        tshirt_id = c.get('tshirt')
            
                        quantity = c.get('quantity')+1
                        cart_obj = Cart()
                        cart_obj.sizeVariant = SizeVariant.objects.get(
                            size=size, tshirt=tshirt_id)
                        cart_obj.quantity = quantity
                        cart_obj.user = user
                        cart_obj.save()

                # { size , tshirt , quantiti }
                cart = Cart.objects.filter(user=user)
                session_cart = []
                for c in cart:
                    obj = {
                        'size': c.sizeVariant.size,
                        'tshirt': c.sizeVariant.tshirt.id,
                        'quantity': c.quantity
                    }
                    session_cart.append(obj)

                request.session['cart'] = session_cart
                next_page = request.session.get('next_page')
                if next_page is None:
                    next_page = 'homepage'
                return redirect(next_page)
        else:
            return render(request,
                          template_name='login.html',
                          context={'form': form})


def add_cart_to_database(user, size, tshirt):
    size = SizeVariant.objects.get(size=size, tshirt=tshirt)
    existing = Cart.objects.filter(user=user, sizeVariant=size)

    if len(existing) > 0:
        obj = existing[0]
        obj.quantity = obj.quantity + 1
        obj.save()

    else:
        c = Cart()
        c.user = user
        c.sizeVariant = size
        c.quantity = 1
        c.save()

def add_cart_for_anom_user(cart, size, tshirt):
    flag = True
    for cart_obj in cart:
        t_id = cart_obj.get('tshirt')
        size_short = cart_obj.get('size')
        if t_id == tshirt.id and size == size_short:
            flag = False
            cart_obj['quantity'] = cart_obj['quantity'] + 1

    if flag:
        cart_obj = {'tshirt': tshirt.id, 'size': size, 'quantity': 1}
        cart.append(cart_obj)

def add_to_cart(request,slug,size):
    add = request.session.get('plusItem')
    user = None
    if request.user.is_authenticated:
        user = request.user

    cart = request.session.get('cart')
   
    if cart is None:
        cart=[]

    tshirt = Tshirt.objects.get(slug=slug) 
    request.session['cart']= cart
    

    add_cart_for_anom_user(cart, size, tshirt)
        
    if user is not None:
        add_cart_to_database(user, size, tshirt)
       
        
    request.session['cart']= cart 
    return_url = request.GET.get('return_url')
    return redirect (return_url)

def show_product(request, slug):
    tshirt = Tshirt.objects.get(slug=slug)
    size = request.GET.get('size')
    active_size = size

    if size is None:
        size = tshirt.sizevariant_set.all().order_by('price').first()
    
    size = tshirt.sizevariant_set.get(size=size)  
    size_price = floor(size.price)
    sell_price = size_price - (size_price * (tshirt.discount/100))
    sell_price = floor(sell_price)

    context = {
        'tshirt': tshirt,
        'price': sell_price,
        'size_price': size_price,
        'active_size': size
        
        
        

    }

    print(size)
    return render(request, template_name='product_details.html', context=context)


def index(request):
    query = request.GET
    tshirts = []
    tshirts = Tshirt.objects.all()

    brand = query.get('brand')
    neckType = query.get('necktype')
    color = query.get('color')
    idealFor = query.get('idealfor')
    sleeve = query.get('sleeve')
    page = query.get('page')


    if(page is None or page == ''):
        page = 1

    if brand != '' and brand is not None:
        tshirts = tshirts.filter(brand__slug=brand)
    if neckType != '' and neckType is not None:
        tshirts = tshirts.filter(neck_type__slug=neckType)
    if color != '' and color is not None:
        tshirts = tshirts.filter(color__slug=color)
    if sleeve != '' and sleeve is not None:
        tshirts = tshirts.filter(sleeve__slug=sleeve)
    if idealFor != '' and idealFor is not None:
        tshirts = tshirts.filter(ideal_for__slug=idealFor)

    occasion = Occasion.objects.all()
    brands =  Brand.objects.all()
    idealFor =  IdealFor.objects.all()
    sleeves =  Sleeve.objects.all()
    neckType =  NeckType.objects.all()
    colors =  Color.objects.all()

    cart = request.session.get('cart')

    paginator = Paginator(tshirts, 3)
    page_object = paginator.get_page(page)

    query = request.GET.copy()
    query['page'] = ''
    pageurl = urlencode(query)
    

    context = {
        'page_object': page_object,
        'occasions': occasion,
        'brands': brands,
        'idealFor': idealFor,
        'sleeves': sleeves,
        'neckType': neckType,
        'colors': colors,
        'pageurl' : pageurl

    }
    return render(request, 'index.html', context=context)


def cart(request):
    cart = request.session.get('cart')
    add = request.session.get('plusItem')
    if cart is None:
        cart = []
    for c in cart:
        tshirt_id = c.get('tshirt')
        tshirt = Tshirt.objects.get(id=tshirt_id)
        c['size'] = SizeVariant.objects.get(tshirt= tshirt_id , size= c['size'])
        c['tshirt']= tshirt
    print(cart)
    return render(request, 'cart.html', context={'cart': cart})

@login_required(login_url='/login/')
def orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-date').exclude(order_status='PENDING')
    context = {
        'orders' : orders
    }
    return render(request, 'orders.html', context=context)


def signup(request):
    if (request.method is 'GET'):
        form = CustomerCreationForm()

        context = {
            "form": form
        }
        return render(request, 'signup.html', context=context)

    else:
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = user.username
            user.save()
            print(user)
            return redirect('login')

            context = {
                "form": form
            }

        context = {
            "form": form
        }
        return render(request, 'signup.html', context=context)


def signout(request):
    logout(request)
    return redirect('homepage')

def cal_total_payable_amount(cart):
    total = 0
    for c in cart:
        discount =c.get('tshirt').discount
        price = c.get('size').price
        sale_price = floor(price-(price * (discount/100)))
        total_of_single_product = sale_price * c.get('quantity')
        total = total + total_of_single_product
        
    return total

@login_required(login_url='/login/')
def checkout(request):
    if request.method == 'GET':
        form = CheckForm()
        cart = request.session.get('cart')
        if cart is None:
            cart = []

        for c in cart:
            size_str = c.get('size')
            tshirt_id = c.get('tshirt')
            size_obj = SizeVariant.objects.get(size=size_str, tshirt=tshirt_id)
            c['size'] = size_obj
            c['tshirt'] = size_obj.tshirt

        print(cart)

        return render(request, 'checkout.html', {
            "form": form,
            'cart': cart
        })
    else:
        # post request
        form = CheckForm(request.POST)
        user = None
        if request.user.is_authenticated:
            user = request.user
        if form.is_valid():
            # payment
            cart = request.session.get('cart')
            if cart is None:
                cart = []
            for c in cart:
                size_str = c.get('size')
                tshirt_id = c.get('tshirt')
                size_obj = SizeVariant.objects.get(size=size_str,
                                                   tshirt=tshirt_id)
                c['size'] = size_obj
                c['tshirt'] = size_obj.tshirt
            shipping_address = form.cleaned_data.get('shipping_address')
            phone = form.cleaned_data.get('phone')
            payment_method = form.cleaned_data.get('payment_method')
            total = cal_total_payable_amount(cart)
            print(shipping_address, phone, payment_method, total)

            order = Order()
            order.shipping_address = shipping_address
            order.phone = phone
            order.payment_method = payment_method
            order.total = total
            order.order_status = "PENDING"
            order.user = user
            order.save()

            # saving order items
            for c in cart:
                order_item = OrderItem()
                order_item.order = order
                size = c.get('size')
                tshirt = c.get('tshirt')
                order_item.price = floor(size.price -
                                         (size.price *
                                          (tshirt.discount / 100)))
                order_item.quantity = c.get('quantity')
                order_item.size = size
                order_item.tshirt = tshirt
                order_item.save()

            buyer_name = f'{user.first_name} {user.last_name}'
            print(buyer_name)
            # crating payment
            
            response = API.payment_request_create(
            amount=order.total,
            purpose="Payment For Tshirts",
            send_email=True,
            buyer_name=f'{user.first_name} {user.last_name}',
            email=user.email,
            redirect_url="http://localhost:8000/validate_payment"
            )

            payment_request_id = response ['payment_request']['id']
            url = response['payment_request']['longurl']

            payment = Payment()
            payment.order = order
            payment.payment_request_id= payment_request_id
            payment.save()
            return redirect(url)

        else:
            return redirect('/checkout/')

def validatePayment(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
    print(user)
    payment_request_id = request.GET.get('payment_request_id')
    payment_id = request.GET.get('payment_id')
    print(payment_request_id, payment_id)
    response = API.payment_request_payment_status(payment_request_id,
                                                  payment_id)
    status = response.get('payment_request').get('payment').get('status')

    if status is not "Failed":
        print('Payment Success')
        try:
            payment = Payment.objects.get(payment_request_id=payment_request_id)
            payment.payment_id = payment_id
            payment.payment_status = status
            payment.save()

            order = payment.order
            order.order_status = 'PLACED'
            order.save()

            cart = []
            request.session['cart'] = cart
            Cart.objects.filter(user=user).delete()

            return redirect('orders')
        except:
            return render(request, 'payment_failed.html')
            
    else:
        return render(request, 'payment_failed.html')

def clear_cart(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
    print(user)
    cart = []
    request.session['cart'] = cart
    Cart.objects.filter(user=user).delete()
    return redirect('homepage')

class OrderListView(ListView):
    template_name = 'orders.html'
    model = Order
    paginate_by = 5
    context_object_name = 'orders'

    def get_queryset(self):
        return  Order.objects.filter(user = self.request.user).order_by('-date').exclude(
        order_status='PENDING')
        # // return error page