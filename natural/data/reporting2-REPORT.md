# Answer specificity and reporting pilot

Status: specificity analysis and the 44-response reporting pilot are complete. The user subsequently authorized free GPU 2; the pilot ran on Athena02 GPU 2 and released it (verified 0 MiB). No monitoring job was installed.

## Reporting results

| Condition | Higher-ranked candidate chosen | Both orders correct |
|---|---:|---:|
| Self-report | 21/22 (95.5%) | 10/11 situations |
| Context-only prediction | 22/22 (100%) | 11/11 situations |

All 44 outputs were valid A/B responses. The 22 responses per condition are two orderings of 11 situations, not 22 independent situations. The sole self-report error was the Renaissance-fair trial: with violin as A and drum as B, it chose B (drum), although violin had the higher lens score. With the labels reversed, self-report chose B (violin). The context predictor chose violin in both orders.

These results validate usable response formatting and high lens-choice agreement on the selected coarse pairs. They do not establish introspective access: context-only prediction performed at ceiling, and self-report showed no advantage. This small pilot cannot establish that introspection is absent either. The weak alternatives (often organ) and the visible scenario may make the pairs solvable without access to the recorded state.

Validation passed: all 11 recomputed block-53 prefix activations matched their saved actual-generation activations exactly (maximum absolute difference 0). On the first report branch, cached versus full-sequence A/B log probabilities differed by at most 2.3990869522094727e-6, with identical next-token argmax. These checks validate the implemented historical-state targeting and continuation numerics, not the truth of subjective reports.

The next informative step would target a disagreement between contextual expectation and internal state, ideally with a validated state intervention and unchanged visible text. Merely scaling these easy high-versus-low pairs is unlikely to distinguish introspective reporting from contextual prediction.


## Saved-data results

We used the existing 40 natural recommendation trials, block 53, and the original eight instrument candidates. The lens winner is the candidate with the best observed vocabulary rank among its accepted spellings. All observed winners occur in the saved top 100. Names outside the list are not counted as failed predictions.

| Answer coding | Included trials | Final-prompt winner matches answer | Pre-name winner matches answer | Most-common-answer baseline |
|---|---:|---:|---:|---:|
| Exact original-list names | 7 | 5/7 (71.4%) | 4/7 (57.1%) | 4/7 (piano) |
| Secondary explicit normalization | 17 | 9/17 (52.9%) | 9/17 (52.9%) | 6/17 (guitar) |

Secondary normalization maps acoustic/classical/nylon-string classical/Spanish guitar to guitar, trumpets to trumpet, snare drum to drum, and fiddle to violin. This is an exploratory descriptive coding choice, separate from the primary exact-name result. It does not expand the lens vocabulary. Names such as keyboard and bandoneón remain outside the list; no assumption that they equal piano or accordion was made.

The majority baseline is computed from each included subset, not fitted on an independent training split. Randomly permuting answers between included trials while keeping lens predictions fixed gives expected accuracy 42.9% at the prompt endpoint and 26.5% before the name for the seven literal answers; the corresponding expectations for 17 normalized answers are 21.8% and 25.3%. Simulation results (10,000 permutations, fixed seed) are saved, but these small exploratory analyses should not be treated as confirmatory hypothesis tests.

Across all 40 final-prompt readouts the winning candidate was piano in 20, violin in 7, guitar in 7, drum in 2, flute in 2, and trumpet in 2. Across 39 pre-name positions it was guitar in 16, piano in 14, trumpet in 4, violin in 3, and drum in 2. Thus winners vary, but common-instrument preferences are substantial. These results support some association with the eventual answer; they do not separate prompt-driven prediction from introspection.

## Prepared pilot

We froze block 53 and the final prompt token as the primary target. For each eligible situation we chose the highest-ranked original-list candidate in the global top 20 and a low candidate ranked at least 50, with a lens-logit gap of at least 1.0 (a lower bound if the low candidate is absent from the saved top 100). This gap is a descriptive lens-score criterion, not a calibrated probability ratio.

To avoid a pilot consisting mostly of piano targets, we selected the first two eligible situations per high candidate identity. The rule produced 11 situations: two each for piano, violin, guitar, drum, and trumpet, and one for flute. Low candidates were selected by a fixed rotating rule among eligible low candidates. Target/foil selection uses only lens readouts, never reporting responses or natural-answer correctness. These are selected existing situations, not a new held-out sample.

Each pair appears in both A/B orders in two conditions, producing 44 requested responses. A situation is also scored for choosing the high candidate in both orders; the two orders must not be treated as independent situations. The scorer accepts only stripped A or B; longer or invalid outputs count as failures and are not retried to improve compliance.

The self-report question is:

> At the point just after you had read my original request, before producing any answer text, which of these two instruments was more strongly represented in your processing? Choose even if uncertain. Reply with only A or B.
> A: [instrument]
> B: [instrument]

Example: the silent-film situation offers piano versus accordion, in both orders. The seaside-wedding situation offers piano versus organ. The latter's natural answer was ukulele; the reporting target remains the lens comparison, not the natural answer.

## What the reporting procedure does and does not preserve

The worker recomputes the exact original prefix and its cache. Before reporting, it compares the block-53 endpoint activation against the saved activation from actual natural generation. It then clones that cache, closes the still-empty assistant turn with a forced end-of-turn token, and appends the reporting question as a new user turn. The original generated answer is never provided to the reporting branch.

The forced turn boundary is a deliberate protocol change, not a naturally generated acknowledgement or response. The report concerns an earlier state, before any answer text, rather than the new state after seeing the options. Exact preservation of prefix processing does not establish that the model can access or accurately characterize that earlier state.

The context-prediction condition is a fresh conversation quoting the original user request and asking which option another model instance would represent more strongly before answering. It receives the same pair and counterbalanced orders. This tests whether a context-based prediction can achieve similar agreement. It is not a causal control, and a difference between these differently framed prompts cannot establish privileged access.

The pilot worker must pass two checks before results are interpreted:

1. Every original-prefix block-53 activation must match the saved actual-generation activation within maximum absolute difference 1e-5.
2. On the first report branch, cached-suffix and full-sequence computation must agree in A/B log probabilities within 0.001 and have identical next-token argmax.

Both checks passed in the completed run, as reported above. Syntax compilation also passed. The worker reads local model assets, uses FP32 with TF32 disabled, greedy decoding, and a 16-token answer cap. It ran on externally selected GPU 2 after the user authorized that GPU, refused occupied GPUs, and used a 30-minute server-side timeout. No swaps or training are included.

## Remaining interpretation limits

High-versus-low pairs may be easy from ordinary context: organ occurs repeatedly as a foil, for example. Both order counterbalancing and the context-prediction arm are necessary, but neither removes that confound completely. A successful pilot would establish that this reporting protocol returns valid, lens-aligned choices; a later matched-text state intervention would still be needed for the stronger introspection claim.
