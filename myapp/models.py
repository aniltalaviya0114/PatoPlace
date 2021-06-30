from django.db import models
from django.utils import timezone
# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	phone=models.CharField(max_length=100)
	message=models.TextField()

	def __str__(self):
		return self.name

class Reservation(models.Model):
	date=models.CharField(max_length=100)
	time=models.CharField(max_length=100)
	people=models.CharField(max_length=100)
	name=models.CharField(max_length=100)
	phone=models.CharField(max_length=100)
	email=models.CharField(max_length=100)

	def __str__(self):
		return self.name 

class Signup(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	phone=models.CharField(max_length=100)
	address=models.TextField()
	email=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	gender=models.CharField(max_length=100)
	status=models.CharField(max_length=100,default="inactive")
	usertype=models.CharField(max_length=100,default="user")
	image=models.ImageField(upload_to="image/",blank=True,null=True,default="")

class Login(models.Model):
	email=models.CharField(max_length=100)
	password=models.CharField(max_length=100)


class Product(models.Model):

	BRANDS=(

			('Apple','Apple'),
			('Samsung','Samsung'),
			('Mi','Mi'),
			('OnePlush','OnePlush'),
		)
	saller=models.ForeignKey(Signup,on_delete=models.CASCADE)
	product_brand=models.CharField(max_length=100,choices=BRANDS)
	product_model=models.CharField(max_length=100)
	product_price=models.IntegerField()
	product_desc=models.TextField()
	product_image=models.ImageField(upload_to="product_image")


	def __str__(self):
		return self.saller.fname+" - "+self.product_model

class Wishlist(models.Model):
	user=models.ForeignKey(Signup,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+ self.product.product_brand


class Cart(models.Model):
	user=models.ForeignKey(Signup,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	qty=models.IntegerField(default=1)
	price=models.IntegerField()
	total_price=models.IntegerField()

	def __str__(self):
		return self.user.fname+" - "+self.product.product_brand

class Transaction(models.Model):
	made_by = models.ForeignKey(Signup, related_name='transactions', on_delete=models.CASCADE)
	made_on = models.DateTimeField(auto_now_add=True)
	amount = models.IntegerField()
	order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
	checksum = models.CharField(max_length=100, null=True, blank=True)

	def save(self, *args, **kwargs):
		if self.order_id is None and self.made_on and self.id:
			self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
		return super().save(*args, **kwargs)

		"time : 10:10"