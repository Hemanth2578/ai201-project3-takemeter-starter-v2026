# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Your community, and what your classifier sorts posts into. Three or four
     sentences. -->

TakeMeter sorts short US English-language finance news articles into four
topic labels: `Business`, `Economy`, `Administrative` and `None of These`.
The articles come from the Webz.io news feed, so they are a mix of wire stories, analyst-rating
headlines, local business news, press releases and off-topic pages that the
feed tags as finance.

---

## Label Taxonomy

<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.

     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### What I saw when reading

Three distinctions came up again and again in the first 30 articles, and
each one became a label boundary:

| What I saw in the articles                                                | Boundary it became            |
| ------------------------------------------------------------------------- | ----------------------------- |
| Some articles name a company; others talk about a whole sector or country | `Business` vs `Economy`       |
| Some report a government action; others report its economic effect        | `Administrative` vs `Economy` |
| Some aren't finance news at all (sports, elections, gardening)            | `None of These` vs the rest   |

### Why topic, not quality

Sorting these articles by quality doesn't work. A news article reports what
happened and what its effects are, in a neutral reporting voice, so under a
quality taxonomy like analysis / hot take / reaction almost every article
would land in one label, with analysis only rarely. That breaks the 70% cap
and gives the model nothing to learn. What actually varies from article to
article is what it is about, so the labels sort by topic.

### `Business`

**Definition:** News about companies or businesses, including transactions,
restructuring, mergers, credit ratings, analyst ratings, stock forecasts, and
financial fraud involving companies or money, plus market-trading news (stock,
commodity-futures and crypto price moves).

**Example 1:**

> Crédit Agricole Agrees to Buy German Bank IKB. Crédit Agricole agreed to buy
> the German bank IKB Deutsche Industriebank AG as part of its expansion push
> in Germany.

**Example 2:**

> Whit's Frozen Custard announces closure of downtown Ashland location. A
> business in downtown Ashland announced it will be permanently closing.

### `Economy`

**Definition:** News about real-world economic conditions of a country, state,
or the world: supply and production, trade, jobs, wages, cost of living and
inflation.

**Example 1:**

> Hormuz clogging stop 6-7 million bpd of oil from reaching markets. About 6-7
> million barrels per day of oil does not reach the world markets through the
> Strait of Hormuz creating an imbalance between supply and demand.

**Example 2:**

> The Rising Cost Of Water. A new report finds that over the past 10 years, the
> cost of household drinking water increased faster than the cost of
> groceries, faster than inflation, and faster than household income.

### `Administrative`

**Definition:** Actions or measures taken by an agency — a government office
or public official, a nonprofit, a community organization, or an HOA.

**Example 1:**

> West Virginia - Price Optimization. The West Virginia Office of the Insurance
> Commissioner published a bulletin informing insurers that the use of price
> optimization is unfairly discriminatory and in violation of state law.

**Example 2:**

> Fort Bragg council to vote on emergency fix for broken Noyo water line. City
> staff will ask the Fort Bragg City Council to declare an emergency so the
> city can drill a new water pipe under the Noyo River before winter storms.

### `None of These`

