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
                thread_ts=ticket.msgTs,
                user=helper.slackId,
                text="Usage: `?tag <tag name>`",
            )
            return

        tag_name = parts[1].strip()

        all_tags = await env.db.tag.find_many()

        tag = next((t for t in all_tags if t.name == tag_name), None)
        if not tag:
            matches = [t for t in all_tags if t.name.lower() == tag_name.lower()]
            tag = matches[0] if matches else None

        if not tag:
            names = ", ".join(f"`{t.name}`" for t in all_tags)
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msgTs,
                user=helper.slackId,
                text=f"Tag `{tag_name}` not found. Available tags: {names}"
                if names
                else f"Tag `{tag_name}` not found. No tags exist yet.",
            )
            return

        existing = await env.db.tagsontickets.find_first(
            where={"ticketId": ticket.id, "tagId": tag.id}
        )
        if existing:
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msgTs,
                user=helper.slackId,
                text=f"Tag `{tag.name}` is already on this ticket.",
            )
            return

        await env.db.tagsontickets.create(
            data={
                "tag": {"connect": {"id": tag.id}},
                "ticket": {"connect": {"id": ticket.id}},
            }
        )

        subscriptions = await env.db.usertagsubscription.find_many(
            where={"tagId": tag.id}
        )
        subscriber_ids = [s.userId for s in subscriptions if s.userId != helper.id]

        if subscriber_ids:
            subscribers = await env.db.user.find_many(
                where={"id": {"in": subscriber_ids}}
            )
            url = get_question_message_link(ticket)
            ticket_url = get_backend_message_link(ticket)
            for user in subscribers:
                await env.slack_client.chat_postMessage(
                    channel=user.slackId,
                    text=f"New ticket for *{tag.name}*: *{ticket.title}*\n<{url}|ticket> <{ticket_url}|bts ticket>",
                )

        await env.slack_client.chat_postEphemeral(
            channel=env.slack_help_channel,
            thread_ts=ticket.msgTs,
            user=helper.slackId,
            text=f"Tagged `{tag.name}`.",
        )
