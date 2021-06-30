from django.shortcuts import render,redirect
from . models import Contact,Signup,Login,Product,Wishlist,Cart,Transaction
from . models import Reservation
import random
from django.conf import settings 
from django.core.mail import send_mail
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def initiate_payment(request):
    if request.method == "GET":
        return render(request, 'pay.html')
    try:
    	made_by=Signup.objects.get(email=request.session['email'])        
    	amount = int(request.POST['amount'])
        
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=made_by,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def index(request):
	return render(request,'index.html')

def menu(request):
	return render(request,'menu.html')

def gallery(request):
	return render(request,'gallery.html')


def reservation(request):
	if request.method=="POST":
		Reservation.objects.create(
			date=request.POST['date'],
			time=request.POST['time'],
			people=request.POST['people'],
			name=request.POST['name'],
			phone=request.POST['phone'],
			email=request.POST['email'],
			)
		return render(request,'reservation.html')
	else:
		return render(request,'reservation.html')

def blog(request):
	return render(request,'blog.html')

def about(request):
		return render(request,'about.html')


def contact(request):
	if request.method=="POST":
		print("POST")
		Contact.objects.create(
				name=request.POST['name'],
				email=request.POST['email'],
				phone=request.POST['phone'],
				message=request.POST['message']
			)
		return render(request,'contact.html')
	else:
		print("get")
		return render(request,'contact.html')

def signup(request):
	print("Signup Called")
	if request.method=="POST":
		try:
			print("Try Called")
			user=Signup.objects.get(email=request.POST['email'])
			msg="Email Already Registered" 
			return render(request,'signup.html',{'msg':msg})
		except:
			print("Except Called")
			if request.POST['password']==request.POST['cpassword']:
				Signup.objects.create(
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					phone=request.POST['phone'],
					address=request.POST['address'],
					email=request.POST['email'],
					password=request.POST['password'],
					cpassword=request.POST['cpassword'],
					gender=request.POST['gender'],
					image=request.FILES['image'],
					usertype=request.POST['usertype']
				)
				msg="Signup Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Cpassword Does Not Match"
				return render(request,'signup.html',{'msg':msg})
		
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		if request.POST['action']=="Forgot Password":
			return render(request,'forgot_password.html')
		elif request.POST['action']=="Login":
			try:
				user=Signup.objects.get(
						email=request.POST['email'],
						password=request.POST['password']
					)
				print(user.usertype)
				if user.usertype=="user":
					wishlists=Wishlist.objects.filter(user=user)
					carts=Cart.objects.filter(user=user)
					request.session['fname']=user.fname
					request.session['email']=user.email
					request.session['image']=user.image.url
					request.session['wishlist_count'] = len(wishlists)
					request.session['cart_count']=len(carts)
					return render(request,'login_user.html')
				elif user.usertype=="saller":
					request.session['fname']=user.fname
					request.session['email']=user.email
					request.session['image']=user.image.url
					return render(request,'saller_login.html')
			except Exception as e:
				print(e)
				msg="Email or Password is incorrect"
				return render(request,'login.html',{'msg':msg})
		else:		
			pass
	else:
		return render(request,'login.html')
		
def forgot_password(request):
	print("Forgot Password Called")
	if request.method=='POST':
		try:
			print("try called")
			print(request.POST['email'])
			user=Signup.objects.get(email=request.POST['email'])
			if user:
				rec=[request.POST['email'],]
				subject="OTP Forgot Password"
				otp=random.randint(1000,9999)
				message="Your OTP Forgot Password Is "+str(otp)
				email_from=settings.EMAIL_HOST_USER
				send_mail(subject,message,email_from,rec)
				
				return render(request,'otp.html',{'otp':otp,'email':request.POST['email'],})
			else:
				pass
		except Exception as e:
			print("Except Called : ",e)
			msg="Email Does Not Exist"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def validate_otp(request):
	otp1=request.POST['otp1']
	otp2=request.POST['otp2']
	email=request.POST['email']

	user=Signup.objects.get(email=email)

	if otp1==otp2:
		user.status="active"
		user.save()
		msg="User Validated Successfully"
		return render(request,'index.html',{'msg':msg})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'msg':msg,'otp':otp1,'email':email})

def new_password(request):
	if request.method=="POST":
		user=Signup.objects.get(email=request.session['email'])
		if request.POST['npassword']==request.POST['cnpassword']:
			user.password=request.POST['npassword']
			user.cpassword=request.POST['npassword']
			user.save()
			return render(request,'login.html')
		else:
			msg="hello"+user.fname+"New Password & Confirm Password Does not Match"
			return render(request,'new_password.html',{'email':request.POST['email'],'msg':msg})
	else:
		return render(request,'new_password.html')