**Definition:** An article that reports no company news, no economic
conditions and no agency action — which covers elections and campaigns
(candidates, parties, PACs, debates, campaign ads), stories about one
individual (a lottery winner, an athlete's opinion), and non-finance topics
(sports, entertainment, gardening, software alerts, ads, listings, or pages
with no article in them).

Campaign groups, parties and PACs are not agencies, so their spending or ads
stay `None of These`. An official acting _in office_ is an agency action and
goes to `Administrative`.

**Example 1:**

> Houston resident bought winning $1M Powerball ticket near Aldine.

**Example 2:**

> Former All-Star Calls Potential Brewers/Rays World Series 'Terrible' for MLB.

### Known limitation of these labels

The labels are broad topics, so one label can cover articles that tell a
reader very different things. A stock-rating headline ("Palantir Stocks Slip
Despite Barclays' $265 AI Target") and a local opening ("Dutch Bros Coffee
nears opening in southwest Fort Wayne") are both `Business`, but they are
miles apart in what they convey. `Business` got broader still when
`Financial Fraud` (5 rows) and `Credit Rating and Forecasts` (40 rows) were
merged into it to reach four labels.

### The hardest boundary

**Which two labels:** `Economy` vs `Administrative`. Government actions such
as road works, water lines and public housing often have an economic side
without saying anything about the economy itself.

**The decision rule I used every time:**

<!-- e.g. "If the post names a specific checkable fact, it's `analysis`, even
     if the tone is heated." -->

If the article says an agency is taking an action, it is `Administrative` —
always, even if the article also says the economy improves because of it. An
agency means a government office or public official, a nonprofit, a community
organization, or an HOA. The economic effect only decides the label when no
agency action is reported.

**What counts as an action:** a step an agency takes to make amendments,
resolve an issue, or address a concern — passing, approving, restricting,
funding, ordering, or launching something for that purpose. These are _not_
actions:

- A view or preference. "Fed's Hammack … favors more restrictive policy" is a
  suggestion until a decision is taken, so it stays `Economy`.
- Describing a situation. Russia's Deputy PM Novak describing oil stuck at
  Hormuz, with no step taken to fix it, stays `Economy`.
- Describing how policies play politically. "How Trump's economic policies are
  giving Democrats a new…" is campaign politics, so `None of These`.
- Announcing someone else's action. "Town of Vinton announces plans for
  Wawa": the town only says Wawa is coming; the action is a new business
  opening, so `Business`.
- A meeting. "Security Council Meets on UN Verification Mission in Colombia"
  reports a meeting, not a decision, so `None of These`.
- A demand or an endorsement. "Republican, Democratic senators call on Trump
  to end diesel deal" and the League of Women Voters supporting a library tax
  levy ask for a step without taking one, so both are `Economy`.
- Reporting activity. "Gateway Development reports busy pipeline" lists site
  visits and proposals, not a step to fix anything, so `Economy`.
- A proposed ballot measure. Voters haven't acted yet, so it is labelled by
  what it is about: Prop 45 (deadlines for housing, water and energy
  projects) is `Economy`; Oklahoma State Question 845 (how the judicial
  nominating commission is formed) is `None of These`.
- An award, or a notice that a body was formed. A bicycle-friendly award to a
  company's office is `None of These`; a notice of incorporation is
  `Business`.

**These _are_ actions:**

- Acting on fraud or wrongdoing. When a regulator fines a company, a sheriff
  arrests a suspect, or a court orders a party, it is `Administrative`, even
  though `Business` covers fraud. Fraud news with no agency acting (a law
  firm's class-action notice, an allegation, a report) stays `Business`.
- Deciding to keep something unchanged, when the decision is made to address
  a concern. A central bank holding interest rates to fight inflation is
  `Administrative`.

### Second boundary: `Business` vs `Economy`

**The decision rule:** if one or more _named_ companies are at the centre of
the article — their deal, results, rating, stock move, product, opening or
closing — it is `Business`, even when the article also talks about the wider
economy. Market-trading news is `Business` too, even with no company named:
stock, commodity-futures and crypto price moves, sector stock updates, and
market forecasts. `Economy` is for real-world conditions in a country, state
or the world: supply and production, trade, jobs, wages, cost of living and
inflation.

"Harlow Steel cuts 900 jobs as the regional construction slowdown deepens" is
`Business`: the layoffs are the event, and the slowdown is context. "Retail
sales at the five largest US grocery chains fell 2%" is `Economy`: no company
is named, and the subject is the sector.

### Decision order

Apply the rules in this order and stop at the first one that fits:

1. An agency takes an action → `Administrative`
2. Named companies are at the centre, or it is market-trading news → `Business`
3. Real-world economic conditions of a country, state or the world → `Economy`
4. Otherwise → `None of These`

---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:** 227 articles pulled from the Webz.io news API
(`language:english`, `thread.country:US`), all published 6–12 October 2026. A cleaning script built each row
as headline + body, stripped scraper boilerplate (paywall stubs, "read full
story" tails, risk warnings, menus), and dropped 4 rows: 2 spam link pages
and 2 duplicate stories. 34 of the remaining 223 are headline only, because
the body was empty, an ID number, or a paywall.

**How I labelled them:** <!-- Cold first? Pre-labelled with AI and corrected?
Say so plainly — the disclosure is required, not penalised. -->
First I decided on the labels and wrote a definition for each. Using only
those definitions, I labelled the first 30 rows cold, by myself, with no help
(`note` = `cold`). I then gave an AI my definitions and my 30 cold labels as
examples and had it pre-label the remaining 193 rows. I read every one of
those 193 labels myself (`note` = `pre-labelled by AI, checked`).

While writing the decision rules, I reviewed the labels against them with AI
help: it listed rows that conflicted with a rule, and I decided each one. 16
rows changed label this way, and each is marked in `note` as `relabelled X ->
Y under revised rule`. One of them is a cold row: "Chinese national accused of
$1M nationwide fraud scheme arrested in Michigan" was my cold `Fraud` label
(merged into `Business`) and became `Administrative` once I decided that an
agency acting on fraud is `Administrative`.

**Counts per label:**

| Label            | Count | Share |
| ---------------- | ----- | ----- |
| `Business`       | 132   | 59%   |
| `None of These`  | 35    | 16%   |
| `Economy`        | 30    | 13%   |
| `Administrative` | 26    | 12%   |
| **Total**        | 223   | 100%  |

**Three hard cases**

<!-- Any post that made you pause: what it was, which two labels it could have
     been, and what you chose. These are worth more than the easy 190. -->

**1.**

> _The post:_ "Global Hygiene Products Market in 2025 Highlights Key Trends,
> Market Size, and Regional Developments. Xiamen, Fujian, China — Overall
> Market Size: According to multiple industry research firms, the global
> disposable hygiene products market generated approximately RMB 260 billion
> (about 36 billion USD) in revenue in 2024…"
>
> _Could have been:_ `Business` or `Economy`
>
> _I chose, because:_ `Business`. It reads like a global, industry-wide
> figure, which points to `Economy`, but the main point of the article is the
> business market for these products in 2025: its size, trends and regions,
> put out from a company's side. It is not about the economic conditions of a
> country or the world (jobs, prices people pay, trade, inflation).

**2.**

> _The post:_ "The 2026 Paris Auto Show. By Nick Carey and Giulio Piovaccari
> PARIS, Oct 12 (Reuters) — Europe's car industry fought back against rising
> Chinese competition at the Paris car show on Monday with a wave of new model
> launches and…"
>
> _Could have been:_ `Business` or `Economy`
>
> _I chose, because:_ `Business`. It talks about a whole industry, which
> points to `Economy`, but what it reports is competition in the car market:
> European carmakers launching new models against Chinese ones. That is
> companies competing for customers, not the state of an economy. There is
> nothing in it about jobs, trade, prices or growth.

Both are hard because my Business vs Economy rule doesn't settle them on its
own: neither names a company at the centre, and neither is market-trading
news, yet both cover a whole industry. I decided by asking what the article
reports. Companies' products, sales and competition make it `Business`; only
the conditions of an economy (jobs, trade, prices, inflation) make it
`Economy`.

**3.**

> _The post:_ "Gateway Development reports busy pipeline, cites housing push.
> Gateway Development Corporation Executive Director Mike Rooks said the
> organization has hosted three site visits, received six new requests for
> proposals and had several properties close in the last …"
>
> _Could have been:_ `Administrative` or `Economy`
>
> _I chose, because:_ `Economy`. My first call was `Administrative`: a
> development agency pushing to get properties sold reads like an agency
> taking action, and the economic side (new jobs, more people for stores, gas
> stations and schools) is only a knock-on effect, which my rule says never
> decides the label. But when I pinned down what counts as an action — a step
> taken to make amendments, resolve an issue or address a concern — this
> article didn't meet it. It only reports activity: site visits, requests for
> proposals and property sales. No step to fix anything is described, so it
> falls back to `Economy`. This is the case that made me write the
> definition of an action.

---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:** `distilbert-base-uncased`, trained on an NVIDIA GeForce RTX
5070 Laptop GPU (CUDA).

**Settings:** <!-- epochs, learning rate, batch size, seed -->
3 epochs, learning rate 2e-5, batch size 16, max 128 tokens per post, seed 42.

**Anything I changed from the defaults, and why:** Nothing. Only `LABELS`
was set to my four labels: `Business`, `Economy`, `Administrative`,
`None of These`.

**Split sizes:** <!-- train / val / test, and per-label counts in the test
split. If a label had fewer than about 8 in test, say so — it explains a lot
of next unit's variance. -->
train 155 · val 34 · test 34.

| Label            | In the test split |
| ---------------- | ----------------- |
| `Business`       | 20                |
| `None of These`  | 5                 |
| `Economy`        | 5                 |
| `Administrative` | 4                 |

Three of my four labels have fewer than 8 test examples (`Economy` 5,
`None of These` 5, `Administrative` 4), so their scores will move a lot
between seeds.

---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- _What I asked for:_ To label the news articles based on my definitions and
  my 30 cold-labelled posts.
- _What came back:_ It pre-labelled every remaining article. I read each and
  every one of them and found discrepancies, which showed me my label
  definitions were ambiguous (for example, what counts as an "agency" and
  what counts as an "action").
- _What I changed:_ I rewrote the definitions, then had the labels checked
  against the new definitions. The AI listed the rows that conflicted with
  them, and I decided each one myself. 16 rows changed label, including one
  of my cold rows (the Michigan fraud arrest).

**Moment 2**

- _What I asked for:_ Eight example news posts sitting on my label
  boundaries, for me to label as a stress test.
- _What came back:_ It gave me the eight posts. I labelled them myself, and it
  checked my labels against my own written rules. Three didn't match what my
  rules said, or made me hesitate: a steel company's layoffs, a regulator
  fining an insurer, and a central bank holding interest rates.
- _What I changed:_ I didn't change my labels. I refined the definitions
  instead: an agency acting on fraud is `Administrative`, holding rates to
  fight inflation counts as an action, and I wrote a rule for `Business` vs
  `Economy`.

**Moment 3 (unit 6): choosing the number of epochs**

- _What I asked for:_ Help picking the one improvement for Milestone 5 and
  carrying it out.
- _What came back:_ It went through the three options against my diagnosis.
  Relabelling was ruled out because my agreement checks (30/30 with staff,
  20/20 with an independent labeller) found no boundary I had applied two
  ways, and adding 30 posts would need new labelling. That left one training
  setting. It pointed at my "before" training log: loss was still falling at
  epoch 3 (about 1.30 → 1.07 in every seed) while the learning rate had
  decayed to almost zero, so 3 epochs (30 steps) stopped the model before it
  learned anything beyond guessing `Business`. It suggested 10 epochs (100
  steps), and said to fix that number before seeing any results, so I
  wouldn't be tuning against the test set.
- _What I changed:_ I made only that one change, `EPOCHS` 3 → 10, and kept
  everything else the same, including the three seeds. I did not try other
  epoch values after seeing the results. It also helped me spot patterns in
  my errors afterwards — that `None of These` became the weakest label and
  that its posts were being called `Administrative` — which is what my
  What's Still Broken section is built on.

**Pre-labelling disclosure:** 193 of 223 rows were pre-labelled by an AI,
given my definitions and my 30 cold labels as examples. I read every one of
them, and they are marked `pre-labelled by AI, checked` in the `note` column. 16 rows were later relabelled after
an AI-assisted check against my decision rules, with every final label
decided by me; those rows say so in `note`.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

I ran the baseline twice on the same 34 held-out posts: once with my label
definitions (`label_definitions.txt`, the default) and once with the bare
label names only.

**Baseline with my definitions** (`baseline_results.json`):

| Measure               | Baseline | Trained | Difference |
| --------------------- | -------- | ------- | ---------- |
| Overall accuracy      | 0.147    | 0.588   | +0.441     |
| Macro F1              | 0.079    | 0.185   | +0.106     |
| F1 — `Administrative` | 0.222    | 0.000   | -0.222     |
| F1 — `Business`       | 0.095    | 0.741   | +0.646     |
| F1 — `Economy`        | 0.000    | 0.000   | +0.000     |
| F1 — `None of These`  | 0.000    | 0.000   | +0.000     |

**Baseline with bare label names** (`baseline_results_bare.json`):

| Measure               | Baseline | Trained | Difference |
| --------------------- | -------- | ------- | ---------- |
| Overall accuracy      | 0.735    | 0.588   | -0.147     |
| Macro F1              | 0.483    | 0.185   | -0.297     |
| F1 — `Administrative` | 0.333    | 0.000   | -0.333     |
| F1 — `Business`       | 0.870    | 0.741   | -0.129     |
| F1 — `Economy`        | 0.727    | 0.000   | -0.727     |
| F1 — `None of These`  | 0.000    | 0.000   | +0.000     |

The gap between the two baseline runs is what my definitions were worth to
the zero-shot model: 0.147 − 0.735 = **−0.588** accuracy.

**What I predicted before I looked:**

<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

I expect my trained model to beat the baseline on the `Economy` vs
`Administrative` labels, as this is the hard case in my data, and also to
perform very well on labelling the `Business` posts.

**What the gap actually means:**

<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->

The baseline with my definitions did worse than my trained model, whereas
the baseline with bare label names fared better than my trained model. This
means either my labels are not good and/or the current training method is
not up to the mark.

My prediction was half right. On `Business` the trained model beat the
definitions baseline (0.741 vs 0.095) but lost to the bare-names baseline
(0.741 vs 0.870). On `Economy` and `Administrative` it was wrong: the trained
model scored 0.000 on both, while the definitions baseline found all 4
`Administrative` posts (F1 0.222) and the bare-names baseline scored 0.333 on
`Administrative` and 0.727 on `Economy`.

With my definitions, the baseline labelled 32 of 34 posts `Administrative`,
including 19 of 20 `Business` posts and all 5 `Economy` posts. Reviewing
`baseline_results.json`, some of these are genuine boundary cases (e.g.
"NOTICE OF INCORPORATION OF HOUSING AUTHORITY OF THE VILLAGE OF DECATUR" or
"Rosen Law Firm Encourages Barclays PLC Investors to Inquire About Securities
Class Action"), but others have no agency in them at all (e.g. "HCLTech
Reports Strong Q2; Deal Bookings $3.3B" or "Freddy's Frozen Custard &
Steakburgers Opens 600th Restaurant"). My `Administrative` definition starts
"Actions or measures taken by an agency…", and almost every news story
describes someone taking an action. The definition doesn't say that a
company's action is excluded, and "agency" is stretched to cover nonprofits
and community organizations, so the zero-shot model matched it to companies
opening, buying and reporting results too. So the ambiguity is in how my
`Administrative` definition is worded: it is broad enough to cover almost any
article.

With bare label names, the same model got 0.735 accuracy and 0.727 `Economy`
F1, so the four categories themselves can be told apart. The problem the
definitions run shows is in the wording of my definitions, not in the
categories.

My trained model predicted `Business` for all 34 posts, so the gap with the
baselines is mainly a training problem: it learned to guess the majority
label (59% of my data) instead of learning my categories.

---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
| --------- | ------ | ------- | ------ | --------- | ------- |
| 1. `Administrative` F1 | ≥ 0.60 | 0.000 | 0.000 | 0.000 | MISSED |
| 2. Overall accuracy | ≥ 0.65 | 0.588 | 0.588 | 0.588 | MISSED |
| 3. Independent labeller agreement on 20 cold rows (revised — see `criteria.md`) | ≥ 70% (14 of 20) | 20 of 20 (100%) — one check, not per seed | — | — | MET |
| 4. Every label's recall | ≥ 0.60 | 0.000 (lowest) | 0.000 (lowest) | 0.000 (lowest) | MISSED |
| 5. Largest share predicted as one label | ≤ 59% | 100% `Business` | 100% `Business` | 100% `Business` | MISSED |

**Three seeds** (`results_three_seeds_before.json`, 34 test posts each:
20 `Business`, 5 `Economy`, 5 `None of These`, 4 `Administrative`):

| Measure               | Seed 42 | Seed 7 | Seed 2024 |
| --------------------- | ------- | ------ | --------- |
| Accuracy              | 0.588   | 0.588  | 0.588     |
| Macro F1              | 0.185   | 0.185  | 0.185     |
| F1 — `Business`       | 0.741   | 0.741  | 0.741     |
| F1 — `Economy`        | 0.000   | 0.000  | 0.000     |
| F1 — `Administrative` | 0.000   | 0.000  | 0.000     |
| F1 — `None of These`  | 0.000   | 0.000  | 0.000     |

**Spread across seeds:** 0 points. Accuracy was 0.588 in every seed.

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

Identical in all three seeds.

| true \ predicted     | `Business` | `Economy` | `Administrative` | `None of These` |
| -------------------- | ---------- | --------- | ---------------- | --------------- |
| **`Business`**       | 20         | 0         | 0                | 0               |
| **`Economy`**        | 5          | 0         | 0                | 0               |
| **`Administrative`** | 4          | 0         | 0                | 0               |
| **`None of These`**  | 5          | 0         | 0                | 0               |

**My biggest off-diagonal number, and what it means:**

<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->

My biggest off-diagonal numbers are 5 (`Economy` → `Business`) and 5
(`None of These` → `Business`), plus 4 `Administrative` → `Business`, and
nothing went the other way. The model didn't learn any boundary; it learned
to predict `Business` for everything, because about 60% of my training data
is `Business`, so always answering `Business` was the easiest way for it to
be right most of the time.

---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| #   | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1   | `Administrative` F1 | ≥ 0.60 | MISSED | 0.000 in all three seeds; the model never predicted `Administrative` |
| 2   | Overall accuracy | ≥ 0.65 | MISSED | 0.588 in all three seeds, below 0.65 every time |
| 3   | Independent labeller agreement on 20 cold rows (revised) | ≥ 70% (14 of 20) | MET | A fresh AI agent with only my README definitions and rules labelled my first 20 cold rows and agreed on 20 of 20 (`independent_label_check.json`) |
| 4   | Every label's recall | ≥ 0.60 | MISSED | `Business` 1.000, but `Economy`, `Administrative` and `None of These` 0.000 in every seed |
| 5   | Largest share predicted as one label | ≤ 59% | MISSED | `Business` was predicted for 34 of 34 test posts (100%) in every seed |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->

All four misses (criteria 1, 2, 4 and 5) come from one behaviour: in every
seed the model predicted `Business` for all 34 test posts. So I diagnose the
cause once, then show how each miss follows from it.

**The cause: too few examples for my small labels, in a lopsided dataset,
with a very short training run. This is a data and model problem, not a
labelling one.**

How I know, cause by cause:

- **Too few examples for a label — yes.** Of about 155 training rows, roughly
  92 are `Business` and only about 18 `Administrative`, 21 `Economy` and 24
  `None of These`. With 59% of the data in one label, always answering
  `Business` was the easiest way for the model to be right most of the time,
  and it never learned anything else.
- **A boundary I labelled inconsistently — no.** My agreement report is 30/30
  with staff: I applied written rules the same way every time, including the
  ambiguous posts with a number in them. If I had applied a boundary two
  different ways in my own 223 labels, I would expect errors between the two
  labels on that boundary. My confusion matrix shows none. One caveat: the staff set tests
  how I apply someone else's rules, and 16 of my own rows changed when I
  rewrote my rules, so my labels are consistent with my final rules, not
  necessarily with my first ones.
- **A genuinely hard label pair — no.** A hard pair would show up as errors
  between those two labels, for example `Economy` posts called
  `Administrative`. My confusion matrix has zero errors between any of the
  three smaller labels. Every error goes into `Business`, so the model never
  got as far as the `Economy` vs `Administrative` boundary.
- **A task the model can't reach from this much data — partly.** The task
  itself is learnable: the zero-shot baseline with bare label names got
  0.735 accuracy and 0.727 `Economy` F1 without any training. But my
  fine-tuned model had about 155 training rows and only 30 training steps
  (155 rows ÷ batch 16, × 3 epochs). That was not enough to move it past
  guessing the majority label.

The three seeds were identical (0.588 accuracy each time), so this is a
consistent behaviour, not noise from one unlucky split.

How each miss follows:

1. **`Administrative` F1 0.000 (target ≥ 0.60).** `Administrative` is my
   smallest label (about 18 training rows, 4 test posts). All 4 test posts
   were called `Business`.
2. **Accuracy 0.588 (target ≥ 0.65).** 0.588 is exactly the share of
   `Business` posts in the test split (20 of 34): the score of a model that
   always guesses `Business`, which is the floor I set this target against.
3. **Independent labeller agreement — MET, 20 of 20.** I had no classmate,
   so I revised the labeller (not the 70% target) in `criteria.md`: a fresh
   AI agent that had never seen my labels got only my README definitions and
   rules and labelled my first 20 cold rows. It agreed with me on all 20.
   This is weaker evidence than it looks: 15 of the 20 are `Business`, many
   of them easy analyst-rating headlines; two of my rules were written from
   these exact rows (the fraud-arrest rule from row 1, "a notice of
   incorporation is `Business`" from row 6); and an AI applies my rules
   literally, where a person might not. What it does show is that my written
   rules are specific enough for a reader with no other context to reach my
   labels, which supports the conclusion above that the misses are not a
   labelling problem.
4. **Every label's recall (target ≥ 0.60).** `Business` recall was 1.000; the
   other three were 0.000, because none of their posts was ever predicted.
5. **Largest predicted share 100% (target ≤ 59%).** This is the failure this
   criterion was written to catch: the model defaulted to the majority label
   for every post.

---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** **30 / 30 = 100%**

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

None. I matched staff on all 30 posts, so there is nothing to adjudicate or
sort into piles.

**What the pattern in my disagreements tells me:**

With no disagreements, the question is whether the set was easy or the rules
are tight. I think it is both.

The set was easy in places. The posts arrive grouped by label (sp_001–010
are all `analysis`, sp_011–020 all `hot_take`, sp_021–030 all `reaction`),
so the order alone could cue the labels. sp_014 ("Times are down about 3%
since the shoe rules changed, so obviously the shoes are the whole story") is
close to the taxonomy's own worked example under rule 1. And the three
labels look very different on the page: `analysis` posts cite splits and
percentages, `hot_take` posts are one-line claims, and `reaction` posts are
first-person and in the moment.

The rules are also tight where it matters. Staff say several posts were
picked because they are ambiguous, and rule 1 ("does the fact carry the
argument?") settles the ones with a number in them. sp_014 has a statistic
but the statistic is decoration, so it is `hot_take`. sp_011 has "once a
month", but that is a threshold the writer chose, not evidence, so it is
`hot_take` too.

What this says about my own 223 labels: I can apply clear written rules
consistently. My own taxonomy only reached that level of clarity after I
rewrote its rules (what counts as an agency, what counts as an action, the
`Business` vs `Economy` rule), and 16 rows changed label as a result. So my
own labels are consistent with the final rules, but they weren't with the
first version of my definitions.

---

## The Improvement

**What I changed:** One training setting: `EPOCHS` from 3 to **10**. Nothing
else changed — same `labels.csv`, same base model, learning rate 2e-5,
batch size 16, 128 tokens, and the same three seeds (42, 7, 2024), so the
same three splits. `RUN_LABEL` was set to `"after"`, and the results are in
`results_three_seeds_after.json`. I picked 10 before seeing any "after"
numbers and did not try other values, so I wasn't tuning against the test
set.

**Which diagnosis pointed at it:** My diagnosis named a training run that was
too short: 155 rows at batch 16 for 3 epochs is only 30 training steps. In
the "before" run, training loss was still falling at epoch 3 (about 1.30 →
1.07 in every seed) while the learning rate had decayed to almost zero, so
the model stopped before it learned anything beyond guessing `Business`. My
agreement checks (30/30 with staff, 20/20 with an independent labeller)
ruled out relabelling a boundary, so a training setting was the change the
diagnosis pointed at. 10 epochs gives 100 training steps instead of 30.

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
| --------- | ------ | ------- | ------ | --------- | ------- |
| 1. `Administrative` F1 | ≥ 0.60 | 0.800 | 0.500 | 0.571 | MISSED |
| 2. Overall accuracy | ≥ 0.65 | 0.882 | 0.853 | 0.794 | MET |
| 3. Independent labeller agreement on 20 cold rows (revised) | ≥ 70% (14 of 20) | 20 of 20 (100%) — one check, not per seed | — | — | MET |
| 4. Every label's recall | ≥ 0.60 | 0.400 (`None of These`) | 0.500 (`Administrative`) | 0.200 (`None of These`) | MISSED |
| 5. Largest share predicted as one label | ≤ 59% | 59% `Business` (20 of 34) | 65% `Business` (22 of 34) | 71% `Business` (24 of 34) | MISSED |

**Three seeds, after:**

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.882 | 0.853 | 0.794 | 0.088 |
| Macro F1 | 0.812 | 0.751 | 0.635 | 0.177 |
| F1 — `Business` | 0.950 | 0.952 | 0.909 | 0.043 |
| F1 — `Economy` | 1.000 | 0.800 | 0.727 | 0.273 |
| F1 — `Administrative` | 0.800 | 0.500 | 0.571 | 0.300 |
| F1 — `None of These` | 0.500 | 0.750 | 0.333 | 0.417 |

**Confusion matrix, after (seed 42):**

| true \ predicted | `Business` | `Economy` | `Administrative` | `None of These` |
|---|---|---|---|---|
| **`Business`** | 19 | 0 | 0 | 1 |
| **`Economy`** | 0 | 5 | 0 | 0 |
| **`Administrative`** | 0 | 0 | 4 | 0 |
| **`None of These`** | 1 | 0 | 2 | 2 |

**Before vs after, side by side:**

| Measure | Before (3 epochs) | After (10 epochs) |
|---|---|---|
| Accuracy (seeds 42 / 7 / 2024) | 0.588 / 0.588 / 0.588 | 0.882 / 0.853 / 0.794 |
| Macro F1 | 0.185 / 0.185 / 0.185 | 0.812 / 0.751 / 0.635 |
| Labels the model ever predicts | `Business` only | all four |
| Criteria met (of 5) | 1 (criterion 3) | 2 (criteria 2 and 3) |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->

Yes, it helped a lot, and it confirms the diagnosis. With the same data and
the same splits, the only change — more training steps — took accuracy from
0.588 in every seed to 0.794–0.882, and macro F1 from 0.185 to 0.635–0.812.
The model stopped predicting `Business` for everything: in seed 42 it found
all 5 `Economy` posts and all 4 `Administrative` posts. Criterion 2
(accuracy) moved from MISSED to MET. All three seeds now also beat the
bare-names baseline (0.735 accuracy, 0.483 macro F1), which the "before"
model did not.

It did not fix everything. Criteria 1, 4 and 5 are still MISSED, because
each has to hold in all three seeds: `Administrative` F1 cleared 0.60 in seed
42 (0.800) but not in seeds 7 and 2024; the predicted `Business` share was
within 59% only in seed 42. `None of These` is now my weakest label (recall
0.20–0.60), and in seed 42 two of its posts were called `Administrative`.

The spread also got bigger: accuracy now moves 0.088 across seeds and
`None of These` F1 moves 0.417. Before, the spread was 0 only because the
model gave the same answer every time. Now that it is actually learning the
small labels, their 4–5 test posts per split make their scores jump between
seeds — the thin-label effect the notebook warned about in unit 5.

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->

After the 10-epoch run, three criteria are still missed. Each one passed in
at least one seed but not in all three.

**1. `Administrative` F1 ≥ 0.60 — missed (0.800, 0.500, 0.571).**
*What I'd do:* add about 30 more `Administrative` articles, labelled with the
same agency-action rule. With only 26 rows, each split has about 18 to train
on and 4 to test on, so one wrong post moves its F1 by about 0.2, and the
seeds disagree.
*Why I stopped:* the milestone allows one change, and I wanted the epochs
change measured on its own. Adding data at the same time would have made it
impossible to tell which change did what.

**4. Every label's recall ≥ 0.60 — missed (lowest 0.400, 0.500, 0.200).**
*What I'd do:* fix `None of These`, which is now my weakest label (recall
0.20–0.60). It is the only label defined by what it isn't, so its 35 rows
(sports, elections, gardening, software alerts) share nothing a model can
learn. I would either give it a positive definition or split out its
biggest group, elections and campaigns, which is where it collides with
`Administrative`.
*Why I stopped:* that is a relabelling of a whole label, a second change on
top of the epochs one, and it means re-checking 35 rows by hand.

**5. Largest share predicted as one label ≤ 59% — missed (59%, 65%, 71%).**
*What I'd do:* reduce the pull toward `Business`, either with class weights
in training or with more posts in the three smaller labels. Seed 2024
predicted `Business` for 24 of 34 posts, including 2 `Administrative` and 1
`Economy` post.
*Why I stopped:* class weights mean changing the training code, not just a
setting, and more data is the same change as criterion 1. One change was the
limit.

The common thread: all three are about my small labels having only 4–5 test
posts per split. That is also why accuracy now moves 0.088 across seeds. A
larger dataset would help every one of them, and is the single change I'd
make next.

**The gap between what I meant my labels to capture and what the model
learned:**

<!-- Two sentences. Your confusion matrix is the evidence. -->

I meant `Administrative` to capture a rule — an agency *taking an action* to
fix something — but the model seems to have learned a topic instead: in seed
42, 2 of the 5 `None of These` posts were called `Administrative`, which
fits a model reacting to government and election words rather than to
whether an action was taken. And `None of These` never became a category of
its own for the model: across the three seeds its posts were scattered into
`Business`, `Economy` and `Administrative`, because "everything else" gave it
no shared signal to learn.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

---

## Capstone

Everything below this heading is the capstone unit. The sections above are
units 5 and 6 and are left as they were.

**The Shape**

*System:* TakeMeter (project 3), the fine-tuned DistilBERT that sorts finance
news articles into `Business`, `Economy`, `Administrative` and
`None of These`.

*Shape:* **C — extend one capability.**

*What I'm adding:* a way to classify an article the model has never seen.
Until now TakeMeter only existed inside `takemeter.ipynb`: it trained, scored
its own 34 held-out posts, wrote `results.json`, and then the model was
thrown away (`save_strategy="no"`, and `takemeter_out/` is empty). There was
no way to hand it a new article and get a label back. The extension is one
endpoint, `POST /classify`: send it `{"text": "..."}` and it returns one of my
four labels with the model's confidence. To make that possible the seed-42
model has to be saved to disk once (`train.py`), and the endpoint loads it
from there. Every request, good or bad, is written to a structured log.

*Run path:* **Path B — local with logs.** The system loads a 268 MB model and
PyTorch, which does not fit in the 512 MB of the free hosting tier.

*What is out of scope:*

- **I'm not retraining to fix my three missed criteria from unit 6.** No new
  articles, no class weights, no extra epochs. The endpoint serves the same
  seed-42, 10-epoch model that `results.json` describes, weaknesses included
  (`None of These` recall 0.40).
- **I'm not touching the taxonomy.** No fifth label, no splitting elections
  out of `None of These`, no relabelling. `labels.csv` does not change.
- **I'm not building an interface or a batch mode.** One article per
  request, JSON in and JSON out. No web page, no CSV upload, no
  authentication.

*Size check:* three small files (`train.py`, `classify.py`, `serve.py`) that
reuse the notebook's own split and training code. No new dependencies.

**Instrumentation**

Every request the endpoint answers writes one record to
`logs/classify.jsonl`, one JSON object per line. The record is built in
`Handler._new_record` and written by `Handler._finish` in `serve.py`, which
calls `RunLog.write` in `runlog.py`. The server also writes a `startup`
record when it starts, or fails to, and a `shutdown` record when it is
stopped with Ctrl+C.

| Field | What it holds |
|---|---|
| `ts` | When the request arrived, ISO-8601 UTC, to the millisecond |
| `request_id` | Also sent back to the caller, so a response can be matched to its record |
| `status`, `http_status` | `ok`, `rejected` (the caller's mistake) or `error` (the model failed), and the HTTP code sent |
| `input_chars`, `input_preview` | What came in: the length of the text and its first 160 characters |
| `n_tokens`, `truncated` | How long the text was in tokens, and whether it was cut to the model's 128 |
| `label`, `confidence`, `scores` | What came out |
| `tokenize_ms`, `model_ms`, `duration_ms` | How long it took: the two stages, and the whole request |
| `error` | Why it was rejected or failed; `null` when it was classified |

`python runlog.py` reads the file back as counts and timings, so questions
like "how many were rejected" or "how slow was the slowest" need no new code.

The entries below are from one real session on 11 November 2026 (the
timestamps are UTC, so they read 12 November). The full 25-record log is
committed as `logs/classify.jsonl`.

*The server starting:*

```json
{"ts": "2026-11-12T00:55:53.922+00:00", "event": "startup", "host": "127.0.0.1", "port": 8000, "status": "ok", "device": "cuda", "labels": ["Business", "Economy", "Administrative", "None of These"], "max_length": 128, "model_seed": 42, "model_trained_at": "2026-11-12T00:44:50+00:00", "model_load_ms": 4760.0, "error": null}
```

*Ten classified requests.* These are the first ten posts in
`test_split.csv`, sent with `python send.py --held-out 10`:

```json
{"ts": "2026-11-12T00:55:54.458+00:00", "request_id": "b0d20328d76a", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 240, "input_preview": "Bitcoin Miner Fees Fall to Just 0.64% of Revenue, Analyst Says. Transaction fees averaged just 0.64% of Bitcoin miner revenue in the last 30 days, according to ", "n_tokens": 67, "truncated": false, "label": "Business", "confidence": 0.9269, "scores": {"Business": 0.9269, "Economy": 0.0222, "Administrative": 0.0193, "None of These": 0.0316}, "tokenize_ms": 2.69, "model_ms": 215.43, "duration_ms": 218.23, "error": null}
{"ts": "2026-11-12T00:55:54.693+00:00", "request_id": "99cafccfa116", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 1149, "input_preview": "The Rising Cost Of Water. As Americans grapple with a widespread affordability crisis, it seems even water is not immune to economic pressures — in fact, it’s g", "n_tokens": 229, "truncated": true, "label": "Economy", "confidence": 0.401, "scores": {"Business": 0.129, "Economy": 0.401, "Administrative": 0.2279, "None of These": 0.2421}, "tokenize_ms": 1.44, "model_ms": 3.29, "duration_ms": 4.83, "error": null}
{"ts": "2026-11-12T00:55:54.709+00:00", "request_id": "3abc4e875354", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 230, "input_preview": "SoftBank invested $20 million in Alibaba in 2000. 14 years later, that tiny stake was ... In 2000, SoftBank’s Masayoshi Son invested $20 million in Alibaba, the", "n_tokens": 59, "truncated": false, "label": "Business", "confidence": 0.9332, "scores": {"Business": 0.9332, "Economy": 0.0197, "Administrative": 0.0193, "None of These": 0.0278}, "tokenize_ms": 0.7, "model_ms": 3.63, "duration_ms": 4.43, "error": null}
{"ts": "2026-11-12T00:55:54.725+00:00", "request_id": "a9452c85736a", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 242, "input_preview": "From gas prices to grocery bills: How Trump's economic policies are giving Democrats a new ... Rising living costs are becoming a focal point for Democrats in t", "n_tokens": 51, "truncated": false, "label": "Administrative", "confidence": 0.3398, "scores": {"Business": 0.1182, "Economy": 0.2303, "Administrative": 0.3398, "None of These": 0.3116}, "tokenize_ms": 0.71, "model_ms": 3.38, "duration_ms": 4.15, "error": null}
{"ts": "2026-11-12T00:55:54.741+00:00", "request_id": "90d9d42dea0d", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 259, "input_preview": "Pickleball facility franchisor files for bankruptcy as founder acknowledges business mistake: 'I own it'. The Picklr's Chapter 11 filing stems from costly lease", "n_tokens": 50, "truncated": false, "label": "Business", "confidence": 0.9364, "scores": {"Business": 0.9364, "Economy": 0.0207, "Administrative": 0.0175, "None of These": 0.0254}, "tokenize_ms": 0.71, "model_ms": 3.55, "duration_ms": 4.32, "error": null}
{"ts": "2026-11-12T00:55:54.756+00:00", "request_id": "3447e8d871ff", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 569, "input_preview": "Global Intelligence Report for Monday, October 12, 2026. You've reached subscriber-only content Unlock expert intelligence: your gateway to exclusive security i", "n_tokens": 107, "truncated": false, "label": "None of These", "confidence": 0.3343, "scores": {"Business": 0.2843, "Economy": 0.2245, "Administrative": 0.1569, "None of These": 0.3343}, "tokenize_ms": 0.88, "model_ms": 3.41, "duration_ms": 4.36, "error": null}
{"ts": "2026-11-12T00:55:54.771+00:00", "request_id": "8d659c71caa3", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 435, "input_preview": "SEC proposes broader fund cross-trading to cut investor costs. To expand the types of securities eligible for cross-trading by registered funds while introducin", "n_tokens": 72, "truncated": false, "label": "Administrative", "confidence": 0.3601, "scores": {"Business": 0.1761, "Economy": 0.2244, "Administrative": 0.3601, "None of These": 0.2394}, "tokenize_ms": 0.78, "model_ms": 3.68, "duration_ms": 4.53, "error": null}
{"ts": "2026-11-12T00:55:54.787+00:00", "request_id": "6f5b2f4a7585", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 103, "input_preview": "Rosen Law Firm Encourages Barclays PLC Investors to Inquire About Securities Class Action Investigation", "n_tokens": 19, "truncated": false, "label": "Business", "confidence": 0.8956, "scores": {"Business": 0.8956, "Economy": 0.0327, "Administrative": 0.0301, "None of These": 0.0416}, "tokenize_ms": 0.72, "model_ms": 3.47, "duration_ms": 4.27, "error": null}
{"ts": "2026-11-12T00:55:54.803+00:00", "request_id": "1fea799d44f2", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 432, "input_preview": "Global Hygiene Products Market in 2025 Highlights Key Trends, Market Size, and Regional Developments. Xiamen, Fujian, China - October 12, 2026 - Overall Market ", "n_tokens": 89, "truncated": false, "label": "Business", "confidence": 0.7067, "scores": {"Business": 0.7067, "Economy": 0.1303, "Administrative": 0.0662, "None of These": 0.0968}, "tokenize_ms": 0.94, "model_ms": 3.57, "duration_ms": 4.6, "error": null}
{"ts": "2026-11-12T00:55:54.819+00:00", "request_id": "640bdc08be25", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 374, "input_preview": "Trump defends Russia diesel deal as legislators from both parties complain. Story audio is generated using AI President Donald Trump on Monday defended a diesel", "n_tokens": 66, "truncated": false, "label": "Administrative", "confidence": 0.3559, "scores": {"Business": 0.1058, "Economy": 0.2445, "Administrative": 0.3559, "None of These": 0.2938}, "tokenize_ms": 0.9, "model_ms": 3.86, "duration_ms": 4.85, "error": null}
```

*Failed runs.* Four requests the endpoint refused (sent with
`python send.py --bad`), and one server that could not start because the
port was already in use:

```json
{"ts": "2026-11-12T00:55:54.976+00:00", "request_id": "2bcc51967005", "event": "request", "method": "POST", "path": "/classify", "status": "rejected", "http_status": 400, "input_chars": 0, "input_preview": "", "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "model_ms": null, "duration_ms": 0.06, "error": "'text' is empty"}
{"ts": "2026-11-12T00:55:55.023+00:00", "request_id": "af4ff5fdc37c", "event": "request", "method": "POST", "path": "/classify", "status": "rejected", "http_status": 400, "input_chars": null, "input_preview": null, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "model_ms": null, "duration_ms": 0.11, "error": "body is not valid JSON (Expecting value at character 0)"}
{"ts": "2026-11-12T00:55:55.087+00:00", "request_id": "60652b641b89", "event": "request", "method": "POST", "path": "/classify", "status": "rejected", "http_status": 413, "input_chars": null, "input_preview": null, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "model_ms": null, "duration_ms": 0.04, "error": "body is 1100012 bytes; the limit is 1000000"}
{"ts": "2026-11-12T00:55:55.103+00:00", "request_id": "66d47c528aa7", "event": "request", "method": "POST", "path": "/label", "status": "rejected", "http_status": 404, "input_chars": null, "input_preview": null, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "model_ms": null, "duration_ms": 0.03, "error": "no such route"}
{"ts": "2026-11-12T00:56:00.313+00:00", "event": "startup", "host": "127.0.0.1", "port": 8000, "status": "error", "error": "could not listen on 127.0.0.1:8000 ([WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted)"}
```

All 11 bad requests in that session were refused with a 400, 404 or 413 and
each left a record. Two kinds of failure did **not** happen, so they are not
shown:

- **No request ended in a 500.** The model never raised on any input, so the
  `"status": "error"` path has not been exercised by a real failure.
- **There is no `shutdown` record for this session.** I stopped the server by
  killing the process, not with Ctrl+C, and a killed process writes nothing.
  The log shows that as a missing line, which is the kind of gap the log is
  supposed not to have.

Two things the log showed me that I did not know before I had it:

- The first request took 218.23 ms and the next nine took 4.15 to 4.85 ms.
  Almost all of the first one is `model_ms` (215.43).
- The two worked examples in my own taxonomy above come back wrong. "Harlow
  Steel cuts 900 jobs as the regional construction slowdown deepens" is
  `Business` by my rule and the model said `Economy` at 0.32 confidence. "Fed
  holds interest rates steady to fight inflation" is `Administrative` by my
  rule and the model said `Business` at 0.79.

**What It Costs**

TakeMeter calls no API and buys no tokens, so its real cost is **seconds of
compute on my own machine**. One run is one `POST /classify` request.

*Measured cost per run: **25.86 ms (0.026 s)**, averaged over ten requests.*

*How I measured it:* I started a fresh server (`python serve.py`), sent the
first ten held-out posts with `python send.py --held-out 10`, and took the
`duration_ms` field of those ten records from `logs/classify.jsonl`. That
field is timed inside the server, from the start of handling the request to
after the response is sent. The ten values, in order:

| Request | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| `duration_ms` | 218.23 | 4.83 | 4.43 | 4.15 | 4.32 | 4.36 | 4.53 | 4.27 | 4.60 | 4.85 |

Sum 258.57 ms ÷ 10 = **25.86 ms**. The average hides two very different
numbers: the first request after start-up cost 218.23 ms, and the other nine
averaged 40.34 ÷ 9 = 4.48 ms. Of the 25.86 ms, 24.73 ms is the model and
1.05 ms is the tokenizer.

Costs that are paid once, not per run: loading the model when the server
starts took 4.76 s (`model_load_ms` in the `startup` record), and training
it took 9 s (`python train.py`).

This was measured on an NVIDIA RTX 5070 Laptop GPU. I did not measure it on a
CPU, where each request will be slower.

*For a hundred people a day,* at one article each: 100 × 0.02586 s =
**2.6 s of compute a day**. If the server stays up all day, only the first
of the hundred is a slow one, so it is nearer 218.23 ms + 99 × 4.48 ms =
0.66 s, plus 4.76 s to load the model once: about 5.4 s a day in total.

**Stretch**

Declared here before starting either one:

- *A second measured improvement*, run and logged the same way as the first.
- *A latency breakdown*: where the time goes across the stages of one
  request, from the `tokenize_ms`, `model_ms` and `duration_ms` fields the
  log already records.

**Run Log — Before**

The criteria are in `criteria.md` under "Capstone criteria" and were
committed (`add capstone criteria`) before `capstone_eval.py` existed. A
trial is one fresh start of `serve.py` followed by 100 requests. Run with
`python capstone_eval.py --label before`; scores are in
`capstone_results_before.json` and each trial's server log is
`logs/eval_before_trial<N>.jsonl`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Endpoint as accurate as the notebook | 30 of 34 | 30/34 | 30/34 | 30/34 | MET |
| 2. Every label's recall through the endpoint | ≥ 0.60 | 0.40 lowest (`None of These`) | 0.40 lowest (`None of These`) | 0.40 lowest (`None of These`) | MISSED |
| 3. No classified request over 100 ms | 35 of 35 | 33/35 | 33/35 | 33/35 | MISSED |
| 4. Log agrees with what was sent, 10 at a time | 50 of 50 | 50/50 | 50/50 | 50/50 | MET |
| 5. Bad request refused within 5 s, server still up | 14 of 14, then 200 | 12/14, then 200 | 12/14, then 200 | 12/14, then 200 | MISSED |

The three runs have the same scores. I checked that they really are three
runs: each has its own log file with its own timestamps and request ids, and
the timings differ (the first request took 210.71, 212.08 and 210.98 ms).
The scores repeat because nothing in the endpoint is random. The model is
fixed and in evaluation mode, so the same text gets the same label every
time.

*Criterion 1.* From `stage_held_out` in `capstone_eval.py`, trial 1. The
four posts the endpoint got wrong, of 34:

```
true None of These  got Administrative  conf 0.34  From gas prices to grocery bills: How Trump's economic policies are gi
true None of These  got Administrative  conf 0.38  Full text of Oklahoma State Question 845 set for Nov. 3 vote. If State
true None of These  got Business        conf 0.89  Prime Day 2 deals - Last chance: Mac mini, AirPods, Apple Watch Series
true Business       got None of These   conf 0.35  NOTICE OF INCORPORATION OF HOUSING AUTHORITY OF THE VILLAGE OF DECATUR
```

*Criterion 2.* Scored in `score_trial` from the same 34 answers, trial 1:

```
Business        recall 0.95
Economy         recall 1.00
Administrative  recall 1.00
None of These   recall 0.40
```

*Criterion 3.* From `stage_held_out` and `stage_long_article`, with the
times read from each trial's log. The requests over 100 ms, all three
trials:

```
trial 1: request  1 (held-out post): duration_ms 210.71, tokenize_ms 2.52, model_ms 208.09, n_tokens 67
trial 1: request 35 (900,000-character article): duration_ms 768.34, tokenize_ms 758.52, model_ms 3.49, n_tokens 177274
trial 2: request  1 (held-out post): duration_ms 212.08, tokenize_ms 3.37, model_ms 208.6, n_tokens 67
trial 2: request 35 (900,000-character article): duration_ms 770.17, tokenize_ms 760.78, model_ms 3.31, n_tokens 177274
trial 3: request  1 (held-out post): duration_ms 210.98, tokenize_ms 3.45, model_ms 207.4, n_tokens 67
trial 3: request 35 (900,000-character article): duration_ms 766.15, tokenize_ms 758.56, model_ms 3.63, n_tokens 177274
```

The two log records from trial 1 (`logs/eval_before_trial1.jsonl`, written
by `Handler._finish` in `serve.py`):

```json
{"ts": "2026-11-12T01:08:36.207+00:00", "request_id": "33f4b10fc861", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 240, "input_preview": "Bitcoin Miner Fees Fall to Just 0.64% of Revenue, Analyst Says. Transaction fees averaged just 0.64% of Bitcoin miner revenue in the last 30 days, according to ", "n_tokens": 67, "truncated": false, "label": "Business", "confidence": 0.9269, "scores": {"Business": 0.9269, "Economy": 0.0222, "Administrative": 0.0193, "None of These": 0.0316}, "tokenize_ms": 2.52, "model_ms": 208.09, "duration_ms": 210.71, "error": null}
{"ts": "2026-11-12T01:08:36.978+00:00", "request_id": "eda94e455cc6", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 900000, "input_preview": "The city council approved a new water budget for the coming year. The city council approved a new water budget for the coming year. The city council approved a ", "n_tokens": 177274, "truncated": true, "label": "None of These", "confidence": 0.3023, "scores": {"Business": 0.1649, "Economy": 0.275, "Administrative": 0.2578, "None of These": 0.3023}, "tokenize_ms": 758.52, "model_ms": 3.49, "duration_ms": 768.34, "error": null}
```

*Criterion 4.* From `stage_concurrent`, trial 1. The 50 requests were
answered 200 forty times, 400 nine times and 413 once, and every one had
exactly one log record with the same `request_id`, `http_status` and
`label`. The harness waits one second before reading the log, because
`serve.py` writes a record just after it sends the answer.

*Criterion 5.* From `stage_bad_requests`, trial 1. HTTP status, seconds to
answer, the case, and the error message sent back:

```
400    0.011 s  empty text                        'text' is empty
400    0.015 s  whitespace only                   'text' is empty
400    0.001 s  no text field                     'text' is missing
400    0.014 s  text is a number                  'text' must be a string, got int
400    0.015 s  text is null                      'text' is missing
400    0.001 s  not JSON                          body is not valid JSON (Expecting value at character 0)
400    0.015 s  JSON cut short                    body is not valid JSON (Unterminated string starting at at character 9)
400    0.016 s  a list, not an object             body must be a JSON object like {"text": "..."}
400    0.016 s  no body                           request body is empty; send {"text": "..."}
413    0.016 s  body over 1 MB                    body is 1100012 bytes; the limit is 1000000
404    0.015 s  wrong route                       no route /label; try POST /classify
400    0.016 s  not valid UTF-8                   body is not valid UTF-8
None   5.012 s  body shorter than Content-Length  no answer: TimeoutError: timed out
500    0.016 s  JSON nested 100,000 deep          the classifier failed on this input; it has been logged
```

The log records for the two that were not refused:

```json
{"ts": "2026-11-12T01:08:38.435+00:00", "request_id": "c5c21604eac6", "event": "request", "method": "POST", "path": "/classify", "status": "rejected", "http_status": 400, "input_chars": null, "input_preview": null, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "model_ms": null, "duration_ms": 5011.32, "error": "body is not valid JSON (Unterminated string starting at at character 9)"}
{"ts": "2026-11-12T01:08:43.461+00:00", "request_id": "30f3faeeb2d2", "event": "request", "method": "POST", "path": "/classify", "status": "error", "http_status": 500, "input_chars": null, "input_preview": null, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "model_ms": null, "duration_ms": 0.47, "error": "RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string"}
```

**Verdicts and Diagnoses**

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Endpoint as accurate as the notebook | 30 of 34 | MET | 30 of 34 in all three trials, and the four it gets wrong are the same four cells as the seed-42 confusion matrix above |
| 2 | Every label's recall through the endpoint | ≥ 0.60 | MISSED | `None of These` 0.40 in all three trials; the other three labels are 0.95 or 1.00 |
| 3 | No classified request over 100 ms | 35 of 35 | MISSED | 33 of 35 in all three trials: the first request and the 900,000-character article |
| 4 | Log agrees with what was sent, 10 at a time | 50 of 50 | MET | 50 of 50 in all three trials |
| 5 | Bad request refused within 5 s, server still up | 14 of 14, then 200 | MISSED | 12 of 14 in all three trials: one request never got an answer and one got a 500 |

*Criterion 2 — the stage is the model, not the endpoint.* The endpoint
returns exactly what the notebook's model returns (criterion 1), so this is
the unit 6 miss seen through a new door. Two of the five `None of These`
posts were called `Administrative` at low confidence (0.34 and 0.38): an
article on how Trump's economic policies play for Democrats, and the text of
Oklahoma State Question 845. Both are full of government and election words,
and my rules send them to `None of These` because no agency takes an action.
The model learned the vocabulary, not the rule. The third, a Prime Day deals
page, was called `Business` at 0.89, because it is a list of company and
product names. The mechanism is the one What's Still Broken already names
above: `None of These` is defined by what it isn't, so its 24 training rows
share nothing to learn.

*Criterion 3 — two misses, two different stages.*

- **The first request (about 211 ms): the stage is the model's forward
  pass.** `model_ms` is 208.09 of the 210.71 ms, and `tokenize_ms` is 2.52.
  The same post costs about 4 ms on any later request. The mechanism is
  that the first pass through the model on the GPU pays a one-time set-up
  cost, and `serve.py` never runs the model before it starts listening. So
  the cost is not paid at start-up, where nobody is waiting. It is paid by
  whoever calls first.
- **The 900,000-character article (about 768 ms): the stage is the
  tokenizer.** `tokenize_ms` is 758.52 of the 768.34 ms and `model_ms` is
  3.49, the same as a short post. The mechanism is in `Classifier.classify`
  in `classify.py`: to report `n_tokens` it tokenizes the whole text with no
  limit (177,274 tokens), then tokenizes it again cut to the 128 the model
  reads. So the cost grows with the length of what the caller sends. My
  criterion assumed it was capped by the 128-token limit. It is worse than
  one slow answer, because `serve.py` holds `model_lock` around the whole
  of `classify()`, so every other caller waits for those 758 ms too.

*Criterion 5 — two misses, both in how `serve.py` reads the request.*

- **Body shorter than its `Content-Length` (no answer in 5 s): the stage is
  `Handler._read_json_body`.** It calls `self.rfile.read(length)` with the
  length the caller claimed. The caller said 200 bytes and sent 20, so the
  read waits for 180 bytes that never come, and the handler has no socket
  timeout. The server only moved on when the client gave up and closed the
  connection. The log record shows it: `duration_ms` 5011.32, with a 400
  that was written to a closed socket. So the log says the caller was sent
  a 400 and the caller got nothing. That is a disagreement between the log
  and the caller that criterion 4 did not catch, because none of its 50
  requests was this kind.
- **JSON nested 100,000 deep (500): the stage is the same function.**
  `json.loads` raises `RecursionError` on that body, not `JSONDecodeError`.
  `_read_json_body` only catches `JSONDecodeError` and `UnicodeDecodeError`,
  so the error falls through to the `except Exception` in `do_POST`, which
  was written for the model failing. The caller got a 500 saying "the
  classifier failed on this input", which is wrong twice: it was the
  caller's mistake, and the classifier never ran.

*The pattern.* Criterion 2 is the model, and the endpoint cannot fix it. The
first-request miss is a start-up cost paid at the wrong moment. The other
three misses (the long article, the short body and the nested JSON) are one
problem with three symptoms: **the endpoint lets the caller decide how much
work it does before it has decided whether to accept the request.** The
caller's text length sets the tokenizer's cost, the caller's claimed
`Content-Length` sets how long a thread waits, and the caller's nesting
depth sets how deep the JSON parser recurses. The 1 MB body limit was the
only bound I put on the input, and all three got under it.

**The Improvement**

*What I changed:* one thing, in `Classifier.classify` in `classify.py`. It
used to tokenize the whole text to count its tokens. Now it tokenizes only
the first 4,096 characters of a long text. If that head alone is clearly
over the model's 128-token limit, the model's 128 tokens all come from it,
so the head is all that gets tokenized. Nothing else changed: same model,
same `serve.py` request handling, same criteria, same harness.

*Which diagnosis pointed at it:* the pattern above, that the caller decides
how much work the endpoint does. Of its three symptoms I took the long
article, because it was the only one that also slowed down everyone else:
the 758 ms of tokenizing happened inside `model_lock`.

*Checked before re-running:* on 282 texts over 4,096 characters, built from
my own articles and some odd cases, the 128 tokens the model receives are
identical to the old path on all 282.

### Run Log — After

`python capstone_eval.py --label after`, results in
`capstone_results_after.json`, logs in `logs/eval_after_trial<N>.jsonl`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Endpoint as accurate as the notebook | 30 of 34 | 30/34 | 30/34 | 30/34 | MET |
| 2. Every label's recall through the endpoint | ≥ 0.60 | 0.40 lowest (`None of These`) | 0.40 lowest (`None of These`) | 0.40 lowest (`None of These`) | MISSED |
| 3. No classified request over 100 ms | 35 of 35 | 34/35 | 34/35 | 34/35 | MISSED |
| 4. Log agrees with what was sent, 10 at a time | 50 of 50 | 50/50 | 50/50 | 50/50 | MET |
| 5. Bad request refused within 5 s, server still up | 14 of 14, then 200 | 11/14, then 200 | 11/14, then 200 | 12/14, then 200 | MISSED |

The 900,000-character article after the change, from
`logs/eval_after_trial1.jsonl`:

```json
{"ts": "2026-11-12T01:12:46.815+00:00", "request_id": "fc60bd1c98ed", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 900000, "input_preview": "The city council approved a new water budget for the coming year. The city council approved a new water budget for the coming year. The city council approved a ", "n_tokens": 809, "n_tokens_exact": false, "truncated": true, "label": "None of These", "confidence": 0.3023, "scores": {"Business": 0.1649, "Economy": 0.275, "Administrative": 0.2578, "None of These": 0.3023}, "tokenize_ms": 2.59, "model_ms": 3.11, "duration_ms": 6.77, "error": null}
```

*Before and after, side by side* (run 1 / run 2 / run 3):

| Criterion | Target | Before | After | After the second improvement |
|---|---|---|---|---|
| 1. Accuracy through the endpoint | 30 of 34 | 30/34 / 30/34 / 30/34 — MET | 30/34 / 30/34 / 30/34 — MET | 30/34 / 30/34 / 30/34 — MET |
| 2. Lowest label recall | ≥ 0.60 | 0.40 / 0.40 / 0.40 — MISSED | 0.40 / 0.40 / 0.40 — MISSED | 0.40 / 0.40 / 0.40 — MISSED |
| 3. Classified requests within 100 ms | 35 of 35 | 33/35 / 33/35 / 33/35 — MISSED | 34/35 / 34/35 / 34/35 — MISSED | 35/35 / 35/35 / 35/35 — MET |
| 4. Log agrees, 10 at a time | 50 of 50 | 50/50 / 50/50 / 50/50 — MET | 50/50 / 50/50 / 50/50 — MET | 50/50 / 50/50 / 50/50 — MET |
| 5. Bad requests refused in 5 s | 14 of 14 | 12/14 / 12/14 / 12/14 — MISSED | 11/14 / 11/14 / 12/14 — MISSED | 12/14 / 12/14 / 12/14 — MISSED |
| Slowest classified request, ms | | 768.34 / 770.17 / 766.15 | 226.89 / 213.37 / 209.78 | 7.38 / 8.33 / 7.41 |
| The 900,000-character article, ms | | 768.34 / 770.17 / 766.15 | 6.77 / 7.52 / 6.83 | 7.38 / 8.33 / 7.41 |
| The first request after start-up, ms | | 210.71 / 212.08 / 210.98 | 226.89 / 213.37 / 209.78 | 6.37 / 6.33 / 6.07 |

*Did it help:* yes for what it was aimed at, and it did not change a
verdict. The long article went from about 768 ms to about 7 ms, and
criterion 3 went from 33 of 35 to 34 of 35. It is still MISSED, because the
first request after start-up is still over 200 ms. That is the other
mechanism in the criterion 3 diagnosis, and this change was never going to
touch it.

*What got worse, or looked like it:*

- **Criterion 5 came out lower in two of the three trials: 11, 11, 12
  against 12, 12, 12 before.** The request that failed is one that passed in
  every earlier run, the body over 1 MB. In trials 1 and 2 the caller got
  no answer: `ConnectionAbortedError: [WinError 10053] An established connection was aborted by the software in your host machine`. My change is in `classify.py` and this
  request is refused before the classifier is reached, so I do not think the
  change caused it. I tested that: I sent the same request 30 times to the
  old code and 30 times to the new code, each on a fresh server, and got a
  413 all 60 times. So I could not reproduce it on its own, and I cannot
  prove what triggers it. What I can name is the mechanism. `serve.py`
  answers 413 from the `Content-Length` header and closes the connection
  without reading the 1.1 MB body, while the caller is still sending it. On
  Windows the caller can then get a connection reset in place of the answer.
  It is a race, it was there before the change, and it is the reason for
  running three trials: one run of "before" would have told me this case was
  fine.
- **`n_tokens` is no longer exact for long texts.** For the article it now
  reads 809 where the true count is 177,274. The response and the log carry
  a new field, `n_tokens_exact: false`, to say so. `truncated` is still
  right. That is the trade: an exact count nobody used, for 750 ms.
- **The fix does not cover every long input.** A 900,000-character string
  with no spaces is one giant word, which tokenizes to 3 tokens, so the head
  is not over the limit and the code falls back to tokenizing everything.
  That took about 500 ms when I tried it. Criterion 3's article has spaces,
  so the criterion does not see this.

**The Second Improvement** (stretch)

*What I changed:* `serve.py` now classifies one throwaway string after
loading the model and before it starts listening, and records how long that
took as `warmup_ms` in the `startup` record.

*Which diagnosis pointed at it:* the other half of criterion 3. The first
pass through the model costs about 210 ms once, and it was being paid by
whoever called first.

`python capstone_eval.py --label after2`, results in
`capstone_results_after2.json`, logs in `logs/eval_after2_trial<N>.jsonl`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Endpoint as accurate as the notebook | 30 of 34 | 30/34 | 30/34 | 30/34 | MET |
| 2. Every label's recall through the endpoint | ≥ 0.60 | 0.40 lowest (`None of These`) | 0.40 lowest (`None of These`) | 0.40 lowest (`None of These`) | MISSED |
| 3. No classified request over 100 ms | 35 of 35 | 35/35 | 35/35 | 35/35 | MET |
| 4. Log agrees with what was sent, 10 at a time | 50 of 50 | 50/50 | 50/50 | 50/50 | MET |
| 5. Bad request refused within 5 s, server still up | 14 of 14, then 200 | 12/14, then 200 | 12/14, then 200 | 12/14, then 200 | MISSED |

The `startup` record and the first request, from
`logs/eval_after2_trial1.jsonl`:

```json
{"ts": "2026-11-12T01:14:23.166+00:00", "event": "startup", "host": "127.0.0.1", "port": 8765, "status": "ok", "device": "cuda", "labels": ["Business", "Economy", "Administrative", "None of These"], "max_length": 128, "model_seed": 42, "model_trained_at": "2026-11-12T00:44:50+00:00", "model_load_ms": 4626.8, "warmup_ms": 211.1, "error": null}
{"ts": "2026-11-12T01:14:23.299+00:00", "request_id": "267cfc76d3f4", "event": "request", "method": "POST", "path": "/classify", "status": "ok", "http_status": 200, "input_chars": 240, "input_preview": "Bitcoin Miner Fees Fall to Just 0.64% of Revenue, Analyst Says. Transaction fees averaged just 0.64% of Bitcoin miner revenue in the last 30 days, according to ", "n_tokens": 67, "n_tokens_exact": true, "truncated": false, "label": "Business", "confidence": 0.9269, "scores": {"Business": 0.9269, "Economy": 0.0222, "Administrative": 0.0193, "None of These": 0.0316}, "tokenize_ms": 0.89, "model_ms": 5.39, "duration_ms": 6.37, "error": null}
```

*Did it help:* yes. The first request went from about 211 ms to about 6 ms,
and criterion 3 is MET in all three trials, with the slowest classified
request at 7.38 / 8.33 / 7.41 ms. The trade is that the cost moved; it did
not go away. Start-up is now about 210 ms longer
(4.6 s to load the model, then 210 ms of
warm-up), paid once when nobody is waiting. Criterion 5 was back to 12 of
14 in all three trials, which fits the 1 MB failure being a race and not
something the first change broke.

**Latency Breakdown** (stretch)

Where the time goes in one request, from the `tokenize_ms`, `model_ms` and
`duration_ms` fields in the three `logs/eval_after2_trial<N>.jsonl` files.
Each figure is the mean of the three trials. "Everything else" is
`duration_ms` minus the two stages: reading the body, parsing the JSON,
waiting for the model lock, and sending the answer.

| Requests | Whole request, ms | Tokenizer | Model | Everything else |
|---|---|---|---|---|
| 34 held-out posts, one at a time | 4.42 | 0.84 (19%) | 3.51 (79%) | 0.07 (2%) |
| 40 held-out posts, 10 at a time | 18.76 | 0.78 (4%) | 3.61 (19%) | 14.37 (77%) |
| The 900,000-character article | 7.71 | 2.82 (37%) | 3.82 (50%) | 1.07 (14%) |

One at a time, the model is most of a request and the HTTP handling is
almost nothing. Ten at a time, each request does the same work in the
tokenizer and the model but takes about four times as long, and nearly all
of the extra is "everything else". That is requests queuing for
`model_lock`: the server answers on ten threads but only one can use the
model at once. So under load the model is not the slow stage. Waiting for
it is.

**What It Costs — after the improvements**

The number in What It Costs above (25.86 ms) was measured before either
improvement, and most of it was the slow first request. Measured the same
way on the final code, the `duration_ms` of the first ten requests in
`logs/eval_after2_trial1.jsonl`:

| Request | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| `duration_ms` | 6.37 | 5.03 | 4.15 | 4.41 | 4.18 | 4.58 | 4.18 | 4.11 | 4.31 | 4.48 |

Sum 45.80 ms ÷ 10 = **4.58 ms (0.0046 s) per run.**

For a hundred people a day, at one article each: 100 × 0.0046 s =
**0.46 s of compute a day**, plus 4.6 s to load the model
and 0.21 s to warm it each time the server is started. It is
seconds of my own laptop's GPU, not money. I did not measure it on a CPU.

**What's Still Broken**

Two criteria are still missed.

*2. Every label's recall ≥ 0.60 — missed (`None of These` 0.40 in every
trial).*
What I'd do: what unit 6 already says. Give `None of These` something
positive to learn, by splitting elections and campaigns out of it, and add
articles to the three small labels.
Why I stopped: I ruled it out of scope at the start. It is a relabelling
and a retraining, and this unit was about the endpoint. The endpoint cannot
improve a label the model did not learn.

*5. Bad requests refused within 5 s — missed (12 of 14 at best).* Three
mechanisms, all in how `serve.py` reads a request:

- A body shorter than its `Content-Length` gets no answer. I'd set a read
  timeout on the handler so a stalled body is answered with a 408.
- JSON nested 100,000 deep gets a 500. I'd catch `RecursionError` in
  `_read_json_body` and answer 400.
- A body over 1 MB sometimes gets a connection reset in place of its 413.
  I'd read and discard the body before closing, up to a limit.

Why I stopped: the unit allows one improvement, and I added one more as a
declared stretch. I spent both on criterion 3, because one of its two misses
slowed every other caller. No single change would have turned criterion 5
to MET, since it has three separate mechanisms.

*Things no criterion caught:*

- A 900,000-character string with no spaces still takes about 500 ms.
- When the short-body request hangs, the log records a 400 that the caller
  never received. Criterion 4 passed because none of its 50 requests was
  that kind.
- A server that is killed leaves no `shutdown` record.
- I have not run any of this on a CPU, and I tested `RUNNING.md` from a
  clean clone using my existing virtual environment, not a fresh
  `pip install`.

*Targets that were set too low.* Criteria 1 and 4 were met in every run.
Criterion 1 could only fail if the serving code was wrong, and it is useful
as a guard, but it was never going to teach me anything. Criterion 4 I
would tighten: 200 requests, 50 at a time, with the short-body and
oversized requests in the mix, and the log read without a one-second wait.
Criterion 3 is now met with a slowest request of about 8 ms, so 100 ms is
loose. I'd tighten it to 25 ms and apply it to the requests sent 10 at a
time as well, which average 14 to 20 ms and would not all pass.

*What I'd do first with another unit:* put a read timeout on the request
handler. It is the only remaining miss where one caller can hold a server
thread for as long as they like, and it is also the case where my log says
something that did not happen.

**How I Used AI**

I used Claude (in Claude Code) for most of the work in this unit, and I am
listing it plainly.

*Moment 1 — the extension.* I chose project 3 and shape C and asked it to
carry out the capstone. It read the repo, pointed out that the notebook
never saved the model, and proposed the `POST /classify` endpoint as the one
capability. It wrote `train.py`, `classify.py`, `serve.py`, `runlog.py`,
`send.py` and `capstone_eval.py`. While testing it found a bug in its own
code: on Windows a second `serve.py` could bind a port that was already in
use, and it fixed that before the criteria were written.

*Moment 2 — the criteria.* The brief says not to ask a model to write
these. I asked it to take my unit 5 criteria and modify them, and it did:
each capstone criterion names the unit 5 criterion it came from. The
targets and reasons in `criteria.md` under "Capstone criteria" were drafted
by AI from my earlier ones, and committed before any test was run.

*Moment 3 — the testing and write-up.* It ran the three trials, wrote the
diagnoses from the log records, chose and made the two improvements, and
drafted these README sections. When criterion 5 came out worse after the
first improvement, it sent the failing request 60 more times to check
whether the change had caused it before writing that up.

*What I decided myself:*

- Which system to extend. I picked project 3, TakeMeter, out of my four.
- The shape. I chose C, extend one capability, because TakeMeter could
  train and score itself but could not label a new article.
- To keep the work in this repository and not start a new one. I checked
  that before going further, so the extension sits next to what it extends.
- Where the criteria came from. I decided to base them on my unit 5
  criteria with small changes, instead of starting from five new ones, so
  each capstone criterion can be traced back to one I had already tested.
- That the work should be committed in small steps, so the history shows
  the order things happened in, with the criteria before any result.
