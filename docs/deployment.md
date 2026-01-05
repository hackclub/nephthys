# Deploying Nephthys on Hack Club Coolify

Here's a mostly-complete guide to deploying a new instance of Nephthys on the Hack Club Coolify.

You can also follow it to deploy Nephthys elsewhere, but you'll have to replace the Coolify-specific steps with writing docker compose files, or whatever else floats your boat.

## Deploying the database to Coolify

1. Navigate to the **amber/nephthys** project on the Hack Club HQ Coolify
2. Navigate to the Production environment and add a new resource
3. To add the database, select **PostgreSQL**
4. Select the **coolify-app-server-b** server (as it's currently recommended)
5. Select standard PostgreSQL
6. Update the database name to something useful like "Flavorbase" or "Construct Data". Perhaps add a description too.
7. You'll need the **Postgres URL (internal)** later, so write it down or idk, keep the tab open or something
8. You can start the database now, or later. Just don't forget to do it

## Deploying Nephthys to Coolify

1. In the same Production environment, add a new application
2. Select **Private Repository (with GitHub App)** (this ensures auto-deploys work)
3. Select the **coolify-app-server-b** server (to match the database)
4. Use the **coolify-hackclub** GitHub app (because everyone else uses it, I guess)
5. Select the **nephthys** repository
6. Select **Dockerfile** as the Build Pack

   ![Screenshot of the Coolify UI](deployment-1.png)

7. Update the name and description to be descriptive
8. Update the domain to be a custom one you've set up on [hackclub/dns](https://github.com/hackclub/dns) (it should be `[something].nephthys.hackclub.com`) (or leave the ugly default domain)
9. Environment variables! We'll set them later

## Creating the Slack app

Note: These steps have to be done by a Workspace Admin (otherwise it will be unable to fully delete threads in the tickets channel).

1. Go to <https://api.slack.com/apps>
2. Create New App > From a manifest
3. Select YAML. Paste the [manifest.yml](../manifest.yml) file (but don't submit it yet)
4. Update the `https://nephthys.hackclub.com/` URLs in the manifest to match the bot's domain (see above), and update the `name`, `description`, and bot user's `display_name`.
5. Important: **Change the name of the `/dm-magic-link` command!** Or remove it entirely if it's not relevant
6. Review the app's permissions and authorise it
7. Click **OAuth & Permissions** in the sidebar, and hit **Install to Hack Club**

## Setting environment variables

1. Go back to the Nephthys resource you created in Coolify, and click on **Configuration** > **Environment Variables**. Click **Developer view** (production environment variables) to make it easier to add all the variables.
2. Add the required environment variables (see [.env.sample](../.env.sample) for an up-to-date list of environment variables):

   ```bash
   # Keep these as they are
   ENVIRONMENT="production"
   PORT=3000
   # Copy these from the Slack bot OAuth & Permissions screen
   SLACK_USER_TOKEN="xoxp-..."
   SLACK_BOT_TOKEN="xoxb-..."
   # Slack bot basic information screen
   SLACK_SIGNING_SECRET="..."
   # This should probably be your Slack ID
   SLACK_MAINTAINER_ID="U..."
   # Channels that will be used by the bot
   SLACK_HEARTBEAT_CHANNEL="C..."
   SLACK_TICKET_CHANNEL="C..."
   SLACK_BTS_CHANNEL="C..."
   SLACK_HELP_CHANNEL="C..."
   # Slack user group for the support team
   SLACK_USER_GROUP="S..."
   # Copy this from the PostgreSQL resource you created earlier
   DATABASE_URL="postgres://postgres:blahblah@somewhere:5432/postgres"
   # Pick a transcript from the transcripts/ folder (your event will probably have its own)
   PROGRAM="flavortown"
   # Choose a title to be shown to helpers at the top of the App Home
   APP_TITLE="Heidi the Assistant"
   # Hack Club AI API key for generating ticket titles (highly recommended)
   HACK_CLUB_AI_API_KEY="sk-hc-v1-..."
   # Set this to anything
   SITE_API_KEY="none"
   ```

   - `SITE_API_KEY` (and `SITE_URL`) are only used for generating magic links for Summer of Making, so they don't have to be included (but `SITE_API_KEY` must be set due to a bug)

3. There's more optional environment variables that you can set, which I shall document here:

   ```bash
   # Export logs to an OpenTelemetry endpoint (optional)
   # example using Loki:
   OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://loki.example.com/otlp/v1/logs"
   # If HTTP Basic Authentication is required for the OTLP endpoint, specify it here
   # If your password has special characters, switch to normal view to add it, and check the "Is Literal?" checkbox
   OTEL_EXPORTER_OTLP_LOGS_BASIC_AUTH="username:password"
   # You can change the OTel service name if you want, but you don't have to
   OTEL_SERVICE_NAME="nephthys"
   # Setting this to any value disables daily summary messages (yes, this is counter-intuitive and will be changed soon)
   DAILY_SUMMARY=""
   # Set the log level (defaults to "WARNING" in production)
   LOG_LEVEL="WARNING"
   # Override the log level for console output
   LOG_LEVEL_STDERR="WARNING"
   # Override the log level for OpenTelemetry output
   LOG_LEVEL_OTEL="WARNING"
   ```

4. Don't forget to click **Save All Environment Variables**

## Some final pre-requisites

1. Add the bot to the BTS channel, help channel, tickets channel, and heartbeat channel
2. Add the user who authorised the bot (probably you!) to (at least) the tickets channel
3. Ensure your DNS PR has been made and merged (if applicable)
4. You can also set a profile picture for the Slack bot in the Slack app settings at this point
5. The database should be started by this point

## Deploying

1. Press **Deploy** on the new Nephthys resource in Coolify
2. It will take some time to build, deploy, and start
3. You should see a message in the heartbeats channel and the bot should respond to messages in the help channel
   - If it isn't responding to anything, check the logs in Coolify for errors, and double-check all the URLs in the Slack app settings are valid
