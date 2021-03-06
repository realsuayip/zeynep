import types

from rest_framework import exceptions, serializers

from zeynep.auth.serializers.user import UserPublicReadSerializer
from zeynep.messaging.models import Conversation, ConversationRequest, Message


class MessageComposeSerializer(serializers.HyperlinkedModelSerializer):
    conversation = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name="conversation-detail",
        source="sender_conversation",
    )

    class Meta:
        model = Message
        fields = (
            "id",
            "body",
            "conversation",
            "date_created",
        )

    def create(self, validated_data):
        sender = self.context["request"].user
        recipient = self.context["recipient"]
        body = validated_data["body"]

        message = Message.objects.compose(sender, recipient, body)

        if message is None:
            raise exceptions.PermissionDenied

        return message


MessageSourceType = serializers.ChoiceField(choices=["sent", "received"])


class MessageSerializer(serializers.ModelSerializer):
    date_read = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "body", "source", "date_created", "date_read")

    def get_date_read(  # noqa
        self, message
    ) -> serializers.DateTimeField(allow_null=True):
        return message.date_read if message.has_receipt else None

    def get_source(self, message) -> MessageSourceType:
        user = self.context["request"].user
        return "sent" if message.sender_id == user.pk else "received"


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    target = UserPublicReadSerializer(
        fields=(
            "id",
            "display_name",
            "username",
            "profile_picture",
            "is_private",
            "url",
        )
    )
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "id",
            "target",
            "last_message",
            "date_created",
            "date_modified",
            "url",
        )

    def get_last_message(self, obj) -> MessageSerializer(allow_null=True):
        if obj.last_message is None:
            return None

        message = types.SimpleNamespace(**obj.last_message)
        serializer = MessageSerializer(message, context=self.context)
        return serializer.data


class ConversationDetailSerializer(ConversationSerializer):
    accept_required = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "id",
            "target",
            "accept_required",
            "last_message",
            "date_created",
            "date_modified",
            "url",
        )

    def get_accept_required(self, conversation) -> bool:  # noqa
        return ConversationRequest.objects.filter(
            date_accepted__isnull=True,
            recipient=conversation.holder_id,
            sender=conversation.target_id,
        ).exists()
