#!/usr/bin/env python
import time
import smtplib
import boto.route53

from datetime import date


class Cerbero:
    conn = None
    days_limit = 45
    hosted_domains = []

    def __init__(self, days_limit=45):
        self.conn = boto.route53.connect_to_region('us-west-2')
        self.days_limit = days_limit

    def set_hosted_domains(self):
        hosted_zones = self.conn.get_all_hosted_zones()
        self.hosted_domains = []
        for domain in hosted_zones['ListHostedZonesResponse']['HostedZones']:
            self.hosted_domains.append(
                {
                    'domain': domain['Name'],
                    'comment':domain['Config']['Comment']
                }
            )
  
    def get_hosted_domains(self):
        self.set_hosted_domains()
        return self.hosted_domains

    def send_email(self, email_subject, email_message):
        try:
            fromaddr = 'user@example.com'
            toaddrs  = ['destinatary1@example.com', 'destinatary2@example.com', 'destinatary3@example.com']
            #toaddrs  = ['ricardo@evolutiva.mx']
            subject = "Subject: " + email_subject
            msg = "\r\n".join([ "From: user@example.com", "To: " + ", ".join(toaddrs), subject, "", email_message ])
            username = 'user@example.com'
            password = 'PASSWD'
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(username,password)
            server.sendmail(fromaddr, toaddrs, msg)
            server.quit()

        except Exception:
            print("No se pudo enviar el email")


    def send_expire_notification(self, domain, provider, days_remain):
        subject = "Vencimiento de dominio: {0} en {1} dias".format(domain, days_remain)
        message = "El dominio: '{0}' con el provedor: '{1}' expira en {2} dias\n".format(domain, provider, days_remain)
        self.send_email(subject, message)

    def get_days_to_expire(self, domain_date):
        today = date.today()
        expire_ds = time.strptime(domain_date, "%Y-%m-%d")
        expire_date = date(expire_ds.tm_year, expire_ds.tm_mon, expire_ds.tm_mday)
        time_to_expire = abs(expire_date - today)
        return time_to_expire.days

    def watcher(self):
        hd = self.get_hosted_domains()
        for domain in hd:
            domain_date, domain_provider = domain['comment'].split(' | ')
            days_remain = self.get_days_to_expire(domain_date)

            if(days_remain <= self.days_limit):
                self.send_expire_notification(domain['domain'], domain_provider, days_remain)

#Inicializacion de watcher
crb = Cerbero(45).watcher()
