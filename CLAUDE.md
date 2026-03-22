# CLAUDE.md - Contributor Guide

## 1. Project Overview

job-application-crew is a Claude Code plugin that provides an AI-powered job application workflow. It generates targeted resumes and cover letters using the candidate's profile data, a positioning strategy, and an iterative review process.

This file is for contributors who clone the repo for development. Plugin users receive instructions through skill and command file content, not through this CLAUDE.md.

## 2. Plugin Structure

```
.claude-plugin/plugin.json    # Plugin manifest
commands/job-application.md   # Main workflow command (user-invocable)
skills/*/SKILL.md             # 9 skills (auto-discovered by Claude Code)
starter-kit/                  # Templates copied to user's project on init
scripts/                      # Export utilities (Python)
examples/                     # Sample data and complete application walkthrough
```

### Skills (9 total)

| Skill | Purpose |
|-------|---------|
| `onboarder` | First-run setup: creates candidate files from user input |
| `enricher` | Expands profile.yaml achievements into STAR narratives |
| `researcher` | Company + job description research |
| `resume-builder` | Generates targeted resume drafts |
| `resume-reviewer` | Critical review with ATS/Recruiter/HM scoring |
| `cover-letter-builder` | Generates targeted cover letters |
| `cover-letter-reviewer` | Reviews cover letters for quality and accuracy |
| `final-package-reviewer` | Coherence check across resume + cover letter |
| `humanizer` | Detects and fixes AI-typical language |

## 3. File Ownership (for skill authors)

| File | Owns | Written by |
|------|------|-----------|
| `candidate/profile.yaml` | Career data only | Onboarder (initial), user edits |
| `candidate/achievements.md` | STAR narratives | Enricher (primary), onboarder (skeleton) |
| `candidate/resume-config.yaml` | Contact, preferences, fixed/dynamic rules | Onboarder (initial), user edits |

Rules:
- `profile.yaml` does NOT contain contact info -- that lives in `resume-config.yaml`.
- `achievements.md` is the SINGLE source for STAR stories. Skills must read stories from here, never fabricate them.
- `resume-config.yaml` replaces the old `preferences.md`. It holds contact details, formatting preferences, fixed-content sections, and title-only role declarations.

## 4. Resume Rules (for skill authors)

- **Title must match job posting exactly.** If the job says "Senior Product Manager", the resume title is "Senior Product Manager" -- not "Principal PM" or a creative variation.
- **Bullet formula**: `[Strong Verb] + [What You Did] + [Result/Impact]`.
- **All bullets end with "."** -- no exceptions.
- **Short month format**: Use "Dec 2025" not "December 2025".
- **No first-person pronouns**: No I, my, me, we, our anywhere in the resume.
- **Contact line format**: `{email} | {phone} | {location} | [{linkedin_text}]({linkedin_url}) | [{website_text}]({website_url})`
  - Email is plain text (no mailto: link).
  - LinkedIn and website are markdown hyperlinks.
- **Every bullet must have a quantified outcome.** If no metric exists in the source data, describe the scope or scale honestly -- do not invent a number.

## 5. Never Fabricate

This is a hard rule across all skills:

- Do not invent metrics or outcomes. If `achievements.md` and `profile.yaml` do not contain a number, do not make one up.
- Do not inflate years of experience.
- Do not claim expertise the candidate does not have.
- Do not add tools, frameworks, or certifications not present in the candidate's profile.
- If a bullet needs a metric and none exists, use an honest scope signal (e.g., "across 50+ clients") rather than a fabricated percentage.

## 6. Review Framework

Every resume review must use 3 lenses and assign numeric scores:

- **ATS Review (X/10)**: List 3 specific reasons the resume might fail ATS screening.
- **Recruiter 5-Second Scan (X/10)**: List 3 reasons a recruiter might reject within 5 seconds.
- **Hiring Manager Review (X/10)**: List 3 reasons a hiring manager might pass (decide not to hire).

