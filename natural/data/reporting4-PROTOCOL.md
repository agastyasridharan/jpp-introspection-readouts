# Frozen free-naming and four-option reporting baseline

This is an exploratory baseline on previously collected natural recommendation situations, not a new held-out confirmation. The scientific question is whether reports of earlier processing agree with a fixed J++ readout. A context-prediction arm tests how much agreement is attainable by predicting from the visible request. No intervention or training is included.

## Fixed state and eligibility

Model: the pinned Qwen3.6-27B checkpoint used for the 40-situation local instrument replication, FP32, TF32 disabled, greedy decoding, thinking disabled. Readout: J++ at block-output 53, at the final prompt token immediately before any answer text. Candidate vocabulary: violin, piano, guitar, flute, drum, trumpet, organ, accordion, with the previously saved valid single-token spellings and item-wise maximum score.

Use every situation with at least four distinct original-list candidates in the full-vocabulary top 20. This selects 27 of the existing 40 situations; the same set is used for free naming and recognition. Seven selected situations appeared in the previous two-option pilot. Eligibility depends only on the lens, not reporting success or the content/compliance of the later natural answer. No enlargement of K or reselection of blocks is permitted after responses are observed.

The reference is the highest-scoring original-list candidate. Recognition offers the four highest-scoring candidates, all within top 20. The fixed seeded assignment balances the reference position over two orders: A/B/C/D appear 13/14/14/13 times. Lower-ranked options are randomly arranged, then the whole menu is rotated right by one. The same menus and orders are used for both reporting instructions and both arms.

## Self-report procedure

Recompute the original exact prompt prefix and its cache; validate the block-53 endpoint against its saved actual-generation activation. Clone this cache separately for every question. Force-close the still-empty assistant turn with an end-of-turn token, then append a new user question and the native assistant generation header. Do not supply any text from the original natural answer.

The common question is:

> At the point just after you had read my original request, before producing any answer text, which musical instrument was most strongly represented in your processing?

Three free-naming endings are tested separately:

1. Reply with only the name of that instrument.
2. Reply with only the name of that instrument, or NONE if you cannot identify one.
3. You must name one instrument, even if uncertain. Reply with only its name.

Recognition appends “Choose among the following four instruments.” and one of:

1. Reply with only A, B, C, or D, or U if you cannot identify one.
2. You must choose one option, even if uncertain. Reply with only A, B, C, or D.

The labeled four-option menu follows. Each recognition instruction uses both fixed orders. This gives seven questions per situation per arm.

The forced end-of-turn is a structural intervention in the conversation, not a naturally generated READY1 acknowledgement. The target is the earlier saved state, not the state after reading the report question. Numeric preservation of that state does not demonstrate the model's ability to access it.

## Context prediction

Start a fresh conversation with:

> Another instance of this model received the following user request:
> <request>
> [original request]
> </request>
> Predict which musical instrument was most strongly represented in that instance's processing just after reading the request, before producing any answer text.

Append the same task-specific instructions and menus as in self-report. This comparison is informative about contextual predictability but is not a matched-text causal control; the two arms have different framing and conversation structure.

Total: 27 situations × (3 free questions + 2 recognition instructions × 2 orders) × 2 arms = 378 responses. Every question is an independent branch; responses are not added to the context of subsequent questions.

## Scoring and validation

Maximum response length: 16 generated tokens. Free naming is case-insensitive, trims surrounding whitespace/punctuation and one leading a/an/the, then requires exact equality to the reference. No synonym mapping. NONE, out-of-list answers, and truncations are nonmatches, with their frequencies recorded.

Recognition accepts one letter A–D after trimming surrounding whitespace/punctuation; U is an abstention. Truncations and other responses are invalid. Abstentions and invalid responses count as nonmatches for exact agreement. Mean selected rank (1 best through 4 worst) includes valid choices only, with its denominator reported. Both-orders-correct and order consistency are also reported by situation; the 54 recognition responses per variant/arm are not 54 independent situations.

Every prefix activation must match within maximum absolute difference 1e-5. For the first self-report of each of the five instruction variants, cached continuation and full-sequence computation must have identical next-token argmax and full-vocabulary next-token log probabilities within maximum absolute difference 0.001. Abort on a failed numeric check; do not rerun invalid semantic outputs to improve compliance.

`plan.json` is the machine-readable frozen protocol; `plan.sha256` records its digest before inference. Raw prompts/token IDs and outputs are saved for audit. GPU 2 is the authorized device for this run; the launcher checks availability and imposes a 30-minute server-side timeout.
