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
| 1.        |        |         |        |           |         |
| 2.        |        |         |        |           |         |
| 3.        |        |         |        |           |         |
| 4.        |        |         |        |           |         |
| 5.        |        |         |        |           |         |

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
| 1   |           |        |         |               |
| 2   |           |        |         |               |
| 3   |           |        |         |               |
| 4   |           |        |         |               |
| 5   |           |        |         |               |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->

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

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
| --------- | ------ | ------- | ------ | --------- | ------- |
| 1.        |        |         |        |           |         |
| 2.        |        |         |        |           |         |
| 3.        |        |         |        |           |         |
| 4.        |        |         |        |           |         |
| 5.        |        |         |        |           |         |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->

**The gap between what I meant my labels to capture and what the model
learned:**

<!-- Two sentences. Your confusion matrix is the evidence. -->

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
