from random import randint

from django.utils.timezone import now, timedelta

from users.models import Sms
import keys

from kavenegar import KavenegarAPI, APIException, HTTPException


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
