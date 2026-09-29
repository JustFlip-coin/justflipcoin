// Telegram calls this on every update. It answers /start with the card players
// expect: a picture, a line about the game, and a button that opens Just Flip
// inside Telegram rather than kicking them out to a browser.
//
// Deploy:  supabase functions deploy justflip-bot --no-verify-jwt
// Secrets: supabase secrets set TELEGRAM_BOT_TOKEN=... TELEGRAM_WEBHOOK_SECRET=...

const API = "https://api.telegram.org/bot";
const SITE = "https://justflipcoin.xyz";

const CAPTION = [
  "What if you could just flip a coin and keep going?",
  "",
  "No overthinking, no complicated rules. Pick heads or tails, make the flip,",
  "and see what happens.",
  "",
  "Heads or tails?",
].join("\n");

function json(body: unknown) {
  return new Response(JSON.stringify(body), {
    headers: { "Content-Type": "application/json" },
  });
}

async function call(token: string, method: string, body: unknown) {
  const r = await fetch(API + token + "/" + method, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) console.error(method, r.status, await r.text());
  return r;
}

Deno.serve(async (req) => {
  const token = Deno.env.get("TELEGRAM_BOT_TOKEN");
  const secret = Deno.env.get("TELEGRAM_WEBHOOK_SECRET");
  if (!token) return json({ error: "TELEGRAM_BOT_TOKEN is not set" });

  // This URL is public, so anything could POST to it. Telegram echoes the secret
  // back on every call; without this check a stranger could make the bot speak.
  if (secret && req.headers.get("X-Telegram-Bot-Api-Secret-Token") !== secret) {
    return new Response("forbidden", { status: 403 });
  }

  let update: any;
  try {
    update = await req.json();
  } catch {
    return json({ ok: true });
  }

  const msg = update.message ?? update.edited_message;
  const text: string = msg?.text ?? "";

  // Telegram retries anything that is not answered quickly, so every path here
  // returns ok, including the ones that do nothing.
  if (!msg || !text.startsWith("/start")) return json({ ok: true });

  await call(token, "sendPhoto", {
    chat_id: msg.chat.id,
    photo: SITE + "/brand/og.png",
    caption: CAPTION,
    reply_markup: {
      inline_keyboard: [
        [{ text: "Play Just Flip", web_app: { url: SITE } }],
        [{ text: "Open the website", url: SITE }],
      ],
    },
  });

  return json({ ok: true });
});
