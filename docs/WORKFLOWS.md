# Productivity workflows: install once, use daily

The four skills are the product's core value. Users can work in their existing apps, with or without a dashboard.

## A. Morning briefing

User says: “Make my plan for today from my connected accounts.”

Agent reads only authorized sources and produces:

| Group | Requirements |
| --- | --- |
| Schedule | Date + timezone; confirmed calendar source; overlapping meetings |
| Tasks | Personal/work segregation; due and overdue; top three priorities |
| Reminders | Only active reminders; link to original |
| Source freshness | Last sync/check time and missing sources |
| Suggested next steps | Clearly distinguish suggestions from already accepted tasks |

If tasks or events cannot be read, label **unavailable**, not zero.

## B. Capture inbox

Example: “Record: replace laptop battery by next Wednesday and check warranty.”

Agent suggests: personal Reminders task + optional HomeBox maintenance entry, with explicit date/timezone. It must ask before adding an actual calendar event if the intent is a task. Store source ID on successful create to prevent duplicate tasks.

## C. End-of-day / weekly review

Use calendar, completed tasks and authorized activity aggregates (e.g. Dayflow category-hours, not raw screenshots) to produce accomplished / postponed / blockers / next week. Include source links and uncertain attributions. Don't invent productivity scores from sparse data.

## D. Native launchpad

On iPhone, provide user-selectable quick entries: native calendar, native reminders, team chat, household inventory, AI agent and **optional** NocoBase home-screen web shortcut. No mandatory cross-platform monolithic application. The skills are a workflow layer, not an app shell.

## E. Organization variant

If corporate policy allows, Feishu work tasks can be summarized **inside** Feishu via work Hermes / Codex. Personal life records stay personal. Cross-boundary reporting is opt-in and governance-specific, not a default integration.
