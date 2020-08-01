# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
# Project
from . import models


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'name', 'city', 'user_link', 'email', 'phone', 'created', 'last_opened_at')
    search_fields = ['user__username']
    raw_id_fields = ['user', 'category', 'categories', 'city']
    readonly_fields = ['modified', 'created', 'device_token', 'read_notification_count',
                       'phone_number', 'phone_code', 'phone_otp', 'phone_verified', 'category', 'categories', 'city',
                       'inviter', 'birth', 'sex', 'language', 'heading', 'summary', 'last_opened_at',]
    exclude = ('signup_stage', 'signup_done', 'location', 'profile_pic_url')

    def name(self, obj):
        return obj.get_name()

    def email(self, obj):
        return obj.get_email()

    def phone(self, obj):
        return obj.get_phone()

    def city(self, obj):
        return obj.city.name

    def user_link(self, obj):
        url = 'http://cmn-django.herokuapp.com/admin/auth/user/{}/change/'.format(obj.user.pk)
        return '<a href="%s" target="_blank">%s</a>' % (url, obj.user.pk)


    user_link.allow_tags = True
    user_link.short_description = 'User Link'


admin.site.register(models.UserProfile, UserProfileAdmin)