# russian gallium

bekh's own Russian layout for the Lily58, built because typing Russian on ЙЦУКЕН next to
Gallium is a "top dance extravaganza": ЙЦУКЕН wants 11–12 columns, so х ъ ж э end up past
the pinky or on a thumb layer, and its index fingers drown in same-finger pairs. The goal
is comfort, not speed, and **shared muscle memory with Gallium**: Cyrillic letters sit on
their Latin twins wherever that's cheap, so the two languages don't fight in his hands.

Lives in `russian-gallium/`. Not installed anywhere yet: the page is the whole product
so far.

## The layout now

Drawn as physical keys (`opt.py` prints the same picture):

```text
                                  ъ
    б л д ш ц     й ж о у , ю
  к н р т с г     п в а е и
    х щ м ч з     ь ф я ы .
             alt+⏎ э
```

Score 269.8 against ЙЦУКЕН's 861 on the same board (lower is better; the units are
made up and only compare layouts). All 12 annealing restarts converge on it, so it's the
optimum under the current pins.

**How bekh chose it, letter by letter** (these are the pins; the optimizer placed the rest):

- **Twins by sound**: т→t, н→n, р→r, **с→s**. с started pinned to Gallium c *by look*;
  unpinned, the optimizer put it on s by itself, −5.7, and bekh took it. While с sat on the
  index top, the index home could only hold a letter that never touches с, and ж got the
  best key on the board.
- **Twins**: м л д п з б г ф а е и о у й on m l d p z b g f a e i o u j. Pinning all of
  them together cost ~30 points out of a 600-point gap to ЙЦУКЕН. Tested and refused:
  р on Gallium p by look (+14 to +20, the most expensive move tried), в on v (+17),
  к on its twin k (+23, "ск" piles onto one finger).
- **`,` and `.`** stay on Gallium's own comma and period keys, same as English.
- **я and ы are swapped against the numbers** (+4.7, "ая"/"оя" land on one finger), by
  feel. Pinned so the optimizer can't undo it.
