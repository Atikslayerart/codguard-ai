# Decision Log

## Data cleaning

- Removed 30 duplicate `order_id` records.
- Kept only completed orders: `DELIVERED` and `RTO`.
- Normalized status values to uppercase.
- Cleaned phone numbers by removing non-numeric characters and stripping a leading `91`.
- Flagged invalid phone numbers using a 10-digit Indian mobile-number pattern.
- Created address-quality labels: `GOOD`, `MEDIUM`, `WEAK`, and `INVALID`.
- Flagged obvious test names such as `Test Order` and `qwerty`.

**Alternative considered:** deleting rows with missing pincodes.  
**Decision:** kept them, because other fields may still be useful and missing pincodes can be handled as a separate risk signal.

## Risk scoring

- Used an explainable rule-points system rather than a black-box model.
- Gave the highest weight to repeated RTO history and invalid addresses.
- Reduced the score for customers with prior successful orders and no RTO history.
- Capped scores between 0 and 100.

**Alternative considered:** logistic regression.  
**Decision:** start with transparent rules because the dataset is small, the business needs explainability, and threshold changes must be easy for Operations.

## Decision thresholds

- 0–24: Ship as-is.
- 25–44: Nudge prepaid.
- 45–69: WhatsApp confirmation.
- 70–100: Hold for review.

**Alternative considered:** automatically cancel all high-risk orders.  
**Decision:** rejected because it can cancel genuine first-time customers and waste acquisition spend.

## LLM use

- Used local rule-based analysis for address quality, phone validation, suspicious names and Hinglish patterns.
- Designed the system so a Claude API can be added later without changing the decision engine.
- Did not use an LLM for arithmetic, grouping, thresholding or financial calculations.

**Reason:** simple code is more reliable, cheaper and testable for structured checks.

## WhatsApp flow

- Confirmation flow: YES ships, NO cancels, unclear reply asks again, no reply in 24 hours holds for review.
- Prepaid flow: PAY shows a mock payment step, COD keeps COD, CANCEL cancels, unclear reply asks again.
- Used a 3% illustrative discount because its expected cost is lower than the expected RTO-cost reduction.

**Alternative considered:** a larger discount to increase conversion.  
**Decision:** start with 3% and test conversion before increasing the discount.

## Dashboard

- Shows historical replay, not live intervention results.
- Separates actual delivery outcomes from recommended actions.
- Does not present unvalidated savings as measured savings.
- Uses the founder’s requested four buckets.

**Alternative considered:** showing one large “estimated savings” number.  
**Decision:** rejected because it would imply certainty the data does not support.