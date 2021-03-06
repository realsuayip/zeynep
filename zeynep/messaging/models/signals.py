from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver

from zeynep.messaging.models import Conversation, ConversationRequest, Message


@receiver(post_save, sender=Message, dispatch_uid="deliver_message")
def deliver_message(instance, created, **kwargs):
    if not created:
        return

    sender, recipient = instance.sender, instance.recipient

    holder, _ = sender.conversations.get_or_create(target=recipient)
    target, _ = recipient.conversations.get_or_create(target=sender)
    ConversationRequest.objects.compose(sender, recipient)

    holder.messages.add(instance)
    target.messages.add(instance)
    holder.save(update_fields=["date_modified"])
    target.save(update_fields=["date_modified"])
    instance.websocket_send(target.pk)


@receiver(m2m_changed, sender=Conversation.messages.through)
def delete_orphan_messages_individual(action, pk_set, **kwargs):
    if (
        action == "post_remove"
        and not Conversation.objects.filter(messages__in=pk_set).exists()
    ):
        Message.objects.filter(pk__in=pk_set).delete()


@receiver(pre_delete, sender=Conversation)
def delete_orphan_messages_bulk(instance, **kwargs):
    instance.messages.remove(*instance.messages.all())