def login_user(request):
	msg="Welcom"+user.fname+"how are you"
	return render(request,'login_user.html',{'msg':msg})

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['image']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def edit_profile(request):
	user=Signup.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.phone=request.POST['phone']
		user.email=request.POST['email']
		user.address=request.POST['address']
		user.gender=request.POST['gender']
		try:
			user.image=request.FILES['image']
			user.save()
			user=Signup.objects.get(email=request.session['email'])
			msg="Profile Saved Successfully"
			request.session['image']=user.image.url
			return render(request,'edit_profile.html',{'msg':msg})
		except:
			user.save()
			user=Signup.objects.get(email=request.session['email'])
			msg="Profile Saved Successfully"
			request.session['image']=user.image.url
			return render(request,'edit_profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'edit_profile.html',{'user':user})


def saller_login(request):
	return render(request,'saller_login.html')


def saller_edit_profile(request):
	user=Signup.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.phone=request.POST['phone']
		user.email=request.POST['email']
		user.address=request.POST['address']
		user.gender=request.POST['gender']
		try:
			user.image=request.FILES['image']
			user.save()
			user=Signup.objects.get(email=request.session['email'])
			msg="Profile Saved Successfully"
			request.session['image']=user.image.url
			return render(request,'saller_edit_profile.html',{'msg':msg})
		except:
			user.save()
			user=Signup.objects.get(email=request.session['email'])
			msg="Profile Saved Successfully"
			request.session['image']=user.image.url
			return render(request,'saller_edit_profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'saller_edit_profile.html',{'user':user})

def saller_change_password(request):
	#return render(request,'saller_change_password.html')
	if request.method=="POST":
		user=Signup.objects.get(email=request.session['email'])
		if request.POST['npassword']==request.POST['cnpassword']:
			user.password=request.POST['npassword']
			user.cpassword=request.POST['npassword']
			user.save()
			return render(request,'login.html')
		else:
			msg="hello"+user.fname+"New Password & Confirm Password Does not Match"
			return render(request,'saller_change_password.html',{'email':request.POST['email'],'msg':msg})
	else:
		return render(request,'saller_change_password.html')

def saller_add_product(request):
	if request.method=="POST":
		saller=Signup.objects.get(email=request.session['email'])
		Product.objects.create(
				saller=saller,
				product_brand=request.POST['product_brand'],
				product_model=request.POST['product_model'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_image=request.FILES['product_image']
			)
		return render(request,'saller_add_product.html')
	else:
		return render(request,'saller_add_product.html')


def saller_view_product(request):
	saller=Signup.objects.get(email=request.session['email'])
	products=Product.objects.filter(saller=saller)
	return render(request,'saller_view_product.html',{'products':products})

def saller_details_product(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'saller_details_product.html',{'product':product})


def saller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":

		product.product_model=request.POST['product_model']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']

		try:
			product.product_image=request.FILES['product_image']
			product.save()
			return redirect('saller_view_product')

		except:
			product.save()
			return redirect('saller_view_product')

	else:
		return render(request,'saller_edit_product.html',{'product':product})


def saller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('saller_view_product')

def user_view_product(request,pb):
	print(pb)
	if pb=="all":
		products=Product.objects.all()
		return render(request,'user_view_product.html',{'products':products})
	else:
		products=Product.objects.filter(product_brand=pb)
		return render(request,'user_view_product.html',{'products':products})

def user_product_detail(request,pid):
	flag=False
	flag1=False
	user=Signup.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pid)
	try:
		Wishlist.objects.get(user=user,product=product)
		flag=True
	except:
		pass
	try:
		Cart.objects.get(user=user,product=product)
		flag1=True
	except:
		pass
	return render(request,'user_product_detail.html',{'product':product,'flag':flag,'flag1':flag1})

def mywishlist(request):
	
	user=Signup.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'mywishlist.html',{'wishlists':wishlists})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=Signup.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('mywishlist')

def remove_from_wishlist(request,pk):
	user=Signup.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('mywishlist')

def mycart(request):
	net_price=0
	user=Signup.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	for i in carts:
		net_price=net_price+int(i.total_price)
	request.session['cart_count']=len(carts)
	return render(request,'mycart.html',{'carts':carts,'net_price':net_price})


def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=Signup.objects.get(email=request.session['email'])
	Cart.objects.create(
			user=user,
			product=product,
			price=product.product_price,
			total_price=product.product_price
		)
	return redirect('mycart')

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=Signup.objects.get(email=request.session['email'])
	cart=Cart.objects.get(product=product,user=user)
	cart.delete()
	return redirect('mycart')

def change_qty(request):
	cart=Cart.objects.get(pk=request.POST['pk'])
	qty=request.POST['qty']
	cart.qty=qty
	cart.total_price=int(qty)*int(cart.price)
	cart.save()
	return redirect('mycart')