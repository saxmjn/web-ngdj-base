# django-base
This project is not an Introduction to Django. To get the most out of it, you should be familiar with Django.
This project comprises of following microservices/micro-features built on top of Django Framework

1. JWT Authentication with Phone, Email, Google, Facebook
2. Celery and Redis based contacts upload
3. Real Time Chat
4. Notification feed
5. Elastic Search based text and tag search engine

## JWT AUTH
JWT stand for JSON Web Token and it is an authentication strategy used by client/server applications where the client is a Web application using JavaScript or mobile platforms like Android or iOS.

In this app we are going to explore the specifics of JWT authentication and how we have integrated the same withing Django to use either of Phone, Email, Google or Facebook auth.

A JWT Token looks something like this xxxxx.yyyyy.zzzzz, those are three distinctive parts that compose a JWT:
```
header.payload.signature
```

#### Libraries Used:
1. djangorestframework==3.9.4
2. djangorestframework-jwt==1.11.0
3. PyJWT==1.7.1


#### Features:
1. User Signup/Signin with Email
2. User Signup/Signin with Phone
3. Forgot Password
4. Change Password
5. Update Email
6. Update Phone

## CONTACTS AND INVITE BUILT WITH CELERY

#### Libraries used:
1. celery==4.2.2
2. redis==3.3.4

#### Features:
1. Upload Contacts from Phone
2. Invite Contacts
3. Invitee join's from your invite