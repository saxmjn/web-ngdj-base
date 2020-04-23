from django.contrib import admin
from . import models

# Register your models here.


class FileAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'type', 'bucket', 'url')


class PhoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'code', 'otp')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')

class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')


admin.site.register(models.File, FileAdmin)
admin.site.register(models.Phone, PhoneAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.City, CityAdmin)
admin.site.register(models.ContactQuery)
admin.site.register(models.NewsletterSubscriber)