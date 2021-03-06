from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Product
from math import ceil
import itertools
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib.auth import login as auth_login
from .models import Order
from .models import Contact
import cv2
import mediapipe as mp
import razorpay
from django.core.mail import send_mail
from django.conf import settings


def index2(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        allProds.append([prod, cats])
    params = {'allProds': allProds}
    return render(request, 'index2.html', params)


def index1(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        allProds.append([prod, cats])
    params = {'allProds': allProds}
    return render(request, 'index1.html', params)


def about(request):
    return render(request, 'about.html')

def about1(request):
    return render(request, 'about1.html')


def contact(request):
    if request.method == 'POST':
        username = request.user
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        contact = Contact(user = username,name=name,email=email,phone=phone,message=message)
        contact.save()
        messages.success(request, "Your message has been sent successfully!!!")
    return render(request, 'contact.html')

def contact1(request):
    if request.method == 'POST':
        username = request.user
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        contact = Contact(user = username,name=name,email=email,phone=phone,message=message)
        contact.save()
        messages.success(request, "Your message has been sent successfully!!!")
    return render(request, 'contact1.html')


def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search1(request):
    query = request.GET.get('search1')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        if len(prod) != 0:
            allProds.append([prod, cats])
    params = {'allProds': allProds}
    if len(allProds) == 0 or len(query) < 4:
        messages.error(
            request, "Please make sure to enter relevant search query.")
        return redirect('Home1')
    return render(request, 'search1.html', params)


def search2(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    query = request.GET.get('search2')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        if len(prod) != 0:
            allProds.append([prod, cats])
    params = {'allProds': allProds}
    if len(allProds) == 0 or len(query) < 4:
        messages.error(
            request, "Please make sure to enter relevant search query.")
        return redirect('Home2')
    return render(request, 'search2.html', params)


def tracker(request):
    return render(request, 'tracker.html')


def productview(request, myid, mycategory):
    products = Product.objects.filter(id=myid)
    similar_products = Product.objects.filter(
        category=mycategory).exclude(id=myid)
    return render(request, 'productview.html', {'product': products[0], 'related': similar_products})


def productview1(request, myid, mycategory):
    products = Product.objects.filter(id=myid)
    similar_products = Product.objects.filter(
        category=mycategory).exclude(id=myid)
    return render(request, 'productview1.html', {'product': products[0], 'related': similar_products})


def checkout(request):
    ids=request.session.get('cart').keys()
    products=Product.getproductsbyid(ids)
    return render(request, 'checkout.html', {'products': products})

def order(request):
    if request.method == 'POST':
        username = request.user
        name = request.POST['name']
        email = request.POST['email']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        phone = request.POST['phone']
        cart = request.session.get('cart')
        products = Product.getproductsbyid(list(cart.keys()))
        pay = []
        total = []
        for product in products:
            pay.append(((product.price)*(cart.get(str(product.id)))) * 100)
            total.append(((product.price)*(cart.get(str(product.id)))))
            order = Order(user=username, name=name, email=email, address=address, city=city, state=state, pincode=pincode,phone=phone, product=product, price=product.price, quantity=cart.get(str(product.id)),totalPrice =((product.price)*(cart.get(str(product.id)))))
            order.save()
        client = razorpay.Client(auth=("rzp_test_JaZ7Hbjm5CP78f", "m3hI5KDOJIdiaJYOluqpGQZe"))
        payment = client.order.create({'amount':int(sum(pay)+8000),'currency':'INR','payment_capture':'1'})
        return render(request, 'payment.html',{'payment':payment,'name':name,'email':email,'phone':phone,'address':address,'city':city,'state':state,'pincode':pincode,'total':(sum(total))})

@csrf_exempt
def success(request):
    a = request.POST
    # print(a)
    order_id = ''
    payment_id = ''
    for key , val in a.items():
        if key == 'razorpay_order_id':
            order_id = val
        if key == 'razorpay_payment_id':
            payment_id = val
    user = request.user
    sub = 'Your Payment has been Received'
    message = 'Hi '+(str(user))+',\n\nYour Order '' has been Received.\nOrder id : '+(str(order_id))+'\nPayemnt id : '+(str(payment_id))+'\n\nThank You For Ordering!!!'
    email = 'wearit482@gmail.com'
    send_mail(sub, message,email,[user.email])
    request.session['cart'] = {}
    messages.success(request, "Your order has been placed successfully!!!")
    return redirect('Home2')

def cart(request):
    ids=request.session.get('cart').keys()
    products=Product.getproductsbyid(ids)
    return render(request, 'cart1.html', {'l': products})

def emptycart(request):
    request.session['cart'] = {}
    return redirect('Cart')


def addtocart(request):
    if request.method == 'POST':
        product=request.POST.get('product')
        remove=request.POST.get('remove')
        cart=request.session.get('cart')
        if cart:
            quantity=cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        del cart[product]
                        request.session['cart']=cart

                    else:
                        cart[product]=quantity - 1
                else:
                    cart[product]=quantity + 1
            else:
                cart[product]=1
            request.session['cart']=cart
        else:
            cart={}
            cart[product]=1
            request.session['cart']=cart
        return redirect('Cart')


def signup(request):
    if request.method == "POST":
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        # Checks for signup
        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters")
            return redirect('Home1')
        if not username.isalnum():
            messages.error(
                request, "Username should only contain letters and numbers")
            return redirect('Home1')
        if pass1 != pass2:
            messages.error(request, "Password do not match")
            return redirect('Home1')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('Home1')
        # create user
        myuser=User.objects.create_user(username, email, pass1)
        myuser.save()
        messages.success(
            request, "Your account has been created successfully!!!")
        return redirect('Home1')

    else:
        return HttpResponse('404 - Page not found')


def login(request):
    if request.method == "POST":
        loginusername=request.POST['loginusername']
        loginpassword=request.POST['loginpassword']
        user=authenticate(username=loginusername, password=loginpassword)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Successfully Logged in!!!")
            return redirect('Home2')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect('Home1')
    else:
        return HttpResponse('404 - Page not found')


def logout(request):
    auth_logout(request)
    messages.success(request, "Successfully Logged Out!!!")
    return redirect('Home1')

def prodar(request,myid,mycategory):
    products = Product.objects.filter(id=myid)
    similar_products = Product.objects.filter(
        category=mycategory).exclude(id=myid)
    return render(request, 'productviewar.html', {'product': products[0], 'related': similar_products})

def prodar1(request,myid,mycategory):
    products = Product.objects.filter(id=myid)
    similar_products = Product.objects.filter(
        category=mycategory).exclude(id=myid)
    return render(request, 'productviewar1.html', {'product': products[0], 'related': similar_products})

def gen():
    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
    while True:
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while camera.isOpened():
                success, frame = camera.read()  # read the camera frame
                if not success:
                    break
                else:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Make Detections
                    results = holistic.process(image)
                    # print(results.face_landmarks)

                    # face_landmarks, pose_landmarks, left_hand_landmarks, right_hand_landmarks

                    # Recolor image back to BGR for rendering
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    # 1. Draw face landmarks
                    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                                            mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                                            mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                                            )

                    # 2. Right hand
                    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                            mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                                            mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
                                            )

                    # 3. Left Hand
                    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                            mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                                            )

                    # 4. Pose Detections
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                            mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                            )
                    ret, buffer = cv2.imencode('.jpg', image)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen(),content_type= 'multipart/x-mixed-replace; boundary=frame')