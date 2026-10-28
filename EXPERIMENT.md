# Document Verification Lab: preregistered pilot

Question: does an independently trained OCR correctness model improve error routing beyond simple rules on the same OCR outputs?

## Scope

Personal prototype using OpenBMB's released OCR and OCR-Jev weights. No model is fine-tuned here. No Workday tenant or customer data is used. Model predictions and latency will be recorded on a shared DGX Spark; hardware contention precludes isolated speed claims.

Create 120 synthetic invoice pages with known source values and matching critical payment-region crops. Forty pages from four template families form the calibration split; 80 pages from eight other families form the held-out test split. Each family has ten independent invoices spanning clear, low-resolution, blurred, noisy and skewed captures. Splits are fixed before scoring. These generated pages test controlled behavior, not production accuracy. Known crops isolate OCR and verification; automated layout detection is outside this pilot.

## Labels and comparisons

Run MiniCPM-OCR 1.0 on each payment-region crop using its text-recognition task. Retain every output, including failures. Compare the extracted subtotal, shipping, tax, total and currency against the generator's ground truth. Model sees only source pixels and candidate OCR output, never the reference values. Record formatting errors separately from critical-field errors.

Score each natural OCR result with MiniCPM-OCR Jev using the exact upstream ternary prompt: original crop, candidate text, rendered candidate image. Keep precheck/render/runtime failures distinct from scored low confidence.

Compare: (1) arithmetic, currency and required-field checks; (2) those rules plus Jev score; (3) random review at the same review count. Rules can recognize an internally inconsistent total, but not all consistently incorrect numbers. Use calibration samples to choose a review threshold targeting at most 20% calibration review, keeping forced rule failures in review. If mandatory rule failures exceed the budget, report the actual coverage instead of relaxing the checks. Freeze threshold before held-out evaluation. Also show the exploratory risk-coverage curve over all thresholds, clearly distinguished from the frozen operating point.

Report natural OCR critical-field error rate; review count; errors caught; incorrect accepted items / accepted items; and candidate-rendering + model-forward times separately. Include sample counts and uncertainty. A high score is not document authenticity, payment approval, or a calibrated guarantee.

## Separate stress probes

Use correct transcriptions and deliberate substitutions on a fixed small subset to test score sensitivity to decimal point, currency, and consistent amount errors. This injected-error set is always reported separately from natural OCR errors. Include a business-context mismatch whose pixels are read correctly but whose purchase-order facts differ; a deterministic business check, not the OCR verifier, should flag it.

Keep exact model revisions, upstream source revision, image hashes, raw requests/results, model-loading warnings, environment versions and renderer settings. Disclose deviations before interpreting results.
