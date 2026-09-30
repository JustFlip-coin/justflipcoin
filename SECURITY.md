# Security Policy

Just Flip gates play behind a wallet signature and writes scores to a shared
database, from a page that is entirely static. That combination draws more
attention than a coin toss usually would, so this spells out where the trust
boundaries actually sit, what is in scope, and how to report a problem privately.

## Reporting a vulnerability

**Please do not open a public issue for a security problem.** Use GitHub's
Private Vulnerability Reporting instead:

[**Report a vulnerability**](https://github.com/JustFlip-coin/justflipcoin/security/advisories/new)

(Repo → Security tab → Report a vulnerability.) That opens a private advisory
only the maintainer can see, so a fix can ship before the details are out.

Please include what you can:

- The file and line, or the flow, that is affected.
- A minimal reproduction or proof of concept.
- What an attacker gains, and roughly how much work it takes them.
- Anything you think is already covered by the known limits below, so we can
  agree quickly on whether it is new.

You will get a first reply within a few days. If a report turns out to be one of
the known limits, that is still useful: it usually means the limit is not written
plainly enough here.

## What is already known, and why

These are not undiscovered bugs. They are the shape of a static site, stated up
front so nobody spends an afternoon proving them.

**The wallet gate runs on the player's own machine.** The page is served from
GitHub Pages with nothing behind it. It asks MetaMask for an account, then for a
signature over a fresh nonce, and keeps the result in `sessionStorage`. Someone
with devtools open can write that key themselves. The gate stops casual entry,
not a motivated person, and it is not a security boundary.

**The signature is never verified cryptographically.** Recovering the signing
address needs `ecrecover`, which needs either a library this single-file build
does not load or a server this project does not have. What the check actually
proves is that MetaMask was present, unlocked, and approved a prompt. That is
worth something, and it is less than verification.

**The leaderboard can be written to directly.** The Supabase key in the page is
the publishable one, which is the correct key to ship in client code, and it can
read scores and insert one. Anyone can therefore post a score without playing
for it. The board is a leaderboard, not a ledger.

**Player names come from strangers.** They are rendered with `textContent`, never
`innerHTML`, so a name cannot inject markup. If you find a path where a name
reaches the DOM as HTML, that one is a real bug and worth reporting.

## In scope

- Anything that lets a page or a link steal a wallet signature, or get a
  signature approved for a message the player did not see.
- Any path where content from the leaderboard is rendered as HTML.
- Anything that causes the page to request a transaction, a token approval, or
  any wallet method beyond `eth_accounts`, `eth_requestAccounts` and
  `personal_sign`.
- Supply chain problems in what the page loads: the Google Fonts stylesheet is
  the only external resource.
- A way to read or write Supabase rows beyond what the publishable key is meant
  to allow.

## Out of scope

- The four known limits above, unless you have found a way to make one of them
  worse than described.
- Posting a fabricated score to the leaderboard. Known, documented, and the
  reason the board is not treated as authoritative.
- Missing security headers on GitHub Pages, which the platform controls.
- Anything requiring a compromised browser, a malicious extension already
  installed, or physical access to an unlocked machine.
- Denial of service against GitHub Pages or Supabase.

## What the page asks of a wallet

The complete list, so it can be checked against the source in one pass:

| Method | When | Why |
| --- | --- | --- |
| `eth_accounts` | on load, only if a session exists | silently reports an approval this browser already gave, without prompting |
| `eth_requestAccounts` | when the player picks MetaMask | the connection prompt |
| `personal_sign` | straight after access is granted | proves the account can be unlocked right now |

Nothing else. There is no `eth_sendTransaction`, no `eth_sign`, no
`wallet_watchAsset`, no token approval. If you find one, that is a serious bug
and a fast fix.

## Fixing the limits

The path out of most of the above is the same: an endpoint that receives the
signature, verifies it with `ecrecover`, and issues a short lived token that the
leaderboard requires for writes. That turns the gate into a real boundary and
turns the board into something worth trusting. It is on the roadmap, not in the
build.
