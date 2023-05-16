from django.contrib import admin
from Message.models import *
# Register your models here.
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Complain)