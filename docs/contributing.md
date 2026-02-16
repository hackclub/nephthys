# Nephthys contributing guide

This is not a full guide by any means, but it documents some bits about the codebase that are useful to know.

## Getting started

See the [README](../README.md#prerequisites) for instructions on setting up a development environment for the bot!

### Pre-commit hooks

It's recommended to install the pre-commit hooks (for code formatting and import sorting):

```bash
uv run pre-commit install
```

However, if you aren't able to do that, you can run them manually (after making your changes) with:

```bash
uv run pre-commit run --all-files
```

## Branches, PRs, and commits

See the [Hack Club Contribution Guidelines](https://github.com/hackclub/.github/blob/main/CONTRIBUTING.md) for information about the GitHub Flow, how to name commits, and similar things.

## File structure

All the Python code lives in `nephthys/`. Take a look around to get a feel for what all the subfolders are.

Tip: You can ignore a lot of of the subfolders most of the time, and just look at the ones relevant to your feature/change.

We prefer splitting code up into many Python files over having large files with a lot of code.

## Slack Block Kit

We now have the [`blockkit` library](https://blockkit.botsignals.co/) (!!) for building fancy Slack messages and views with buttons, dropdowns, etc.
All new code should use `blockkit`, but note that existing code likely still uses raw JSON objects.
