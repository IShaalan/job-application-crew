# Achievements Template Reference

## `candidate/achievements.md` — Format

Create a skeleton with one placeholder entry per role that has bullets. Do not create entries for title-only roles.

```markdown
# [User's Name] — Achievements & Narratives

These stories feed the cover letter builder and help Claude choose the right narrative for each role.
Run `/job-application enrich` to flesh out these placeholders with full STAR stories.

---

## [Role Title] | [Company] — "[Placeholder — run /job-application enrich to add detail]"

**Added:** YYYY-MM-DD
**Tags:** []

**One-liner:** [To be filled via enricher]

**The Full Story:**

[To be filled via enricher]

**The Challenge:**

- [To be filled]

**My Approach:**

- [To be filled]

**The Outcome:**

- [Must include at least one metric]

**What I Learned:**

[To be filled]

---
```

## Rules for `achievements.md`

- Repeat the template for each role with bullets
- If the user provided any achievement details during import (Path B, question 3), populate those entries with the available information instead of pure placeholders
- Do NOT create entries for title-only roles
- Do NOT fabricate STAR stories from bullet text — the enricher skill deepens them later
- Each entry should include the role title and company name for easy reference
