from django.contrib import admin
from . models import Contact
from . models import Reservation,Signup,Login,Product,Wishlist,Cart,Transaction

from django.contrib.admin.models import LogEntry
LogEntry.objects.all().delete()


# Register your models here.
class AdminReservation(admin.ModelAdmin):
	list_display=('date','time','people','name','phone','email')

class AdminContact(admin.ModelAdmin):
	list_display=('name','email','phone','message')

class AdminSignup(admin.ModelAdmin):
	list_display=('fname','lname','phone','address','email','password','cpassword','gender')

class AdminLogin(admin.ModelAdmin):
	list_display=('email','password')

admin.site.register(Contact,AdminContact)

admin.site.register(Reservation,AdminReservation)

admin.site.register(Signup,AdminSignup)

admin.site.register(Login,AdminLogin)

admin.site.site_header="Pato-Place"

admin.site.register(Product)

admin.site.register(Wishlist)

admin.site.register(Cart)

admin.site.register(Transaction)