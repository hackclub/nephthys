# Nephthys

Nephthys is the bot powering #summer-of-making-help and #identity-help in the Hack Club Slack! Below is a guide to set her up for developing and here's a list of some of her features :)

## Features

### Question tags

Quite often in help channels, the same question gets asked again and again. Helpers can associate tickets with a "question tag", which are pre-defined questions/issue such as "What's the payout range?", "How to top up grant?", or "404 on /shop". We can then keep track of how these questions trend over time, to provide a feedback loop for people building the event/platform/YSWS.

They can be added to tickets in the private tickets channel.

### Team tags

Team tags let you tag tickets that are the responsibility of a specific group of people (or perhaps just one person). E.g. you could have tags for Fufillment, Hack Club Auth, Onboarding flow, etc.

You can add team tags to tickets in the private tickets channel or with the macro `?tag <tag_name>`. This will DM the people who are specialised in responding to those issues and have it show up in their assigned tickets.
You can assign yourself to get notified for specific tags on the app home

### Macros

Sometimes it’s nice to be able to do things quickly... Here’s where macros come in! Send one of the following messages in an open thread and something will happen

- `?resolve` - the ticket gets closed. Equivalent of hitting the resolve button
- `?reopen` - reopen a closed ticket
- `?identity` - redirect to #identity-help
- `?faq` - redirect to the FAQ
- `?hii` - silly message :3
- `?shipcertqueue` - tell them to wait and vote because there's a backlog of ships
- `?fraud` - redirect to Fraud Squad
- `?thread` - remove the reaction and all Nephthys replies to unclutter duplicates
- `?shipwrights` - redirect to #ask-the-shipwrights
- more to come?? feel free to PR your own into hackclub/nephthys or tell me what you want

### Stale

~~Tickets that have been not had a response for more than 3 days will automatically be closed as stale. The last helper to respond in the thread gets credit for closing them~~

Stale ticket handling is not working at the moment, but more features for dealing with stale tickets are planned.

### Leaderboard

At midnight UK time each day, you get to see the stats for the day in the team channel! Helpers can also see more detailed stats at any time on the app home for the bot!

### Assigned Tickets

When you send a message in a help thread, that thread is assigned to you and it is up to you to resolve it. You can see a list of threads waiting for you on the app home - just select the Assigned Tickets tab at the top

## Prerequisites

- Python (3.13 or later)
- uv
- A Slack workspace where you have permissions to install apps
- Tunneling tool (for local development)
- A PostgreSQL database (you can run one in Docker using the command below)

```bash
docker run --name hh-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

## Setting up the Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps) and click "Create New App".
2. Choose "From an app manifest" and select your workspace.
3. Copy and paste the manifest in `manifest.yml`.
4. Review and create the app.
5. In the "Basic Information" section, note down the `App Id`, `Client Id`, `Client Secret`, `Signing Secret` .
6. Go to "OAuth & Permissions" and install the app to your workspace. Note down the "Bot User OAuth Token".

## Setting up the Project

1. Clone the repository:

   ```
   git clone https://github.com/hackclub/nephthys
   cd nephthys
   ```

2. Install dependencies:

   ```
   uv sync
   source .venv/bin/activate # for bash/zsh
   source .venv/bin/activate.fish # for fish
   source .venv/bin/activate.csh # for csh
   source .venv/bin/activate.ps1 # for powershell
   ```

3. Copy the `.env.sample` file to `.env`:

   ```
   cp .env.sample .env
   ```

4. Edit the `.env` file and fill in the values:

## Running the Application

1. Start your tunneling tool and expose the local server. (Not needed in socket mode with `SLACK_APP_TOKEN` set)

   Note the HTTPS URL you get.

2. Update your Slack app's request URLs:

   - Go to your Slack app's settings.
   - In "Event Subscriptions" and "Interactivity & Shortcuts", update the request URL to your HTTPS URL followed by `/slack/events`.
   - In "OAuth & Permissions", update `Redirect URLs` to your HTTPS URL followed by `/slack/oauth_redirect`.

3. MAKE SURE YOU CHANGE THE COMMAND - DO NOT USE THE SAME COMMAND
4. Install pre-commit hooks:

   ```
   uv run pre-commit install
   ```

5. Start your database and update the database schema:

   ```
   uv run prisma db push
   uv run prisma generate
   ```

6. Start the application:
   ```
   nephthys
   ```

Your Slack app should now be running and connected to your Slack workspace!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Scripts

The codebase contains some scripts in the `nephthys/scripts/` directory to help with development and testing. They are documented below.

#### Adding Dummy Data

`add_dummy_data.py` is a script that adds a bunch of dummy (i.e. fake) support ticket records to the database, for stress-testing/performance testing.

Usage: `uv run nephthys/scripts/add_dummy_data.py <num_records>`

- Ensure you run it after the `nephthys` has been run at least once (and once the DB has been initialized)
- It takes a while to run (adding 20k records takes ~50 seconds on my machine)
- Don't run this in production, obviously

## License

This project is licensed under the MIT License.
