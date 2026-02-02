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
  mean_hang_time_minutes: number | null
  mean_resolution_time_minutes: number | null
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
```

Note that some fields can be `null` if there are no tickets (or no open/closed/in-progress tickets)
within the time period.
