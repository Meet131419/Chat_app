from django.contrib import admin
from user.models import Login,Register,ChatGroup,GroupMessage
# Register your models here.

admin.site.register(Login)
admin.site.register(Register)
admin.site.register(ChatGroup)
admin.site.register(GroupMessage)
