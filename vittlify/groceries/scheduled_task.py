from groceries.models import (Shopper,
                              NotifyAction,
                              WebSocketToken,
                              )
from groceries.utils import sendMail
from django_cron import CronJobBase, Schedule
from datetime import datetime

CRON_DAILY_FREQUENCY = 1440
CRON_WEEKLY_FREQUENCY = 10080

def run_daily_emails():
    shoppers = Shopper.objects.all()
    for shopper in shoppers:
        if shopper.email and shopper.receive_daily_email():
            msg = shopper.generateEmail()
            if msg:
                sendMail(shopper.email,
                         'Vittlify Digest',
                         msg)

    actions = NotifyAction.objects.filter(sent=False).all()
    for action in actions:
        action.sent = True
        action.save()

def run_weekly_emails():
    shoppers = Shopper.objects.all()
    for shopper in shoppers:
        if shopper.email and shopper.receive_weekly_email():
            msg = shopper.generateEmail()
            if msg:
                sendMail(shopper.email,
                         'Vittlify Weekly Digest',
                         msg)

    actions = NotifyAction.objects.filter(weekly_sent=False).all()
    for action in actions:
        action.weekly_sent = True
        action.save()

def test_email(addr):
    sendMail(addr,
             'Vittlify Test at %s' % datetime.now(),
             'This is a test email from vittlify.')

class EmailJob(CronJobBase):
    schedule = Schedule(run_every_mins=CRON_DAILY_FREQUENCY)
    code = 'groceries.email_job'

    def do(self):
        run_daily_emails()

class EmailWeeklyJob(CronJobBase):
    schedule = Schedule(run_every_mins=CRON_WEEKLY_FREQUENCY)
    code = 'groceries.email_weekly_job'

    def do(self):
        run_weekly_emails()

class CleanUpTokensJob(CronJobBase):
    schedule = Schedule(run_every_mins=CRON_DAILY_FREQUENCY)
    code = 'groceries.cleanup_tokens_job'

    def do(self):
        WebSocketToken.objects.filter(active=False).delete()
