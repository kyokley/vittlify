from groceries.models import Shopper, NotifyAction
from groceries.utils import sendMail
from django_cron import CronJobBase, Schedule

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

class EmailJob(CronJobBase):
    pass
