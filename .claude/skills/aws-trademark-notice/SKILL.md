---
name: aws-trademark-notice
description: "Handle an AWS Trust & Safety trademark notice (Doppel on behalf of Coinbase, Intuit and similar) about Quora pages. Splits the reported URLs into with-phone-number and without-phone-number groups, then drafts the English reply to AWS. Use when the user pastes an AWS abuse notice with 'Case ID' and '--- Report N ---' blocks, or says 'split the URLs', 'phone numbers', 'reply to AWS', 'URL ichiran'."
---

# AWS trademark notice

Input: one pasted AWS notice. Output: URL groups, then one reply draft.
Do not ask what the user wants. The paste alone starts this flow.

## 1. Split the URLs

1. Save the pasted text to a file in the scratchpad directory.
2. Run `python3 -I scripts/split_urls.py < <file>`.
3. Use the script output for every count and list. Do not count by hand.

The script reads the `--- Report N ---` blocks, not the header URL list.
The header list can miss reports or repeat the same URLs. It reports both cases as NOTE lines.

## 2. Report in Japanese, short

Show these items, in this order:

1. Case ID, report count, unique URL count, marks cited.
2. URLs with a phone number, then URLs without one. Use a plain code block for each group, in report order.
3. Phone numbers. Mark a number NEW if it did not appear in an earlier notice in this conversation.
4. Answer pages and regular question pages: tell the user to check them for fake support numbers. Pages under `/unanswered` need no check.
5. Profile pages: tell the user to suspend the account under the Spam policy. The nominative-use argument is weak for a profile named after a brand plus "Support".

If the Case ID matches an earlier notice and the reports match, say it is a resend. Do not repeat the analysis.

For a follow-up like "give me the URLs", output the latest notice's URLs as a plain code block in report order.

## 3. Draft the reply

Write the draft in English. Sign as the user. Keep it short. Do not list URLs in the reply.

```
Hi AWS Trust & Safety Team,

Thank you for your email regarding Case ID <ID>.

We have reviewed the reports. The reported questions and answers use the term <MARK> to refer to the company itself, not as a brand identifier or an indicator of the source of goods and services. We do not consider this to be trademark infringement.

<ACTION PARAGRAPHS>

If you discover additional content that you believe infringes your intellectual property rights, please report the location of that content via our infringement claim form at https://help.quora.com/hc/en-us/requests/new. We will review your complaint promptly, in accordance with our policies and applicable law.

Regards,
<user name>
Quora Support Team
```

- `<MARK>`: the mark in the notice. Write each mark if the notice cites several.
- `<ACTION PARAGRAPHS>`: use this rule.

<critical>
Never write that content was removed or that accounts were suspended unless the user said so in this conversation.
The reply goes to AWS. A false statement is worse than a short reply.
</critical>

| User said | Paragraph to add |
|---|---|
| Nothing about actions | Omit the paragraph |
| Questions were removed | "The content that violates our Spam policy has been removed accordingly." |
| Profiles were suspended | "The reported profile pages have been suspended under our Spam policy." |

If the notice has profile pages for a brand (for example a profile named after the brand plus "Support"), do not defend them as nominative use. Remove the nominative-use sentence for those pages, or limit it to the Q&A items.

After the draft, tell the user which action paragraphs are missing and why, in one line.

## Style

- Replies to the user: short Japanese. Avoid em-dashes. Avoid parentheses where possible.
- Do not write like an LLM. Use plain words.
- Do not write a per-URL breakdown in the email.
- Use `they/them` for people whose pronouns are unknown.
