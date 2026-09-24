# Nephthys API docs

There is no proper API documentation (apart from [the code](https://github.com/hackclub/nephthys/blob/main/nephthys/utils/starlette.py)) yet, but
here's some explanation of the important routes.

All routes respond with JSON.

## Routes

### `/api/stats_v2`

Statistics! Gives a bunch of metric-like statistic numbers so that you
can see how the support channel is doing.

Gives a response like:

```ts
interface StatsV2 {
  all_time: OverallStats
  past_24h: TimeBoundStats
  past_24h_previous: TimeBoundStats
  past_7d: TimeBoundStats
  past_7d_previous: TimeBoundStats
}

interface OverallStats {
  tickets_total: number
  tickets_open: number
  tickets_closed: number
  tickets_in_progress: number
  helpers_leaderboard: Array<LeaderboardEntry>
  mean_hang_time_minutes_unresolved: number | null
  mean_hang_time_minutes_all: number | null
  mean_resolution_time_minutes: number | null
  oldest_unanswered_ticket: OldestUnansweredTicket | null
}

interface TimeBoundStats {
  /** Tickets created within the time period */
  new_tickets_total: number
  /** Tickets created within the time period and now closed */
  new_tickets_now_closed: number
  /** Tickets created within time period that are now open */
  new_tickets_still_open: number
  /** Tickets created within time period that are now in progress */
  new_tickets_in_progress: number
  /** Tickets closed within the time period */
  closed_today: number
  /** Tickets created and closed within the time period */
  closed_today_from_today: number
  /** Tickets assigned within the time period that are now in progress */
  assigned_today_in_progress: number
  /** Leaderboard for tickets closed within the time period */
  helpers_leaderboard: Array<LeaderboardEntry>
  /** Mean time to first helper response for tickets created within the time period that are currently unresolved */
  mean_hang_time_minutes_unresolved: number | null
  /** Mean time to first helper response for tickets created within the time period */
  mean_hang_time_minutes_all: number | null
  /** Mean time to resolution for tickets created within the time period */
  mean_resolution_time_minutes: number | null
}

interface LeaderboardEntry {
  id: number
  slack_id: string
  count: number
}

interface OldestUnansweredTicket {
  id: number
  created_at: string
  age_minutes: number
  link: string
}
```

Note that some fields can be `null` if there are no tickets (or no open/closed/in-progress tickets)
within the time period.

### `/api/tickets`

Returns a big list of tickets and their details! Please provide filters using query parameters
to avoid overloading Nephthys as it tries to provide 1,000s of tickets at once.

Parameters available are:

- `?status=` - filter by ticket status, can be `open`, `closed`, or `in_progress`
- `?since=` or `?after=` - filter for tickets created after a certain date/time, in ISO 8601 format (e.g. `2026-01-01`)
- `?until=` or `?before=` - filter for tickets created before a certain date/time, in ISO 8601 format (e.g. `2026-01-31T12:00:00`)

The `description` field is not included by default, as it is Slack message content protected by the
[Fire Department's scraping policy](https://news.hackclub.com/news/scraping-use-policy/).
Members of the Hack Club Slack can create an API key, and requests made with an API key will mean the `description` field is included.
See [Authentication](#authentication) below for details.

Returns an array of ticket objects. Ticket objects look like this:

```ts
interface Ticket {
  id: number
  // "No title provided by AI." means no title is available: I suggest
  // displaying truncated description (if possible) or ticket ID, instead
  title: string | "No title provided by AI."
  status: "OPEN" | "CLOSED" | "IN_PROGRESS"
  opened_by: User | null
  closed_by: User | null
  assigned_to: User | null
  reopened_by: User | null
  team_tags: Array<string>
  category_tag: string | null
  // Timestamps in ISO 8601 format
  created_at: string
  closed_at: string | null
  // Slack message ts, e.g. 1775942657.605349
  message_ts: string
  // Only present when authenticated with a valid API key
  description?: string
}

interface User {
  id: number
  slack_id: string
  // Internal Slack username. (Prefer dynamically fetching display name from slack_id if showing to users)
  username: string | null
}
```

Note that the `description` field was removed from the API on 16 June 2026 to comply with the [Hack Club Slack Scraping Policy](https://news.hackclub.com/news/scraping-use-policy/), as it contains message content. It is now only returned when you authenticate with a valid API key (see [Authentication](#authentication)). Without a key, the `title` field can be used as a summarised alternative of the ticket content.

### `/api/ticket?id=<TICKET_ID>`

Returns a single ticket! See above for details on the ticket object returned.

Required parameter:

- `?id=` - the ID of the ticket to return

## Authentication

Some routes accept optional authentication with an API key. This should
be provided in an `Authorization` header, for example:

```http
Authorization: Bearer sk_neph_123abcde...
```

API keys are available only to Hack Clubbers who have a Hack Club Slack account (including alumni) and allow access to Slack message contents.

API keys can be created by signing in (with HCA) to the "Lobby", a web interface that can be accessed in a browser at `/lobby` (e.g. <https://stardance.nephthys.hackclub.com/lobby>) - follow the steps to create one or more API keys.

Each Nephthys instance is independent, so an API key created for `flavortown.nephthys.hackclub.com` _won't_ work for `stardance.nephthys.hackclub.com` (for example).

> [!NOTE]
> Treat message content in accordance with the [Slack Scraping Policy](https://news.hackclub.com/news/scraping-use-policy/). Notably, you must not make messages publicly accessible on the open web, and you must not train AI models on messages.

As always, keep your API keys secure! You can delete them from the Lobby if required.
