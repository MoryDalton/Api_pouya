from random import randint

from django.utils.timezone import now, timedelta

from smtplib import SMTP_SSL
from email.message import EmailMessage

from users.models import EmailVerify


# check email before send:
def check_before_send(email: str) -> bool:

    # if user exsist check for expire time:
    try:
        email = EmailVerify.objects.get(email=email)
        if now() < (email.created_date+timedelta(minutes=2)):
            return False

        # time expired:-> delete code an send sms:
        email.delete()
        return True

    # user not exsist:-> send sms
    except:
        return True


# check user code:
def check_code(email, code):

    # if email and code exsist and code is correct:
    try:
        # if expire time is ok:
        obj = EmailVerify.objects.get(email=email, code=code)
        if now() < (obj.created_date+timedelta(minutes=2)):
            result = (True, "ok")

        # if time expired:
        else:
            result = (False, "expire time")

        # delete object from db
        obj.delete()

    # if email not found or code is not correct:
    except:
        result = (False, "code not valid")

    return result


# send email to user
def send_email(email: str):

    # random code
    code = randint(1000, 9999)

    # save code in DB
    EmailVerify.objects.create(email=email, code=code)

    text = f"""\
<html>
  <head></head>
  <body>
    <p>
        <h1 dir="rtl" align="right">سلام این پیام آزمایشی است.</h1>
    </p>
    <p>
        <h3 dir="rtl" align="right">کد تایید شما برای تغییر رمز عبور :</h3>
    </p>
    <p>
        <h2 dir="rtl" align="right">{code}</h2>
    </p>
    <p>
        <h3 dir="rtl" align="right">این کد را در اختیار هیچکس قرار ندهید.</h3>
    </p>
  </body>
</html>
"""

    # setup vairables:
    HOST = "smtp.gmail.com"
    PORT = 465
    ME = "daltonmory@gmail.com"
    PASSWORD = "lxfdjhdlfqqmpuds"

    msg = EmailMessage()
    msg["SUBJECT"] = "پیام آزمایشی از پایتون"
    msg["FROM"] = ME
    msg["TO"] = email
    msg.set_content(text, subtype='html')

    with SMTP_SSL(host=HOST, port=PORT) as connection:
        connection.login(user=ME, password=PASSWORD)
        connection.send_message(msg=msg)
        connection.quit()
        del msg["TO"]
