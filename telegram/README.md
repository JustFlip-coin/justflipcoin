# Making the bot answer /start

Right now `/start` gets nothing back. That is not a setting you missed. BotFather
only holds the parts of a bot that sit still: its name, its description, its
picture, and the menu button in the corner. Answering a message needs code
running somewhere that receives the update and sends a reply, and BotFather has
nowhere to run code.

That is the whole difference between Just Flip and the bots that greet you with a
picture and an Open App button.

This folder is that missing piece, written for Supabase because the project
already has one and Edge Functions cost nothing at this size.

## Never paste your bot token into a chat

The token is the bot. Anyone holding it can post as you, read every message sent
to it, and change what it does. It belongs in the two places below and nowhere
else. If it ever leaks, open BotFather, run `/revoke`, and use the new one.

## 1. Install the CLI and log in

```bash
npm install -g supabase
supabase login
supabase link --project-ref ajcgmatgejbiikleszxi
```

## 2. Give it the token and a webhook secret

The webhook secret is any long random string you make up. It is not from
Telegram. It exists so the function can tell a real Telegram call from a stranger
who found the URL, because that URL is public.

```bash
supabase secrets set TELEGRAM_BOT_TOKEN=paste_your_token_here
supabase secrets set TELEGRAM_WEBHOOK_SECRET=make_up_a_long_random_string
```

## 3. Deploy

```bash
supabase functions deploy justflip-bot --no-verify-jwt
```

`--no-verify-jwt` matters. Telegram does not send a Supabase auth header, so
without it every call is rejected before your code ever runs.

The deploy prints the function URL. It looks like:

```
https://ajcgmatgejbiikleszxi.supabase.co/functions/v1/justflip-bot
```

## 4. Point Telegram at it

Run this once, with your own token and the same secret from step 2:

```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://ajcgmatgejbiikleszxi.supabase.co/functions/v1/justflip-bot&secret_token=<YOUR_SECRET>"
```

You want `{"ok":true,"result":true,"description":"Webhook was set"}`.

## 5. Try it

Send `/start` to the bot. A picture, a few lines, and two buttons should come
back. The first opens Just Flip inside Telegram. The second opens it in a
browser, for anyone who prefers that.

## When it does not work

**Still silent.** Ask Telegram what it thinks:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

`last_error_message` usually says it outright. `pending_update_count` climbing
means Telegram is delivering and the function is failing.

**401 in the errors.** The `--no-verify-jwt` flag was left off the deploy.

**403 in the errors.** The secret in `setWebhook` does not match the one in
`supabase secrets set`.

**Function logs.** In the Supabase dashboard under Edge Functions, or:

```bash
supabase functions logs justflip-bot
```

## The rest of the polish, which BotFather does handle

These are the parts you can set without any code, and they are worth doing:

`/setuserpic` gives the bot the avatar from `press/avatar/avatar-400.png`.

`/setdescription` is the text shown before anyone presses start, on that
"What can this bot do?" card.

`/setabouttext` is the shorter line on the bot's profile.

`/setmenubutton` is the button in the corner. Point it at
`https://justflipcoin.xyz` and name it Play. You already have this one.

`/setcommands` lists the commands in the menu, for example:

```
start - Flip a coin
```
