from django.contrib import admin
from . import models


# Register your models here.


class UserContactAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'contact', 'first_name', 'last_name', 'phone', 'email', 'created')
    readonly_fields = (
    'user', 'contact', 'source', 'first_name', 'last_name', 'email', 'phone', 'state', 'registered', 'invited_at',
    'created')

    def phone(self, obj):
        return obj.get_phone()


admin.site.register(models.UserContact, UserContactAdmin)
