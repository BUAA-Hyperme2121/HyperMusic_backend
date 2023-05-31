from django.contrib import admin
from Message.models import *
# Register your models here.
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Complain)
admin.site.register(VerifyCode)
admin.site.register(Post)
admin.site.register(JobToMusic)
admin.site.register(Reply)
admin.site.register(Likes)
admin.site.register(UserToMessage)
admin.site.register(UserToComment)
admin.site.register(UserToComplain)
admin.site.register(MusicToComment)
admin.site.register(MusicToComplain)
admin.site.register(MusicListToComment)
admin.site.register(MusicListToComplain)
admin.site.register(PostToComment)






