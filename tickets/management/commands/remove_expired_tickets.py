from django.core.management.base import BaseCommand
from tickets.models import AccessTicket
from django.utils import timezone

class Command(BaseCommand):
    help = 'Remove expired tickets from MikroTik'

    def handle(self, *args, **kwargs):
        expired_tickets = AccessTicket.objects.filter(expiry_date__lt=timezone.now(), is_active=True)
        for ticket in expired_tickets:
            ticket.is_active = False
            ticket.save()
            ticket.remove_from_router()
            self.stdout.write(f"Ticket {ticket.ticket_code} expired and removed.")
