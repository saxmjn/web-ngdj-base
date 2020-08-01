import requests
import json
from . import models
from app import utils

def get_otp(email=None, phone=None):
    data = {'email_otp': None, 'phone_otp': None}
    if email:
        data['email_otp'] = models.Email.create(email=email, send_otp=True).otp
    if phone:
        data['phone_otp'] = models.Phone.create(phone=phone, send_otp=True).otp
    
    return data


def msg91_phone_otp_verification(phone, OTP, email=None):
    import http.client
    conn = http.client.HTTPConnection("control.msg91.com")
    payload = ''
    authkey = '264748AlvMnDweoe6v5c73d868'
    message = 'Your GoMama verification code is {}.'.format(OTP)

    route = '/api/sendotp.php?otp_length=4&authkey={}&message={}&sender=GoMama&mobile={}&otp={}'.format(authkey,
                                                                                                             message,
                                                                                                             phone, OTP)
    if email is not None:
        route = route + '&email={}'.format(email)

    # method 1
    # conn.request("POST", route, payload)
    # res = conn.getresponse()
    # data = res.read()
    # return data.decode("utf-8")

    # method 2
    headers = {"authkey": authkey, 'Content-type': 'application/json'}
    ret = requests.post('http://control.msg91.com' + route, data=json.dumps({}), headers=headers)
    return ret