Do NOT be agreeable. Find real problems. A review that says "looks great" with 10/10 scores is a failed review.

## 7. Grammar/Article Pass

Required before finalizing any document (resume or cover letter):

- Check every bullet and sentence for missing or extra articles (a, an, the).
- Check prepositions (in, on, at, for, with, to).
- Flag AI-typical phrasing artifacts (e.g., "leverage", "utilize", "drive synergies", "passionate about").
- This pass runs on BOTH resume and cover letter before the final checkpoint.

## 8. Version Immutability

Draft files are immutable once created. The correct sequence for iterations:

1. `cp drafts/resume-vN.md drafts/resume-vN+1.md` -- copy first.
2. Edit only `vN+1` -- never touch `vN` after it exists.
3. Review artifacts save to `artifacts/review-vN.md` immediately after each review -- never deliver review results only in conversation.

This preserves diff history and prevents losing earlier versions.

## 9. Workflow (10 phases, 3 checkpoints)

```
Phase 1:  Input            Collect job posting URL or text
Phase 2:  Research          Company + JD research (web search)
Phase 3:  Strategy          Build positioning strategy
          --- CHECKPOINT 1: User approves strategy ---
Phase 4:  Resume Build      Generate resume draft
Phase 5:  Resume Review     Critical review, iterate until approved
          --- CHECKPOINT 2: User approves resume ---
Phase 6:  Cover Letter      Generate cover letter
Phase 7:  CL Review         Cover letter review, iterate
Phase 8:  Final Package     Coherence check (resume + CL together)
          --- CHECKPOINT 3: User gives final approval ---
Phase 9:  Export            Generate DOCX or Google Doc
Phase 10: Retrospective     Log learnings for future applications
```

The reviewer loop (Phases 5, 7) runs automatically after each build. It does not wait for the user to request a review. The loop ends when the reviewer issues an APPROVED verdict or the user intervenes.

## 10. Fixed Content Rules

Users can declare fixed-content sections and title-only roles in `resume-config.yaml`. These create binding constraints on builders and reviewers:

- **Builders MUST insert `fixed_content` text verbatim.** Do not rephrase, reorder, or "improve" fixed bullets.
- **Builders MUST NOT generate bullets for `title_only_roles`.** These entries appear as title/company/dates only -- no bullet points.
- **Reviewers MUST NOT flag `fixed_content` for revision.** These bullets are locked by the user.
- **Reviewers MAY note strategic conflicts** -- e.g., "this fixed bullet conflicts with the target role's priorities" -- but must not rewrite.

## 11. Contributing

### Role Packs
Add new role pack files to `starter-kit/knowledge/role-packs/`. Follow the existing format (see `product-manager.md`). Each role pack should include: role subtypes, what hiring managers look for, positioning angles, and common keywords.

### Review Patterns
Add anonymized patterns to `starter-kit/knowledge/review-patterns.md`. Include the pattern, why it matters, and the fix. Do not include candidate names, company names, or other identifying details.

### Bullet Examples
Add proven bullet phrasings to `starter-kit/knowledge/bullet-library.yaml`. Group by skill area or achievement type.

### Skills
New skills go in `skills/{skill-name}/SKILL.md` with YAML frontmatter. Follow the format of existing skills. Each skill file must be self-contained -- it is the only instruction surface for plugin users.

### Sample Data
Update files in `examples/` to reflect any new features or format changes.

## 12. What NOT to Include

This is a public repository. Never commit:

- Personal candidate data (real names, email addresses, phone numbers, employer names)
- Company-specific learnings with identifiable details
- Google Drive folder IDs, API keys, or credentials
- Token files (`token*.json`, `credentials.json`)
- Anything that belongs in the user's `candidate/` directory (gitignored for this reason)

The `.gitignore` already excludes `/candidate/`, `/jobs/`, `/config/`, `venv/`, `token*.json`, and `credentials.json`. Do not weaken these exclusions.
