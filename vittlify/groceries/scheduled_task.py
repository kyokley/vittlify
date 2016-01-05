from groceries.models import Shopper, NotifyAction
from groceries.utils import sendMail

def run_emails():
    shoppers = Shopper.objects.all()
    for shopper in shoppers:
        if shopper.email:
            msg = shopper.generateEmail()
            sendMail(shopper.email,
                     'Vittlify Digest',
                     msg)

    actions = NotifyAction.objects.filter(sent=False).all()
    for action in actions:
        action.sent = True
