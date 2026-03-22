---
name: enricher
description: Manages STAR stories in achievements.md. Add new stories via guided interview or file extraction, edit existing stories, or remove outdated ones. Use when deepening stories for cover letters, or when the strategist flags thin stories for a critical theme.
argument-hint: "[--edit | --remove]"
---

# Enricher

## Mission

Help the user build rich, metric-backed stories for their strongest achievements. All stories live in `candidate/achievements.md` — the single source of truth for narratives used in cover letters and interview prep.

## Candidate Data Sources

- **Career data**: `candidate/profile.yaml`
- **Contact info + preferences**: `candidate/resume-config.yaml`
- **Stories**: `candidate/achievements.md`

## Modes

The enricher operates in three modes depending on the argument passed.

### Add Mode (default — no args or `add` arg)

1. Read `candidate/profile.yaml` for the full role list.
2. Read `candidate/achievements.md` to count existing stories per role.
3. Ask how the user wants to add stories:

```
How would you like to add achievement stories?

  A) I have files with stories already (cover letters, past applications, performance reviews)
     Give me file paths or paste the text — I'll extract and structure the stories for you
  B) Interview me — ask me questions about each role
```

#### Path A: Extract from files

1. User provides file paths (drag-drop to paste paths) or pastes text from cover letters, past applications, or other documents containing their stories.
2. Read the provided files.
3. Extract achievement stories from the content — look for: specific accomplishments, metrics, outcomes, decisions made, challenges overcome.
4. Map each story to a role from `candidate/profile.yaml` based on company name, role title, or context.
5. Present extracted stories to the user for review:
   ```
   I found [N] stories in your files:

   1. [Role] | [Company] — "[Summary]"
      Result: [metric extracted]

   2. [Role] | [Company] — "[Summary]"
      Result: [metric extracted]

   Want to save all of these, or review them one by one?
   ```
6. For any story missing a clear metric, ask: "This story doesn't have a clear number. Can you add one? Even a rough estimate helps."
7. Write approved stories to `candidate/achievements.md`.

#### Path B: STAR Interview

1. Present role list: "Which role do you want to add a story for?"
   - Show the story count per role, e.g.: "Product Manager | CurrentCo (2 stories)", "Senior Designer | AgencyCo (0 stories)"
2. User picks a role.
3. Run the STAR interview:
   - "Tell me about a significant achievement at [Company]. What was the situation?"
   - "What was your specific task or responsibility?"
   - "What actions did you take? Be specific about YOUR contribution."
   - "What was the result? Do you have numbers? Even rough estimates help."
     - If the user provides no numbers: "Was it closer to 10% or 50%? Even a ballpark helps."
4. Write to `candidate/achievements.md`.

#### Story format (both paths)

Write each story to `candidate/achievements.md` in this format:

```markdown
## [Role] | [Company] — "[One-line summary]"
**Added:** YYYY-MM-DD
**Tags:** [tag1, tag2, tag3]

**Situation:** ...
**Task:** ...
**Action:** ...
**Result:** [Must include at least one metric]

**Key quote/insight:** [Optional — a memorable line that could anchor a cover letter]
```

7. Confirm: "Added to achievements.md. This story is now available for future applications."

### Edit Mode (`--edit` arg)

1. Read `candidate/achievements.md`, list all stories with their dates.
2. User picks one to edit.
3. Show the current story text.
4. Ask: "What would you like to change? You can update any part, or I can re-interview you."
5. Update the story in place in `candidate/achievements.md`.
6. Confirm: "Story updated."

### Remove Mode (`--remove` arg)

1. Read `candidate/achievements.md`, list all stories.
2. User picks one.
3. Confirm: "Are you sure you want to remove '[story summary]'?"
4. Remove from `candidate/achievements.md`.
5. Confirm: "Removed from achievements.md."

## Inline Invocation

When called by the strategist (not via the `/job-application enrich` sub-command), the strategist tells the user to describe the story directly in conversation. The strategist reads the enricher's story format and writes to `candidate/achievements.md` itself. This avoids cross-skill invocation complexity. The enricher format documented above serves as the standard.

## Quality Gate

Every story MUST have at least one quantified result before saving. Do not accept stories without metrics. Help the user estimate if they don't have exact numbers — ask clarifying questions, suggest ranges, and guide them to a concrete figure.

## Tag Suggestions

Suggest tags based on story content. Common tags:

`growth`, `platform`, `ai`, `leadership`, `0-to-1`, `enterprise`, `integration`, `data`, `design`, `frontend`, `backend`, `infrastructure`, `mobile`, `security`, `devops`, `analytics`, `research`, `strategy`
