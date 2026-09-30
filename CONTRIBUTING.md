# Contributing

Bug reports and pull requests are welcome. Security problems go through
[private reporting](SECURITY.md), never a public issue.

## The build

There is no build. `index.html` is the game: markup, styles, art and code in one
file, no dependencies and no bundler. Open it in a browser and you are running
the same thing that is deployed.

```bash
git clone https://github.com/JustFlip-coin/justflipcoin
cd justflipcoin
python -m http.server 8000
```

Then open `http://localhost:8000`. A plain `file://` open mostly works, but
wallet extensions do not inject into every context and `sessionStorage` behaves
differently, so serve it over HTTP when touching either.

Deployment is a push to `main`. GitHub Pages serves the repository root at
[justflipcoin.xyz](https://justflipcoin.xyz), so there is no staging step and no
artifact to build.

## House rules

These are not style preferences. Each one is here because breaking it cost a day.

**Keep `index.html` pure ASCII.** No smart quotes, no em dashes, no accented
characters, no emoji, and no `\u` escapes. Non-ASCII characters have shown up as
mojibake in players' browsers more than once. Use HTML entities where a symbol is
genuinely needed.

```bash
python -c "s=open('index.html',encoding='utf-8').read(); print(sum(1 for c in s if ord(c)>127))"
```

That must print `0`.

**Reduced motion softens, never removes.** `prefers-reduced-motion` should slow
an animation or drop its overshoot. It must never hide an element. An early
version set `display:none` on the loading screen, and for those players the game
simply never appeared.

**`textContent` for anything a stranger typed.** Leaderboard names come from
other people. They are rendered with `textContent`. Do not reach for `innerHTML`
on that path, whatever the escaping looks like.

**No new wallet methods without discussion.** The page calls `eth_accounts`,
`eth_requestAccounts` and `personal_sign`, and nothing else. Adding a fourth
changes the security story, so open an issue before the PR.

**Art is generated, not pasted.** The coins, avatars, banners and video plates
all come out of `brand/make_coins.py` and `press/make_press.py`. Change the
script and rerun it rather than editing a PNG, or the next run silently reverts
your work.

## Before opening a PR

Run these. They are quick and they catch most of what has actually broken here.

```bash
# 1. the JavaScript parses
python -c "
import re
s = open('index.html', encoding='utf-8').read()
b = [m.group(2) for m in re.finditer(r'<script([^>]*)>(.*?)</script>', s, re.S)
     if 'ld+json' not in m.group(1)]
open('_check.js','w',encoding='utf-8').write('\n;\n'.join(b))
"
node --check _check.js && rm _check.js

# 2. no non-ASCII
python -c "s=open('index.html',encoding='utf-8').read(); print('non-ascii:', sum(1 for c in s if ord(c)>127))"

# 3. every getElementById resolves
python -c "
import re
s = open('index.html', encoding='utf-8').read()
ids = set(re.findall(r'id=\"([^\"]+)\"', s))
used = set(re.findall(r\"getElementById\(\s*'([^']+)'\", s))
print('missing:', used - ids or 'none')
print('duplicate:', [i for i in ids if s.count('id=\"%s\"' % i) > 1] or 'none')
"
```

Then play it. Load the page, get past the gate both ways, throw the coin, and
reach a jackpot. Most regressions here have been things a test would not have
caught: focus landing on an invisible button, a transition that never ran, a
canvas that stayed one pixel wide.

If the change touches layout or input, check it at 375px wide as well. Phones
are half the traffic and the failures there are different.

## Commit messages

Say what changed and why it was wrong before. The subject is a sentence, not a
label, and the body carries the reasoning that will not be obvious from the diff
in six months.

## Licence

By contributing you agree your work is released under the [MIT licence](LICENSE).
