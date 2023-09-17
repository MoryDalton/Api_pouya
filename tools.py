from random import randint

from django.utils.timezone import now, timedelta
from django.http import HttpRequest

from users.models import Sms
import keys

from kavenegar import KavenegarAPI


def response_OK(detail):
    return {"isStatus": True, "detail": detail}


def response_ERROR(detail):
    if type(detail) != list:
        return {"isStatus": False, "detail": [detail]}
    return {"isStatus": False, "detail": detail}


# check sms before send:
def check_before_send(phone: str) -> bool:

    # if user exsist check for expire time:
    try:
        user = Sms.objects.get(phone=phone)
        if now() < (user.created_date+timedelta(minutes=2)):
            return False

        # time expired:-> delete code an send sms:
        user.delete()
        return True

    # user not exsist:-> send sms
    except:
        return True


# check user code:
def check_code(phone, code):

    # if phone and code exsist and code is correct:
    try:
        # if expire time is ok:
        user = Sms.objects.get(phone=phone, code=code)
        if now() < (user.created_date+timedelta(minutes=2)):
            result = (True, "ok")

        # if time expired:
        else:
            result = (False, "time expired")

        # delete object from db
        user.delete()

    # if phone not found or code is not correct:
    except:
        result = (False, "code invalid")

    return result


# send sms to user
def send_message(phone: str):

    code = str(randint(1000, 9999))
    Sms.objects.create(phone=phone, code=code)

    # send sms to phone here:
    api = KavenegarAPI(keys.SMS_API)
    params = {
        'receptor': phone,
        'template': 'verify',
        'token': code,
        'type': 'sms'
    }
    api.verify_lookup(params)


# pagination
def paginator_next_previous_page(request, paginator, page):
    next = ''
    previous = ''
    all_pages = paginator.num_pages
    count = paginator.count
    if 1 <= page < all_pages:
        next = HttpRequest.build_absolute_uri(request, f'?page={page+1}')
    if 1 < page <= all_pages:
        previous = HttpRequest.build_absolute_uri(request, f'?page={page-1}')

    return (count, all_pages, next, previous)
