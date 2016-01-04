from groceries.models import Shopper
from groceries.utils import sendMail

def run_emails():
    shoppers = Shopper.objects.all()
    for shopper in shoppers:
        if shopper.email:
            msg = shopper.generateEmail()
            sendMail(shopper.email,
                     'Vittlify Digest',
                     msg)
