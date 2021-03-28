from django.contrib import admin
from .models import User, Item, Watchlist, Bid, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Item)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)

#admin panel login details:
#login: admin
#password: adminadmin