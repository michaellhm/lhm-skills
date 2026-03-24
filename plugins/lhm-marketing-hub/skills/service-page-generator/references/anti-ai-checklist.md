# Anti-AI Writing Checklist

Run these checks programmatically after writing. Use grep/bash to find violations, then fix them manually. Report what was found and what was changed.

## The Checks

### 1. Em Dashes

**Search:** `grep -n '—' [file]`
**Rule:** Zero em dashes in the page copy. Replace with commas, periods, parentheses, or restructure the sentence.
**Exception:** Internal notes, SEO score sections, and schema markup sections don't count.

### 2. Rule of 3

**Search:** Look for bullet lists with exactly 3 items, sentences listing exactly 3 examples, or paragraphs with exactly 3 points.
**Rule:** Vary structural patterns. Use 2, 4, 5, or 6 items instead of defaulting to 3. Not every group of 3 is a problem, but if the pattern repeats across sections, break it up.

### 3. Contrast Framing

**Search:** `grep -ni "while \|although \|whereas " [file]`
**Rule:** Reduce "While X, Y" and "Although X, Y" constructions that create artificial tension between concepts. Rewrite to state the point directly. One or two across a 2,500-word page is fine. Five or more is a pattern.

### 4. Poetic Shift Phrases

**Search:** `grep -ni "in a world\|in an era\|in a landscape\|in today's" [file]`
**Rule:** Remove these. They add nothing and flag the content as AI-generated.

### 5. Adverb Overuse

**Search:** `grep -oP '\w+ly\b' [file] | sort | uniq -c | sort -rn | head -20`
**Rule:** No single -ly adverb should appear more than twice in the page. If "significantly", "dramatically", "effectively", or "importantly" appear at all, consider removing them. Prefer stronger verbs over verb+adverb combinations.

### 6. Marketing Clichés

**Search:** `grep -ni "seamless\|robust\|game-chang\|innovative\|cutting-edge\|holistic\|comprehensive care\|state-of-the-art\|world-class\|next-level\|best-in-class" [file]`
**Rule:** Remove all of these. Replace with specific, concrete language about what the business actually does.

### 7. Formulaic Transitions

**Search:** `grep -ni "let's explore\|let's dive\|now, let's\|let us turn\|without further\|let's take a look\|let's break down" [file]`
**Rule:** Remove all of these. Use natural transitions that connect ideas contextually, or just start the next section directly.

### 8. Forced Inspirational Endings

**Search:** `grep -ni "journey\|empower\|transform your\|unlock\|embrace\|take the first step\|your path to" [file]`
**Rule:** Remove from paragraph endings. End paragraphs with substantive points, specific information, or direct calls to action. Not vague emotional uplift.

### 9. Hypophora (Optional Check)

**Search:** Look for patterns where a question is immediately followed by its answer in the same paragraph (outside the FAQ section).
**Rule:** In the FAQ section, question-then-answer is the format and is fine. Elsewhere, limit this pattern. If the content poses a question and immediately answers it more than twice outside the FAQ, rewrite some of them as direct statements instead.

### 10. Paragraph Structure

**Rule:** Vary paragraph length. Don't write every paragraph at the same length. Mix 1-sentence paragraphs, 2-sentence paragraphs, and 3-4 sentence paragraphs. If all paragraphs are 3 sentences long, the rhythm becomes mechanical.

## Running the Full Check

Here's a bash one-liner to run all searchable checks at once:

```bash
FILE="path/to/page.md"
echo "=== EM DASHES ===" && grep -n '—' "$FILE"
echo "=== CONTRAST FRAMING ===" && grep -ni "while \|although \|whereas " "$FILE"
echo "=== POETIC SHIFTS ===" && grep -ni "in a world\|in an era\|in a landscape\|in today's" "$FILE"
echo "=== ADVERB FREQUENCY ===" && grep -oP '\w+ly\b' "$FILE" | sort | uniq -c | sort -rn | head -15
echo "=== MARKETING CLICHES ===" && grep -ni "seamless\|robust\|game-chang\|innovative\|cutting-edge\|holistic\|comprehensive care\|state-of-the-art\|world-class" "$FILE"
echo "=== FORMULAIC TRANSITIONS ===" && grep -ni "let's explore\|let's dive\|now, let's\|let us turn\|without further" "$FILE"
echo "=== FORCED INSPIRATIONAL ===" && grep -ni "journey\|empower\|transform your\|unlock\|embrace\|take the first step" "$FILE"
```

Report findings as a summary: what was found, what was fixed, what was left intentionally (with reasoning).
