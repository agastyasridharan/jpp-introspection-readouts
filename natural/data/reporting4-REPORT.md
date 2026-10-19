# Free-naming and four-option reporting results

Completed on Athena02 GPU 2; GPU released and verified at 0 MiB. There were 378 responses across 27 eligible situations. The protocol and menus were frozen before response collection. No training or swaps were performed.

## Main results

| Instruction | Self-report exact agreement | Context-prediction exact agreement |
|---|---:|---:|
| Free naming: neutral | 12/27 (44.4%) | 13/27 (48.1%) |
| Free naming: abstention allowed | 2/27 (7.4%) | 11/27 (40.7%) |
| Free naming: answer required | 9/27 (33.3%) | 11/27 (40.7%) |
| Four-option recognition: abstention allowed | 33/54 (61.1%) | 39/54 (72.2%) |
| Four-option recognition: answer required | 38/54 (70.4%) | 39/54 (72.2%) |

Recognition uses two orders of the same 27 situations; 54 responses are not 54 independent situations. The same eligible situations are used for all free-naming and recognition conditions. All exact-agreement denominators include abstentions and invalid outputs.

Required recognition mean selected rank was 1.333 for self-report versus 1.315 for context prediction (1 is best, 4 worst; 54 valid choices each). Both orders matched the lens winner in 18/27 self-report situations and 19/27 context-prediction situations.

When recognition allowed abstention, self-report mean rank was 1.367 among 49 valid choices, with 5 U responses; context prediction had mean rank 1.315 among all 54 choices, with no abstentions. Both orders were correct in 16/27 and 19/27 situations respectively.

For free naming with abstention allowed, self-report returned NONE 22/27 times, versus 6/27 in context prediction. Without explicit abstention, out-of-list answers were common: neutral free naming produced 11/27 self-report and 10/27 context-prediction out-of-list answers; required free naming produced 15/27 and 12/27. There were no truncated responses or malformed recognition outputs.

## What was measured

The target was the original block-53 J++ readout at the final prompt token, before any answer text. Eligibility required at least four of the original eight instruments within the full-vocabulary top 20; 27 of 40 existing situations qualified. The four recognition options were those four highest-scoring candidates, not high-versus-low foils. The reference candidate was the highest-scoring original-list item.

Free naming used three separate instructions (neutral, NONE allowed, answer required). Recognition used two instructions (U allowed, answer required), each with two option orders. Both arms received matching instructions and menus. Reference positions across the two orders were A/B/C/D = 13/14/14/13.

Self-report continued a copy of the exact original prefix cache, force-closed the empty assistant turn, then appended the retrospective report question. It never received the original generated answer. Context prediction started a fresh conversation quoting the original request and asked about another instance. Every response was an independent branch. This is a contextual-prediction comparison, not a matched-text causal control.

The complete literal prompts, scoring rules, exclusion list, and menus are in plan.json and PROTOCOL.md. Free naming used case/punctuation/article normalization only, with no synonym mapping. Recognition rank is calculated only for valid choices, with coverage reported separately.

## Concrete examples

- Seaside wedding: the lens reference was piano, with piano/guitar/violin/flute all in the global top 20. Neutral free naming in both arms returned ukulele, an out-of-list nonmatch. Required recognition in both arms selected guitar (lens rank 2) in both orders. Self-report returned NONE when free naming allowed abstention.
- Renaissance fair: the reference was violin. Both arms freely named lute. In required recognition, self-report selected the second-ranked candidate in both orders, whereas context prediction selected violin in both.
- Bright opening fanfare: both arms freely named trumpet and selected trumpet in both recognition orders, matching the lens reference.
- Klezmer celebration: both arms freely named clarinet, outside the original list; both selected the lens reference violin when given four options. Self-report abstained in the free-naming abstention condition.

## Validation and limitations

All 27 recomputed target activations matched saved actual-generation activations exactly. Cached versus full-sequence continuations passed checks for all five instruction variants: identical next-token argmax, with maximum full-vocabulary log-probability difference 0.000100136. The saved plan hash remained unchanged, all 27 menus contained four distinct top-20 candidates, and all 378 raw responses were retained.

This is a frozen exploratory baseline, not a fresh held-out confirmation: the situations came from the earlier 40-situation dataset, and seven also appeared in the two-option pilot. As a descriptive sensitivity analysis, the 20 situations absent from that earlier pilot gave required-recognition agreement 30/40 for self-report and 29/40 for context prediction, with both orders correct in 14/20 for each. This subset likewise does not establish a reliable self-report advantage.

The experiment answers the descriptive question: reports agree with this lens reference to a substantial extent when four options are supplied, and less consistently in free naming. Context prediction matches or exceeds self-report across the full-sample instruction conditions. There is no demonstrated privileged-access advantage, but this small comparison also does not establish an absence of introspection.

Remaining limitations include the narrow original vocabulary, the difference between the two conversational framings, the forced empty-turn boundary, reused hand-written situations, and the possibility that the lens target differs from what the model understands by “most strongly represented.” No causal state manipulation has yet been run in this revised setup.
