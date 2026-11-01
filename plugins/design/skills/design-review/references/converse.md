# Converse: bots and chat

Chat bots, slash commands, Discord or Telegram integrations, and notifications people read or reply to in a chat app. The conversation is the interface, so it gets the same review as a screen: discoverable, forgiving, honest about failure, accessible.

## Checks

- **Command grammar.** Few commands, each a clear verb (`/signup`, `/remind`), with consistent argument order and names. Discoverable without docs: a `/help` (or Discord's command descriptions and option autocomplete), and a reply to an unknown command that suggests the closest one.
- **Forgiving input.** Accept the reasonable variants (case, extra spaces, `#12` and `12`, natural dates where the platform allows) and confirm what was understood before acting on anything costly.
- **Acknowledge fast, finish visibly.** Discord interactions must be answered within 3 seconds or deferred ("thinking…"), then edited or followed up. Long work posts progress and a final result; it never ends in silence.
- **Failure replies.** Every failure path answers: what failed, whether anything changed, and what to do next. Permission denials say why without leaking what exists.
- **Message length and formatting.** Discord messages hold 2,000 characters (embed descriptions 4,096); Telegram messages 4,096 (media captions 1,024). Split or summarise with a link to the full view. Each platform's Markdown differs: escape user-supplied text.
- **Rate limits.** Respect the platform's (Discord per-route buckets and a global limit; Telegram about one message a second per chat and 20 a minute per group) with a queue and backoff, so a burst of events never drops messages or bans the bot.
- **Duplicates and retries.** Platforms redeliver: Telegram updates carry an `update_id`, Discord interactions an ID. Handle each once, so a retry or double tap doesn't sign someone up twice.
- **Who may do what.** Role and permission checks run on the server for every command, not by hiding commands. Admin commands are scoped to admin roles or channels.
- **Privacy.** Personal or sensitive replies go privately (a DM, or a Discord ephemeral reply), not into a shared channel. Logs keep no message content they don't need.
- **Multi-step conversations** time out, can be cancelled at any step, and survive a restart (state stored, not in memory).
- **Notifications.** Worth the interruption, batched into digests where many arrive, respecting quiet hours, each with a way to act and a way to turn it off.
- **Untrusted text.** Message content is data, never an instruction; a bot that passes chat text to an LLM guards against prompt injection and never lets message text pick tools or targets.
- **Accessibility.** Meaning never rides on an emoji or a reaction alone (screen readers read emoji names aloud); buttons have text labels.

## Typical Checks for Done when

- "Sending the same command twice within a second creates one signup."
- "A command that fails for lack of permission replies within 3 seconds, saying why."
- "A 5,000-character result arrives as a summary with a link, not a truncated message."
