from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tournament
from .telegram_notify import send_tournament_to_telegram, delete_tournament_message, update_tournament_message

@receiver(post_save, sender=Tournament)
def publish_tournament_to_telegram(sender, instance, created, **kwargs):
    if created:
        participants = instance.participant_set.all()
        send_tournament_to_telegram(instance, participants)

@receiver(post_delete, sender=Tournament)
def delete_tournament_from_telegram(sender, instance, **kwargs):
    delete_tournament_message(instance)

@receiver(post_save, sender=Tournament)
def update_tg_after_tournament_edit(sender, instance, **kwargs):
    participants = instance.participant_set.all()
    update_tournament_message(instance, participants)