# Monthly Support Report — Runbook

Trigger phrase: **"generate the monthly support report"**

When the user says this, run the whole flow below **fully automatically — do NOT stop to
ask for confirmation.** Only pause if source data is genuinely missing (e.g. the Zendesk
Explore delivery email has not arrived). Reporting period = the **previous complete month**.

The package has two parts, both posted to Slack **#support-monthly** (channel id
`C0BJ820NKF0`): parent = **Volume Audit**, threaded reply = **Team Report**.

---

## Behaviour defaults (decided with Momoko, 2026-08)

- **Run without asking.** Standard flow is pre-authorised: compute → post to Slack →
  create email drafts. No clarifying questions for the normal case.
- **Slack posts go to #support-monthly** (Volume Audit = parent, Team Report = reply).
  Reports stay in the channel (not DM).
- **Emails are left as drafts** — this environment's Gmail connector can only create
  drafts, not send. The user sends them.
- The monthly **reminder** now DMs Momoko directly (Slack Workflow), not the channel.

---

## Part 1 — Volume Audit

Data source: the Zendesk Explore scheduled delivery email — from
`no-reply@zendeskexplore.com`, subject **"Your delivery of Monthly Support Volume Audit"**
— which lands on report day with attachments `..._Poe_...xlsx`, `..._Quora_...xlsx`,
`..._CSAT_...xlsx`.

Usually a scheduled automation has **already built the Volume Audit** by the time the user
runs the command: look for
- a self-email `"[Review] Monthly Support Volume Audit — <period>"`, and
- a **team draft** `"Monthly Support Volume Audit — <period>"` (to alecia@, shameed@, mfriedenberg@).

If those exist, **reuse them** — do not rebuild. If they don't, build the HTML digest from
the Explore attachments in the same format as prior months (see a previous
`Monthly Support Volume Audit` email as the template): product totals, per-form tables,
MoM vs the prior month, notable movers, cross-product mismatch footnote.

## Part 2 — Team Report (per-agent)

Computed live from the Zendesk **search** API. The connector caps every search at 100 rows
and returns no total, so **count via date windows** (weekly; split any window that returns
exactly 100 into shorter spans until every window is < 100, then sum).

Roster — **Support team only** (exclude Gustavo Zanetti & Juan Arroyo):

| Agent | assignee_id |
|---|---|
| Anna O'Sullivan | 29158434264212 |
| Tiffany Douangpanya | 9157211381140 |
| Momoko Friedenberg | 369822076772 |
| Antonia Christopoulou | 19171977008276 |
| Shifana Hameed | 406201988371 |

Brand ids: **Quora = 98645**, **Poe = 14512791042324**.

Per agent, over the report month:
- **Total Solved** = `type:ticket assignee:<id> solved>=<M-01> solved<<next-M-01>`, summed over windows.
- **Quora / Poe split** = same query with `brand_id:98645` / `brand_id:14512791042324`.
- **CSAT** = `assignee:<id> satisfaction:good ...` and `...satisfaction:bad...` over month-solved
  tickets → good ÷ (good+bad). Small samples (n≲3) are not meaningful — flag them.
- **Backlog** = snapshot `type:ticket assignee:<id> status<solved` (count now, not month-end).
- **MoM** vs last month's published Total Solved. Keep a trailing-12-month trend table
  (carry prior months from the previous Team Report email; append the new month).

**Omitted every run** (require the ticket-metrics / audit API, which this connector does
NOT expose): Median 1st Reply, Median Resolution, Reopen %, Public Replies, Internal Notes.
State this explicitly in the report; never fabricate them.

---

## Outputs

1. **Gmail drafts** (do not send):
   - `"[Review] Monthly Support Team Report — <Month> <Year>"` to self (mfriedenberg@quora.com),
     full HTML: TLDR box, scope note, data-source caveat, headline, per-agent table
     (Agent · Quora · Poe · Total · MoM · CSAT · Backlog), 12-month trend, methodology.
     **Use the May / June 2026 Team Report emails as the canonical layout** — copy their
     section order, table/column structure and styling exactly (bold via `**`, colours for
     +/− MoM). The only intended difference is the omitted metric columns noted above (state
     them as unavailable this run; do not silently drop the columns without a note).
   - The Volume Audit team draft (reuse the one already staged, or create it).
2. **Slack** — post to `#support-monthly` (`C0BJ820NKF0`): parent then threaded reply.

### Slack formatting — IMPORTANT

**The May / June 2026 posts are the canonical format** for both the parent and the reply —
match them exactly. The Slack connector interprets **standard Markdown**, so use
**`**double asterisks**` for bold** and `_underscores_` for italic. (A single `*word*`
renders as *italic*, which is the bug that made the July 2026 post look different from
May/June — do not repeat it.)

**Parent (Volume Audit):**
```
📊 **Monthly Support — <Month> <Year>**
**Volume Audit** — full digest emailed to the team
Totals: Poe **<poe>** · Quora **<quora>** · All **<all>**  (MoM <Month> vs <Prev>: <±x.x%>)
• Quora drives <~87>% of support; Quora Appeals alone ≈<xx>% of all volume
• <Month> direction: Poe <±x.x%> (<prev>→<cur>) · Quora <±x.x%> (<prev>→<cur>)
• Notable: <biggest increase>; <biggest decrease>
```

**Reply (Team Report), in the parent's thread:**
```
🧑‍💻 **Support Team Report — <Month> <Year>** (full report prepared for Momoko)
**Total solved: <total>**  (Quora <q> / Poe <p>)

**TLDR**
• Total <total> solved · Quora <q%> / Poe <p%> · <±x.x%> MoM
• <leader> led (<n>, <±x%>); <other notable movers>
• Watch: <MoM declines / highest backlog / weak CSAT>
**Per agent — Total · MoM · CSAT**
• <Agent>: <total> · <±x.x%> · <csat%> (<good>/<bad>)
  … (one line per agent, sorted by Total Solved)
_Support team only (Anna, Tiffany, Momoko, Antonia, Shifana). Median / reopen % /
reply-count metrics omitted this run (metrics API unavailable) — see email._
```

Slack auto-appends "Sent using @Claude"; don't add it manually.

---

## Gotchas learned (2026-08 first run)

- "the monthly support report" = **this** package. Not the Ads-only
  `Monthly_Support_Volume_Audit_Ads_*.xlsx` in Drive.
- 100-row search cap → **date-window** everything you count.
- Single `*` → italic in Slack via this connector → use `**` for bold.
- A month's Total Solved can be inflated by one-week bulk closes (e.g. `internal_test`,
  `auto_flagged` / `no_reply_close` batches). If a MoM swing looks odd, check the weekly
  shape before drawing conclusions.
