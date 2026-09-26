# Gmail labels: what they mean and which ones the skills use

Mailbox: michael@localhealthmarketing.com.au. Names below are exact; IDs are for tools that need them.

## Working states (the ones triage sets)

| Label | ID | Meaning | Set by |
|---|---|---|---|
| `*** !MICHAEL-ONGOING TASKS` | Label_6121901196225039984 | Live thread Michael is tracking. Should have a BasicOps task. | triage |
| `*** 4.  WAITING ON` | Label_5101339524772641509 | Michael replied, ball is with the other side. | triage after a draft is sent |
| `*** 5.  FYI` | Label_6375283272172258453 | Team is running it (Kristalyn, Jaimee, Josephine). Michael reads, does not act. | triage |
| `*** 9. Done` | Label_1592441423289156563 | Closed. | tidy, triage |
| `*** MEETING WRAP` | Label_2337352758932673166 | Client "Meeting Summary & Action Items" email. Keep only the latest per client. | triage, tidy |
| `***!MICHAEL-TO RESPOND` | Label_3971232719292769826 | Historical. Michael no longer uses it consistently; the brief replaces it. Triage clears it once a reply is sent. | tidy |
| `*** 3.  RESPONDED` | Label_1290455480436315101 | Unused (0 uses in last 30 days). Do not set. | none |

## Context labels (read, never set)

| Label | ID | Notes |
|---|---|---|
| `***MICHAEL: PERSONAL` | Label_324387867638877642 | Off limits. Count only. |
| `*** !MICHAEL: FYI` | Label_2512418631139868580 | Automated self-notes (sitemap rollouts). Noise. |
| `**BasicOps` | Label_704356553002425633 | Only ever on BasicOps notification emails. Does NOT mean a task exists for a client thread. |
| `*** 10. Subscriptions`, `*** 8.  Newsletters`, `Pabbly`, `Loom`, `*ASANA`, `Unroll.me/Unsubscribed` | | Noise. Skip in triage. |
| `Invoice`, `*** 6.  Financials`, `*** 7. Reports` | | Josephine's domain. Mention in brief only if a client is asking Michael directly. |

## Label discipline for the skills

- A thread is in exactly one working state at a time. Setting ONGOING TASKS removes FYI, Done, WAITING ON and vice versa.
- Archive = remove INBOX. The thread keeps its labels.
- The brief is the source of truth for "what needs Michael today", not the labels. Labels exist so Gmail search still works and so the team sees the same picture.
