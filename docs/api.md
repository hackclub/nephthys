# Nephthys API docs

There is no proper API documentation (apart from [the code](https://github.com/hackclub/nephthys/blob/main/nephthys/utils/starlette.py)) yet, but
here's some explanation of the important routes.

All routes respond with JSON.

## `/api/stats_v2`

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

## `/api/tickets`

Returns a big list of tickets and their details! Please provide filters using query parameters
to avoid overloading Nephthys as it tries to provide 1,000s of tickets at once.

Parameters available are:

- `?status=` - filter by ticket status, can be `open`, `closed`, or `in_progress`
- `?since=` or `?after=` - filter for tickets created after a certain date/time, in ISO 8601 format (e.g. `2026-01-01`)
- `?until=` or `?before=` - filter for tickets created before a certain date/time, in ISO 8601 format (e.g. `2026-01-31T12:00:00`)

Returns an array of ticket objects. Ticket objects look like this:

```ts
interface Ticket {
  id: number
  title: string
  description: string
  status: "OPEN" | "CLOSED" | "IN_PROGRESS"
  opened_by: User | null
  closed_by: User | null
  assigned_to: User | null
  reopened_by: User | null
  tags: Array<string>
  created_at: string
  message_ts: string
}

interface User {
  id: number
  slack_id: string
}
```

## `/api/ticket?id=<TICKET_ID>`

Returns a single ticket! See above for details on the ticket object returned.

Required parameter:

- `?id=` - the ID of the ticket to return
