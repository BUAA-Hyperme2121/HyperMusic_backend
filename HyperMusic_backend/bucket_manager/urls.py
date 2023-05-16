from django.urls import path,include
from bucket_manager.views import *

urlpatterns = [
    path('callback/', callback),

]