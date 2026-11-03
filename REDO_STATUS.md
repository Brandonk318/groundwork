# Groundwork locale REDO status

Fresh from-scratch redo of all 88 non-baseline locales (everything except `en`).
`es` is the untouched Spanish baseline. `ru` was redone fresh Nov 3 (Brann
clarified it is NOT his own translation; the old file was NLLB-200 output).
No Hmong locale exists in this repo.

Method per locale: translated fresh from the English source (+ Spanish reference),
never reusing old locale files or NLLB/template output. Placeholders (`{{app}}`,
`{{...}}`), brand names, URLs kept exact. No `⁇` anywhere. The 25 protected
crisis/988/911/legal/money keys stay English in live files; review drafts live in
`docs/review/protected-<lang>.json`. `reentry.crisisStep` quotes the live
`crisis.button` value (`"Need help now"`). `Quiz` kept as `Quiz` in all redo
batches 17-29; Italian `Password` and French `Message` kept; Japanese is polite
(です/ます).

## Commits (local only, never pushed)

Base `3f7d4ba` (crisisStep button match, polite ja, Quiz/Password/Message
nitpicks), then redo batches 1-29:

- `3668feb` batch 1: vi zh hi
- `b77db57` batch 2: fr ar pt
- `6a6dba0` batch 3: bn pa ur
- `11aef0e` batch 4: tl ko fa
- `39933f6` batch 5: ht am my
- `4b39446` batch 6: ne sw so
- `a2b7ac5` batch 7: he de nl
- `d4f88d6` batch 8: ja th lo
- `269713c` batch 9: km ms id
- `55ff041` batch 10: el it tr
- `710c4c8` batch 11: pl uk ro
- `bdeda60` batch 12: cs sk sl
- `f9bf167` batch 13: hr sr bs
- `0a097c7` batch 14: mk bg hu
- `03ca6f6` batch 15: et lv lt
- `c87ef15` batch 16: fi sv da
- `982d009` batch 17: no sq ca
- `6d877d9` batch 18: az bho ceb
- `5bf9223` batch 19: ff gu ha
- `cff7f69` batch 20: hy ig ilo
- `9b9a7b9` batch 21: jv ka kk
- `a50596d` batch 22: kn ku ln
- `1e9810c` batch 23: mg ml mr
- `c36ee6f` batch 24: om prs ps
- `11dfc0d` batch 25: qu rn rw
- `c111b06` batch 26: si sm ta
- `d27a732` batch 27: te ti tw
- `b4ccc94` batch 28: uz wo yi
- `9fefc93` batch 29: yo yue zu
- `c0ca5d0` batch 30 (Nov 3): ru (fresh native Russian from en + es,
  same standard; old file was NLLB output, not Brann's translation)

## English-leftover counts (strings still equal to English, 317 keys each)

Every locale passes: 317-key parity with `en`, no `⁇`, all `{{...}}`
placeholders preserved. Counts below = protected 25 + documented extras:

- 25 (protected only): am ar bn es fa hi ht ko my ne pa so sw ur vi zh
  (+ `en` 317 = source itself)
- 26 (protected + `Quiz`): az bg bho el ff gu ha he hr hu hy id ig jv ka kk
  km kn ku ln lo lt lv mg mk ml mr ms om pl prs ps qu rn ro ru rw si sk sl
  sm ta te ti tr uk uz wo yi yo yue zu
- 27 (protected + `Quiz` + one legitimate loanword): ceb (`Normal`), ilo
  (`Normal`), sq (`Normal`), jv (`Normal`), sv (`Normal`); tl = 27 as
  protected 25 + `Account` + `Password` (tl Quiz is natively translated,
  see review list below)
- 28: pt (`Quiz`, `Tokens`, `Normal`)
- 29: ca (`Quiz`, `Tokens`, `Notes`, `Normal`), fr (`Message`, `Pause`,
  `Notes` — nitpick + identical spellings), it (`Home`, `Account`,
  `Password` — nitpicks + loan)
- 30: no (`Send`, `Pause`, `Tokens`, `Normal` — identical spellings/loan)
- 31: da (`Send`, `Pause`, `Upload`, `Tokens`, `Normal`), de (`Community`,
  `Feature`, `Pause`, `Okay`, `Normal`), nl (`Home`, `Community`, `Feature`,
  `Account`, `Tokens`)

All extras above are identical-spelling words (`Normal`, `Pause`, `Send`,
`Upload`, `Notes`, `Okay`), standard loanwords (`Tokens`, `Quiz`, `Account`,
`Password`), or Brann nitpicks (`Message`, `Password`). No real untranslated
strings remain in any locale.

## Verification (final, this session)

- `backend/.venv/bin/python -m pytest -q`: **140 passed**
- `cd frontend && ./node_modules/.bin/vitest run`: **63 passed (8 files)**
- `npm run build`: **passes**
- Full audit: 90/90 locales parity, no `⁇`, placeholders intact,
  `crisisStep` contains the exact live button name in 88/88 non-baseline
  locales (`en` source has no quotes by design; `ja` uses Japanese corner
  brackets 「」 around the exact button name — flag for reviewer preference),
  no `Test`/`Teste` quiz values, `it` password = `Password`,
  `fr` message = `Message`, `ja` polite form confirmed.

## ru redo verification (Nov 3)

- Fresh native Russian from en + es (`/tmp/redo_ru.py`): 317-key parity,
  no `⁇`, `{{app}}` intact, `reentry.crisisStep` quotes the exact
  `"Need help now"` button name, `phase3.quiz` = `Quiz`, every
  non-protected string contains Cyrillic (Latin only in `{{app}}`,
  `Groundwork`, quoted button name).
- English-equal: **26** (protected-25 + `Quiz`).
- Same gates re-run after the ru redo: backend **140 passed**, frontend
  **63 passed (8 files)**, `npm run build` passes. Committed locally,
  never pushed.

## Typos caught and fixed before commit (batches 18-29)

- Fulfulde step1 French fragment → pure Fulfulde; familyRideHelp stray `h`.
- Gujarati tagline Devanagari danda → period.
- Ilokano Arabic-script contamination (`Mangnayون` → `Mangnayun`, 3x).
- Wolof: `member`/`Member` → native phrasing; `fOF` garbage → `fa`;
  `ku Rescue` → `(réserve)`; `sans telefon` → `te amul telefon`;
  `sans`/`guess`/`retirer`/`impairment`/`Taayal`/`Desit`/`Préparer`/
  `Dorat guy dorat` etc. → native Wolof; 33 fixed to `fanweer ñett`.
- Yiddish Cyrillic `сэйף` → `סייף`; leading-space fix in step15.
- Tigrinya Telugu-script mixing (`చెక్-ఇన్` → `ቼክ-ኢን`), English `never`,
  `posto`, ` virtual` → native.
- Quechua Spanish `Más o menos` → `Masulla`; `coma` → Quechua `koma`.
- Cantonese `routine` → `習慣`, `note` → `註`.
- Pashto Cyrillic `і` → native.
- Twi `fault` → `Asɛnti`; missing steps 32-33 added; inconsistent
  contact terms unified.
- Zulu from/to both `Kuliphi idolobha` → from `Kuvelaphi`.

## For Brann to review

- 17 early-batch locales translate `Quiz` natively (am ar bn es fa hi ht
  ko my ne pa so sw tl ur vi zh): am `ጥያቄዎች`, ar `اختبار`,
  bn `কুইজ`, es `Cuestionario`, fa `آزمونک`, hi `क्विज़`, ht `Tès`,
  ko `퀴즈`, my `ဉာဏ်စမ်း`, ne `प्रश्नोत्तरी`, pa `ਕੁਇਜ਼`, so `Su'aalo`,
  sw `Jaribio`, tl `Pagsusulit`, ur `کوئز`, vi `Câu đố`, zh `小测`.
  None are `Test`/`Teste`; batches 18-30 (incl. ru) use literal `Quiz`.
- `ja` crisisStep quotes the button name in 「」 rather than ASCII quotes.
- `open-questions.md` #9 vs live files: doc says `crisisReply.*` English,
  live files have them translated — needs reviewer reconciliation
  (unchanged by this redo).

## Queued follow-up: other apps (BLOCKED — read-only)

All five folders reject writes (`Read-only file system`, verified by touch
probe; nothing written or deleted there):

- `/workspace/momoempire` (AI Office) — read-only
- `/workspace/momo-academy` (Academy) — read-only
- `/workspace/bk-latest` (Bookkeeping) — read-only
- `/workspace/yee-academy` (YEE) — read-only
- `/workspace/trade-circle-15` (Trade Circle) — read-only

No Young People's Edition repo found (only Young Entrepreneurs Edition at
`/workspace/yee-academy`). No commits, no pushes, no test runs performed in
those repos. Their redo (fresh from en+es sources, batches + tests + counts,
no push) is pending a writable mount.