- **к on the left outer home key** (the `` ` `` / F20 hold-tap). bekh likes that key and the
  pinky stretch costs him nothing, so it's priced like a home key (1.8). The optimizer
  then chose к for it, its best seat by numbers (every other seat +3 to +34). A letter on a
  balanced hold-tap only misfires as F20 when the next key is pressed *and released*
  inside the hold, which normal rolling rarely does.
- **ё is gone.** bekh never types ё, so the corpus counts every ё as е and ё has no key
  (the model parks it on the virtual `chord` seat at zero frequency, undrawn). alt+е
  can't hold it: е sits inside Karabiner's alt numpad block.
- **э on alt+⏎** (left thumb holds Space = alt, right thumb taps Enter): it already lives
  there in his ЙЦУКЕН habit. **ъ on the number-row `]`**, where stock ЙЦУКЕН keeps it too:
  a plain key, no chord, and ъ comes up maybe once a week. Before that it was alt + the ь
  key; a right-thumb chord was out (⌫ is word delete, ⌘ a modifier, F19 caps) and so was
  HEAVEN (held Enter), whose right hand is all arrows.
- **`-` and `=` (the inner bottom keys) stay symbols.** Russian types hyphens all the time
  (что-то, кто-нибудь, по-моему). The thumb chords for э and ъ are what freed them.

## The page

`layout.html`, opened as a local file in bare. The board drawn as the Lily, the score live:

- click two keys to swap, shift-click to pin, hover a key for the letters sharing its finger
- "optimize unpinned" anneals the rest in the browser (~1 s a run, 8 restarts)
- presets: the twin draft (the layout above) and ЙЦУКЕН for comparison
- the typing pad: real subtitle lines, type on the board in either input source, the next
  key glows. alt+⏎ types э.
- state persists in `localStorage["rulayout3"]`; bump the key when a preset changes or the
  page keeps showing the old one

## The machinery

- `ngrams.py stats.npz <files…>`: corpus → unigram, bigram, skipgram and trigram
  frequencies over 35 symbols (33 letters, `,` `.`), each file weighted equally, ё → е.
  Fast (numpy over utf-32), 100 MB in 1.5 s.
- `opt.py pins.json`: the scorer and the annealer. Seats are QWERTY scancodes (what the
  board sends) plus two virtual seats: `alt+⏎` (э) and `chord` (ё's parking spot, never typed). Each seat: hand, finger,
  row, column, effort. The score is effort plus penalties for same-finger bigrams
  (weighted by distance, the heaviest), same-finger skipgrams, index stretches, scissors and
  redirects, minus a bonus for rolls. **The weights in `W` are guesses, not calibrated**: a
  2-point difference is noise, a 600-point one isn't. `pins.json` holds the live pins.
- `score.js`: the same scorer in JS for the page. Parity with Python is exact (checked to
  3 decimals); keep it that way when touching either.
- `build_page.py`: data + `page.tmpl.html` + `score.js` → `layout.html`. The twin preset
  is the `TWIN` string at the top of it (seat, letter pairs). The practice lines come from
  `lines.txt`; pass a subtitles file to resample them.
- `ycuken.py`: scores ЙЦУКЕН as bekh has it on this board.

**The corpus** isn't in the repo; `stats.npz` is. To rebuild it: 40 MB streamed off the top
of OpenSubtitles' Russian mono dump plus Leipzig's 300K-sentence Russian web corpus.
Subtitles because they're the nearest thing to chat (short, spoken, swearing); the web
text so it isn't all movie talk. Classic literature was considered and rejected: it's
Tolstoy describing a field. bekh has no Telegram, and his Mattermost is mostly English.

```bash
curl -sL https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/mono/ru.txt.gz | gunzip | head -c 40000000 > subs.txt
curl -sLO https://downloads.wortschatz-leipzig.de/corpora/rus-ru_web-public_2019_300K.tar.gz && tar xzf rus-ru_web-public_2019_300K.tar.gz
.venv/bin/python ngrams.py stats.npz subs.txt rus-ru_web-public_2019_300K/*-sentences.txt
```

## Gotchas

- **bare eats `a`, `o`, `f`, `F`, `/` (and `g i`)** whenever focus isn't in a text field:
  they're its scroll, tag and find keys. The page's `<body role="textbox">` makes the whole
  page count as one, and the buttons refuse focus on mousedown so focus never leaves
  body. A page also can't focus itself in bare (the focus guard), so anything that needs a
  focused element needs bekh's click.
- **The typing pad reads `e.code`, which is after Karabiner.** Under English input the
  board's scancodes arrive as Gallium; under Russian input they arrive raw. The pad
  remembers which from the last letter typed (Latin or Cyrillic `e.key`), because
  punctuation keys type `.` and `,` in both and can't tell. With alt held, `e.key` is an
  option-symbol, so alt chords assume Gallium.
- **Gallium's punctuation doesn't arrive as its own keycode.** Karabiner's "Gallium
  Colstag" rule sends the physical `,` seat (Gallium `'`) as **`slash`** (shifted:
  `backslash`), `.` as `semicolon`, `/` as `period`, `p` as `comma`. Mapping by the
  Gallium table instead of karabiner.json made the я key type a period. `GALCODE` in
  the template is the real map; letters are fine by the table.
- **alt+⏎ never arrives as alt+Enter.** Karabiner's "Lily58: alt numpad + alt+Enter =
  apostrophe" rule turns it into a bare `quote` keycode with alt stripped, which is how
  RussianWin has always given him э. The pad maps `Quote` to э in both modes; the future
  rule can leave that chord alone. The same rule turns alt + the right-hand block (Gallium
  y o u / h a e / f ' ;) into digits, so no alt chord for a letter can live there.

## Next

1. **bekh is training on the page** and comes back when it feels okay. Feel only gets a
   vote once he can type it; before that, memory (the pins) and math (the rest). Don't
   wait for fluency to build the rule: until it exists he types ЙЦУКЕН everywhere else,
   which fights the new habit, and real chats train faster than subtitles.
2. **The Karabiner rule**: nothing custom gets installed. Keep the stock RussianWin input
   source, and gate a rule on Russian that sends, for each physical key, the key RussianWin
   types our letter on (all 33 letters exist there, shift passes through for capitals). cmd/ctrl
   chords stay out of it so shortcuts keep Gallium. Karabiner reloads instantly, which is
   what iterating needs (a `.keylayout` change needs a logout). alt+⏎ already arrives as
   RussianWin's э key; ъ on `]` is where RussianWin has it, so neither needs a mapping.
   Check how it meets the existing Gallium rules (gated `^en$`) and the spares rule 0
   (`docs/karabiner.md`).
3. Once it stops moving: bake it into a real `.keylayout` with the generator from
   `docs/musings_over_ru_layout.md` (which also solves the cross-language symbols there),
   drop the rule, and give the mini a keyd twin.
