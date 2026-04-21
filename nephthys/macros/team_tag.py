from nephthys.database.tables import TagsOnTickets
from nephthys.database.tables import TeamTag as TeamTagTable
from nephthys.database.tables import User
from nephthys.database.tables import UserTagSubscription
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.ticket_methods import get_backend_message_link
from nephthys.utils.ticket_methods import get_question_message_link


class TeamTag(Macro):
    name = "tag"

    async def run(self, ticket, helper, **kwargs):
        text: str = kwargs.get("text", "")
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msg_ts,
                user=helper.slack_id,
                text="Usage: `?tag <tag name>`",
            )
            return

        tag_name = parts[1].strip()

        all_tags = await TeamTagTable.objects()

        tag = next((t for t in all_tags if t.name == tag_name), None)
        if not tag:
            matches = [t for t in all_tags if t.name.lower() == tag_name.lower()]
            tag = matches[0] if matches else None

        if not tag:
            names = ", ".join(f"`{t.name}`" for t in all_tags)
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msg_ts,
                user=helper.slack_id,
                text=f"Tag `{tag_name}` not found. Available tags: {names}"
                if names
                else f"Tag `{tag_name}` not found. No tags exist yet.",
            )
            return

        existing = (
            await TagsOnTickets.objects()
            .where((TagsOnTickets.ticket == ticket.id) & (TagsOnTickets.tag == tag.id))
            .first()
        )
        if existing:
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msg_ts,
                user=helper.slack_id,
                text=f"Tag `{tag.name}` is already on this ticket.",
            )
            return

        link = TagsOnTickets(tag=tag.id, ticket=ticket.id)
        await link.save()

        subscriptions = await UserTagSubscription.objects().where(
            UserTagSubscription.tag == tag.id
        )
        subscriber_ids = [s.user for s in subscriptions if s.user != helper.id]

        if subscriber_ids:
            subscribers = await User.objects().where(User.id.is_in(subscriber_ids))
            url = get_question_message_link(ticket)
            ticket_url = get_backend_message_link(ticket)
            for user in subscribers:
                await env.slack_client.chat_postMessage(
                    channel=user.slack_id,
                    text=f"New ticket for *{tag.name}*: *{ticket.title}*\n<{url}|ticket> <{ticket_url}|bts ticket>",
                )

        await env.slack_client.chat_postEphemeral(
            channel=env.slack_help_channel,
            thread_ts=ticket.msg_ts,
            user=helper.slack_id,
            text=f"Tagged `{tag.name}`.",
        )
