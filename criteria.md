# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1. `Administrative` F1 is at least 0.60

<!-- Your criterion. It must name a number. -->

`Administrative` has an F1 of at least **0.60** on the held-out test set, in
every seed.

**Why this target:** `Administrative` has the smallest sample size: 26 of 223
rows, so only about 4 land in each test split.

---

## 2. Overall accuracy is at least 0.65

<!-- Your criterion. -->

Overall accuracy is at least **0.65** on the held-out test set, in every seed.

**Why this target:** There are hard cases between `Administrative` and
`Economy`, but the definitions are clearly written, which should give the
model a better understanding of them, even though the sample size for those
labels is really small and may not be enough for training. The floor to beat
is 0.59: 59% of my rows are `Business`, so a model that always guesses
`Business` scores 0.59 without learning anything. On a test split of about 34
posts, 0.65 means about 23 correct against 20 for that guesser, so the model
has to get at least three of the smaller-label posts right that pure
`Business` guessing would miss. With so few `Administrative` and `Economy`
examples to learn from, I don't expect much more than that.

---

## 3. A classmate agrees with my labels at least 70% of the time

<!-- Your criterion. -->

A classmate labels **20** of my 30 cold-labelled articles (`note` = `cold` in
`labels.csv`) using only the definitions in my README, and agrees with my
label on at least **70%** of them — at least 14 of the 20.

**Why this target:** The labels divide articles by topic, and I revised the
definitions to spell out what counts as what (for example, what counts as an
agency action), so another person labelling the same news articles should
mostly land on the same labels.

> **Revised in unit 6:** An independent labeller who has never seen my
> labels — a fresh AI agent given only the definitions and decision rules
> from my README, with the example posts removed — labels the **first 20**
> of my 30 cold-labelled articles, and agrees with my label on at least
> **70%** of them (at least 14 of 20).
>
> **Why revised:** I had no classmate available, so as written the criterion
> could not be checked. The target (70%) is unchanged; only the labeller is.
> An AI agent is a weaker check than a person: it applies my rules
> literally, and an AI also pre-labelled 193 of my rows, so it may share
> their tendencies. I used the first 20 cold rows rather than choosing them,
> so I couldn't pick easy ones.

---

## 4. Every label: at least 3 out of 5 of its posts are predicted correctly

<!-- Your criterion. -->

For every label, at least **3 out of 5** of its test posts are predicted
correctly (recall of at least **0.60**) on the held-out test set, in every
seed.

**Why this target:** With well-defined labels the model should get most posts
right for each label. I set it at 3 out of 5, not higher, because of the
`Administrative` vs `Economy` hard cases.

---

## 5. No label is predicted for more than 59% of test posts

<!-- Your criterion. -->

No single label is predicted for more than **59%** of the posts in the
held-out test set, in every seed.

**Why this target:** 59% is `Business`'s real share of my data. Setting the
cap there means the model can predict `Business` no more often than it really
appears, so even one extra `Business` guess fails it. Over-predicting
`Business` is the failure I am most worried about: with 59% of the training
data in one label, the easiest way for the model to score well is to default
to it, and every extra `Business` guess is an `Administrative`, `Economy` or
`None of These` post it failed to learn. This criterion catches that even
when accuracy looks fine.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria

Five criteria for the capstone extension, the `POST /classify` endpoint,
written before any capstone test was run. The five above are units 5 and 6
and are not changed.

These are my unit 5 criteria carried over to the new thing. Each one says
which old criterion it came from and what changed.

**A trial** is one fresh start of `serve.py` followed by the whole set of
requests. There are three trials, and a target has to hold in all three.

**What I had already seen when I wrote these.** Milestone 3 comes before
this one, so the log in the README existed first. From it I knew: the first
10 held-out posts came back 9 of 10 correct, the first request after
start-up took 218 ms and the next nine took 4 to 5 ms, and the 11 bad
requests in `send.py --bad` were each refused once. Where a criterion below
leans on one of those numbers, it says so.

