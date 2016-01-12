from groceries.models import Shopper, NotifyAction
from groceries.utils import sendMail
from django_cron import CronJobBase, Schedule
from config.settings import CRON_JOB_FREQUENCY
from datetime import datetime

def run_emails():
    shoppers = Shopper.objects.all()
    for shopper in shoppers:
        if shopper.email:
            msg = shopper.generateEmail()
            if msg:
                sendMail(shopper.email,
                         'Vittlify Digest',
                         msg)

    actions = NotifyAction.objects.filter(sent=False).all()
    for action in actions:
        action.sent = True
        action.save()

def test_email(addr):
    sendMail(addr,
             'Vittlify Test at %s' % datetime.now(),
             'This is a test email from vittlify.')

class EmailJob(CronJobBase):
    schedule = Schedule(run_every_mins=CRON_JOB_FREQUENCY)
    code = 'groceries.email_job'

    def do(self):
        run_emails()
