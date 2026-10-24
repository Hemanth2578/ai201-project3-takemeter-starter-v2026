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