---

## 1. The endpoint is as accurate as the notebook

*From criterion 2 (overall accuracy at least 0.65).*

When each of the 34 posts in `test_split.csv` is sent to `POST /classify`,
at least **30 of 34** returned labels equal the label in `test_split.csv`,
in every trial.

**Why this target:** 30 of 34 is 0.882, the accuracy `results.json` records
for the seed-42 model, and the endpoint serves that same model. So it should
not lose a single post. A 29 would mean the serving path treats text
differently from training: a different tokenizer setting, a different cut at
128 tokens, or the labels in a different order. My old target of 0.65 is too
loose here, because it would let the endpoint lose seven posts without
failing. It is not stricter than 30 because the model itself only gets 30.

---

## 2. Every label's recall through the endpoint is at least 0.60

*Criterion 4, target unchanged. This one is about the system as it already
worked.*

Over the same 34 posts, each of the four labels has a recall of at least
**0.60** (at least 3 of every 5 of its posts returned with the right label),
in every trial.

**Why this target:** the same reason as before, and one more. Someone
calling an endpoint does not know which label is the weak one, so a label
that is right 2 times in 5 is a wrong answer they cannot see coming. Unit 6
missed this on seed 42 (`None of These` 0.40), and I am not retraining in
this unit, so I expect to miss it again. I am keeping 0.60 anyway. Lowering
a target because I missed it is not a revision.

---

## 3. No classified request takes more than 100 ms

*From criterion 5 (no label predicted for more than 59% of posts): a cap on
the worst case, not on the average.*

Every request answered with a 200 has a `duration_ms` of at most **100** in
the log. That means any request, including the first one after start-up.
The set is the 34 held-out posts, sent first, then one article of 900,000
characters, which is just under the 1 MB limit the endpoint accepts:
**35 of 35**, in every trial.

**Why this target:** a warm request took 4 to 5 ms in my Milestone 3 log, so
100 ms is twenty times that, and about where an answer stops feeling
instant. It is a cap on every request and not an average for the reason
criterion 5 was: an average looked fine in unit 6 while the model guessed
`Business` for everything. A caller gets one request, not the mean of ten.
I already know the first request took 218 ms in Milestone 3, so I expect
that one to miss. I do not know what the 900,000-character article will do.
I have never sent anything that long.

---

## 4. The log agrees with what was sent

*From criterion 3 (another labeller agrees with my labels at least 70% of
the time).*

50 requests are sent 10 at a time: 40 held-out posts and 10 bad requests.
Every one gets an HTTP response, and the log holds exactly one record for
each, whose `request_id`, `http_status` and `label` equal what the caller
was sent: **50 of 50**, in every trial.

**Why this target:** 70% was right for two people judging articles. A log
is bookkeeping, and one missing record is one request I can never diagnose,
so the target is all of them. It is tested 10 at a time because the server
answers each request on its own thread and they all write to one file. That
is where a record could be lost or two could run together. In Milestone 3 I
only ever sent one request at a time.

---

## 5. A bad request is refused, not crashed on

*New. My unit 5 criteria had nothing about a bad path.*

14 bad requests are sent: the 11 in `send.py --bad`, plus a body that is not
valid UTF-8, a body shorter than its `Content-Length` says, and JSON nested
100,000 levels deep. Each one gets a 4xx answer with a JSON body containing
`error` within **5 seconds**, none gets a 5xx or no answer at all, and a
normal request sent afterwards still returns 200: **14 of 14** and the
follow-up, in every trial.

**Why this target:** a bad request is the caller's mistake, and a 500 tells
them it was mine. A request that never gets an answer is worse, because it
holds a server thread for as long as the caller waits. Five seconds is very
generous beside a 5 ms request, so a miss means a hang and not a slow
answer. The 11 from `send.py` were each refused once in Milestone 3. The
other three I have never tried.
