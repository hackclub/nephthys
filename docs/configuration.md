# Nephthys configuration options

Nephthys is configured using environment variables, which can be set
e.g. in Coolify or a Docker compose file, or loaded from a `.env` file.

For development, copying and editing the [`.env.sample`](../.env.sample)
file is the easiest way to get started, but for production there are some
more options and features that you may with to configure.

## Core environment variables

These should always be configured.

<!-- prettier-ignore -->
| Variable | Required? | Description | Default |
| -------- | --------- | ----------- | ------- |
| `ENVIRONMENT` | Required | Set to `production` for production or staging deployments | `development` |
| `PORT` | Optional | HTTP server port | `3000` |
| `SLACK_USER_TOKEN` | Required | Slack bot user token | _N/A_ |
| `SLACK_BOT_TOKEN` | Required | Slack bot bot token | _N/A_ |
| `SLACK_SIGNING_SECRET` | Required | Slack bot signing secret | _N/A_ |
| `SLACK_MAINTAINER_ID` | Required | Slack user ID to ping on certain exceptions | _N/A_ |
| `SLACK_HEARTBEAT_CHANNEL` | Required | Channel where "heartbeat" (debug) messages are set | _N/A_ |
| `SLACK_TICKET_CHANNEL` | Required | Channel where unresolved threads will be kept | _N/A_ |
| `SLACK_BTS_CHANNEL` | Required | Support team channel, used for permission checks | _N/A_ |
| `SLACK_HELP_CHANNEL` | Required | Public channel where questions are asked | _N/A_ |
| `DATABASE_URL` | Required | PostgreSQL database connection URL | _N/A_ |
| `PROGRAM` | Required | Name of a transcript (see `transcripts/` folder) the bot will use for its strings | _N/A_ |
| `APP_TITLE` | Required | A title to be shown to helpers at the top of the App Home, and in the Lobby | _N/A_ |
| `BASE_URL` | Required | Public HTTPS URL that the bot's web server is accessible from | _N/A_ |

## AI (Hack Club AI)

It is highly recommended to configure a LLM provider, which is used to generate ticket titles and categorise tickets.

The default provider is [Hack Club AI](https://ai.hackclub.com/). If you're not a Hack Clubber, you can specify a different OpenRouter-compatible or OpenAI-compatible endpoint for API requests.

If you don't wish to use AI features, you can skip this section. Note that ticket titles will be unavailable.

<!-- prettier-ignore -->
| Variable | Required? | Description | Default |
| -------- | --------- | ----------- | ------- |
| `HACK_CLUB_AI_API_KEY` | Required | Hack Club AI API key for generating ticket titles | _N/A_ |
| `HACK_CLUB_AI_BASE_URL` | Optional | Any OpenAI compatible base url | `https://ai.hackclub.com/proxy/v1` |
| `AI_TITLE_MODEL` | Optional | Model for generating ticket titles | `openai/gpt-oss-120b` |
| `AI_TAG_MODEL` | Optional | Model for categorising tickets | `google/gemini-3-flash-preview` |

## Logging

You can customise logging. I'd recommend setting `LOG_LEVEL` to `INFO` in production to aid in troubleshooting issues with e.g. tickets failing to resolve or be created.

Log level definitions are roughly as follows:

- `INFO` - Normal operations of the bot
- `WARNING` - Things that may suggest an issue, but don't immediately cause any problems
- `ERROR` - Something happened that shouldn't have; a function or event handler may have failed

<!-- prettier-ignore -->
| Variable | Required? | Description | Default |
| -------- | --------- | ----------- | ------- |
| `LOG_LEVEL` | Optional | Set the default log level | `WARNING` |
| `LOG_LEVEL_STDERR` | Optional | Override the log level for console output | Value of LOG_LEVEL |

## Ticket feedback

Enabling this feature prompts the asker of a question to give feedback after their ticket is resolved. Feedback is stored in the database.

This feature is recommended.

<!-- prettier-ignore -->
| Variable | Required? | Description | Default |
| -------- | --------- | ----------- | ------- |
| `ENABLE_FEEDBACK` | Required | Enable the feedback prompt | `false` |

## HCA integration (for Nephthys Lobby and API keys)

Configuring Hack Club Auth (HCA) integration allows Hack Clubbers to log into the Lobby and create API keys for privileged API access.

If this is not configured, the Lobby will be unavailable (although API keys in the database will continue to work). It is recommended to configure HCA to provide a way for API users to access to privileged data (message contents).

To set this up, you'll need to create a [new HCA Oauth app](https://auth.hackclub.com/developer/apps/new) (you must have developer mode enabled on HCA) with the `slack_id` scope. The redirect URI should be your Nephthys base URL + `/oauth/callback`.

The `SESSION_SECRET` is a secret key used to sign session cookies. If someone gains access to it, they can impersonate any user. Generate one securely with a command like `openssl rand -base64 32`

<!-- prettier-ignore -->
| Variable | Required? | Description | Default |
| -------- | --------- | ----------- | ------- |
| `HCA_CLIENT_ID` | Required | Client ID from your HCA OAuth App | _N/A_ |
| `HCA_CLIENT_SECRET` | Required | Client secret from your HCA OAuth App | _N/A_ |
| `SESSION_SECRET` | Required | Secure, randomly-generated secret key for signing sessions | _N/A_ |
| `HCA_BASE_URL` | Optional | The base URL for HCA | `https://auth.hackclub.com` |

## OpenTelemetry log drain

For observability nerds, logs can be optionally sent to an OpenTelemetry-compatible endpoint.

Mish likes to use this because he doesn't trust Coolify's log output to work 100% of the time.

If you don't want to configure this, or don't know what OpenTelemetry is, skip this section.

<!-- prettier-ignore -->
| Variable | Required? | Description | Default |
| -------- | --------- | ----------- | ------- |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` | Required | Export logs to an OpenTelemetry endpoint | _Unset_ (feature disabled) |
| `OTEL_EXPORTER_OTLP_LOGS_BASIC_AUTH` | Optional | If HTTP Basic Authentication is required for the OTLP endpoint, specify it here | _Unset_ |
| `OTEL_SERVICE_NAME` | Optional | You can change the OTel service name if you want, but you don't have to | `nephthys` |
| `LOG_LEVEL_OTEL` | Optional | Override the log level for OpenTelemetry output | Value of LOG_LEVEL |

## Stale ticket auto-close

Using this feature is **not recommended** for most help channels, as tickets being automatically close after X days is frustrating for question askers and hides the real number of unanswered questions.

<!-- prettier-ignore -->
| Variable | Required? | Description | Default |
| -------- | --------- | ----------- | ------- |
| `STALE_TICKET_DAYS` | Required | Enable stale ticket auto-close; tickets inactive for this many days will be automatically closed; leave unset to disable | _Unset_ (disabled) |

## Other feature flags

You may wish to disable the daily summary for every low-traffic support channels.

<!-- prettier-ignore -->
| Variable | Description | Default |
| -------- | ----------- | ------- |
| `DAILY_SUMMARY` | Set this to false to disable daily summary messages in the BTS channel | `true` |
