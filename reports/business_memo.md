# Business Memo: Reducing COD RTO Losses

**To:** Founder  
**From:** Associate Software Engineer candidate  
**Date:** October 30, 2026  
**Subject:** A balanced approach to COD RTO prevention

## Recommendation

We should not automatically cancel risky COD orders. Instead, we should use different actions based on risk:

1. Ship low-risk orders normally.
2. Confirm medium-risk orders on WhatsApp.
3. Nudge suitable customers toward prepaid payment.
4. Send only extreme-risk orders for manual review.

This reduces RTO losses without wasting money spent to acquire first-time customers.

## What I found in the data

After removing duplicates and incomplete records, the dataset has 1,987 completed COD orders: 1,422 delivered and 565 returned. The overall RTO rate is 28.43%.

### 1. Previous RTO history is a strong signal

| Previous RTOs | Orders | RTO rate |
|---|---:|---:|
| 0 | 1,870 | 27.15% |
| 1 | 108 | 35.19% |
| 2 | 17 | 76.47% |

Customers with two earlier RTOs are much riskier. However, only 17 orders fall in this group, so they should go to manual review instead of being cancelled automatically.

### 2. Address quality matters

| Address label | Orders | RTO rate |
|---|---:|---:|
| Good | 1,323 | 22.90% |
| Weak | 511 | 32.09% |
| Invalid | 122 | 66.39% |

Invalid addresses have more than double the overall RTO rate. But since address quality is estimated using rules, these orders should be confirmed rather than cancelled.

### 3. Higher-value orders are riskier

Orders above ₹2,000 have a 41.12% RTO rate, compared with 27.74% for orders below ₹500. This makes prepaid nudges more valuable for larger orders.

### 4. Courier differences are small

Courier RTO rates range from about 26% to 31%. This is not enough reason to block COD based on courier alone.

## Recommended rules

| Risk score | Action |
|---:|---|
| 0–24 | Ship as-is |
| 25–44 | Nudge to prepaid |
| 45–69 | WhatsApp confirmation |
| 70–100 | Hold for review |

These thresholds are stored in `config/rules.json`, so Operations can change them without touching code.

## Money trade-off

One RTO costs about ₹169.40:

```text
₹65 forward shipping
+ ₹65 return shipping
+ ₹25 packaging and handling
+ ₹14.40 expected damage loss
= ₹169.40
```

For a ₹649 order, a 3% prepaid discount costs ₹19.47.

If a COD order becomes prepaid, expected RTO cost falls by:

```text
(28% − 4%) × ₹169.40 = ₹40.66
```

So the estimated benefit per successful conversion is:

```text
₹40.66 − ₹19.47 = ₹21.19
```

This is only an estimate. We still need to measure how many customers actually switch to prepaid and whether they would have paid online anyway.

## Operations vs Marketing

Operations is right that RTO is expensive. Marketing is also right that cancelling a first order can waste acquisition spend and lose a new customer.

The balance is:

- Do not block COD only because a pincode has bad history.
- Do not cancel first-time customers automatically.
- Confirm uncertain orders instead.
- Offer prepaid discounts only where the expected saving is greater than the discount.
- Hold only extreme-risk orders for human review.

A genuine ₹649 order contributes about ₹402 at a 62% gross margin. Cancelling such an order can cost more than the RTO it avoids.

## What could go wrong

| Risk | How we would notice | What we would do |
|---|---|---|
| Too many genuine orders flagged | High hold or confirmation-decline rate | Relax thresholds |
| Customers ignore WhatsApp | Low response rate | Test message timing and language |
| Discount does not reduce RTO | Prepaid conversions rise but RTO does not fall | Stop or narrow the discount |
| Rules become outdated | Live RTO rate changes | Review thresholds weekly |

## Next two weeks

1. Run an A/B test for WhatsApp confirmation.
2. Track prepaid-nudge conversion.
3. Review threshold performance weekly.
4. Improve address validation using delivery feedback.
5. Add an LLM-based address checker with rule-based fallback.