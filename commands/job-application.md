---
name: job-application
description: AI-powered resume and cover letter workflow for job applications. Sub-commands: init (setup), enrich (profile management), update-knowledge (sync plugin knowledge), or pass a job URL/text to run the full workflow. Also supports: research, build, cover-letter, export to re-run individual phases.
---

# /job-application Command

This command orchestrates a full resume and cover letter workflow for job applications. It reads candidate data, researches companies, builds targeted resumes and cover letters, reviews them with automated scoring, and exports final documents.

## Entry Point: Detect Sub-command

When the user runs `/job-application`, check the argument:

- `init` → Invoke the `onboarder` skill (below)
- `enrich` → Invoke the `enricher` skill (below)
- `enrich --edit` → Invoke the `enricher` skill in edit mode
- `enrich --remove` → Invoke the `enricher` skill in remove mode
- `update-knowledge` → Run the update-knowledge flow (below)
- `research` → Run Phase 2 only for the current in-progress job
- `build` → Run Phase 4 only (resume build+review loop)
- `cover-letter` → Run Phase 6 only (cover letter build+review loop)
- `export` → Run Phase 9 only (export)
- `export --format docx` → Export as DOCX via `scripts/generate_docx.py`
- `export --format gdrive` → Export to Google Drive via `scripts/create_google_doc.py`
- A URL or job posting text → Run the Pre-flight Check, then the Full Workflow (below)
- A job name (matching an existing `{jobs_dir}/{job_id}/` directory) → Run the Pre-flight Check, then resume the in-progress workflow
- No argument → Show usage help:
  ```
  job-application-crew plugin commands:
    /job-application init                    — Set up candidate profile (run once)
    /job-application enrich                  — Add new experience or achievement
    /job-application enrich --edit           — Edit an existing profile entry
    /job-application enrich --remove         — Remove a profile entry
    /job-application update-knowledge        — Merge latest plugin knowledge into local files
    /job-application [URL or text]           — Run full workflow for a job posting
    /job-application [job name]              — Resume in-progress workflow
    /job-application research                — Re-run research phase for current job
    /job-application build                   — Re-run resume build phase for current job
    /job-application cover-letter            — Re-run cover letter phase for current job
    /job-application export                  — Re-run export phase for current job
    /job-application export --format docx    — Export as DOCX
    /job-application export --format gdrive  — Export to Google Drive
  ```

---

## Pre-flight Check (runs before every application)

Before starting or resuming any job application workflow, run these checks:

### 1. Profile exists?
Check if `candidate/profile.yaml` exists. If not:
```
No candidate profile found. Run /job-application init to set up your profile first.
```
Stop — do not proceed.

### 2. Achievements health check
Read `candidate/achievements.md`. Check if ALL entries are placeholders (contain "To be filled" or have empty Situation/Task/Action/Result fields).

If all entries are placeholders:
```
Your achievement stories are all placeholders — this means your cover letters
will be generic and miss the personal depth that makes candidates stand out.

Want to add a few stories before we start? (takes about 5 minutes per story)

  A) Yes — let's add 1-2 stories for my strongest roles
  B) Skip — proceed with the application anyway
```

If the user picks A → invoke the enricher skill for their most recent role, then continue to the workflow.
If the user picks B → proceed, but note that the strategist will flag thin stories again during the strategy phase.

If at least some entries have real content → proceed without prompting.

---

## Init Flow (`/job-application init`)

**Purpose:** Set up the candidate profile and configure the plugin for this repo. Delegates to the `onboarder` skill.

Spawn the `onboarder` skill as a subagent (Task tool, subagent_type="general-purpose"). Provide:
- The full onboarder skill instructions as the task prompt
- The current working directory path
- Whether `candidate/resume-config.yaml` already exists (and its contents if so)
- Whether `candidate/profile.yaml` already exists
- Whether `candidate/achievements.md` already exists
- Instruction to write config to `candidate/resume-config.yaml`

The onboarder skill handles all interactive prompts and file creation.

---

## Enrich Flow (`/job-application enrich`)

**Purpose:** Add, edit, or remove entries in the candidate profile. Delegates to the `enricher` skill.

Spawn the `enricher` skill as a subagent (Task tool, subagent_type="general-purpose"). Provide:
- The full enricher skill instructions as the task prompt
- The mode: `add` (default), `edit` (if `--edit` flag), or `remove` (if `--remove` flag)
- Full content of `candidate/profile.yaml`
- Full content of `candidate/achievements.md`
- Full content of `candidate/resume-config.yaml` (for path resolution)

The enricher skill handles all interactive prompts and file updates.

---

## update-knowledge Sub-command (`/job-application update-knowledge`)

**Purpose:** Merge baseline knowledge from the plugin's starter-kit into local knowledge files, using an append-only strategy with deduplication.

### Merge Algorithm

1. Read baseline files from `${CLAUDE_PLUGIN_ROOT}/starter-kit/knowledge/`
2. Read local `knowledge/` files
3. For each baseline file, find content blocks (by section headers) that exist in baseline but not in local
4. Append missing blocks to end of local file with a `## [Updated from plugin v{version}]` marker
5. Never delete or modify existing local content
6. Report: "Added N new sections to review-patterns.md, M new entries to bullet-library.yaml"

### Steps

1. **Load plugin version:** Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and extract the `version` field.

2. **Process review-patterns.md:**
   - Read `${CLAUDE_PLUGIN_ROOT}/starter-kit/knowledge/review-patterns.md`
   - Read local `knowledge/review-patterns.md` (create if missing)
   - Compare section headers (lines starting with `## `)
   - For each section in baseline not found in local, append the full section block
   - Prepend appended content with `## [Updated from plugin v{version}]` marker
   - Count and report sections added

3. **Process bullet-library.yaml:**
   - Read `${CLAUDE_PLUGIN_ROOT}/starter-kit/knowledge/bullet-library.yaml`
   - Read local `knowledge/bullet-library.yaml` (create if missing)
   - Compare top-level YAML keys
   - For each key in baseline not found in local, append the full entry
   - Add a comment `# [Updated from plugin v{version}]` before appended content
   - Count and report entries added

4. **Process role-packs (read-only sync):**
   - Read `${CLAUDE_PLUGIN_ROOT}/starter-kit/knowledge/role-packs/` directory
   - For each `.md` file in baseline role-packs not found in local `knowledge/role-packs/`, copy it
   - Never modify existing local role-pack files — those are curated content
   - Report: "Added N new role packs"

5. **Output summary:**
   ```
   Knowledge update complete (plugin v{version}):
   - review-patterns.md: Added {N} new sections
   - bullet-library.yaml: Added {M} new entries
   - role-packs: Added {P} new packs
   ```

---

## Full Workflow (`/job-application [job URL or text]`)

### Step 0: Load Config

Read `candidate/resume-config.yaml` from CWD. If not found:
```
Config not found. Run `/job-application init` first to set up your candidate profile.
```
Abort.

Verify `candidate/profile.yaml` exists. If not, warn and abort:
```
profile.yaml not found at candidate/profile.yaml.
Please run `/job-application init` to set up your candidate profile.
```

### Step 1: Parse Job Posting

If argument is a URL → use WebFetch to fetch the page content.
If argument is pasted text → use directly.

Extract:
- Company name
- Role title
- Full job posting text

Create `job_id` by slugifying: `{company-slug}-{role-slug}` (lowercase, hyphens, no special chars).
Example: `acme-corp-senior-pm`

### Step 2: Check for In-Progress Workflow

Check if `{jobs_dir}/{job_id}/workflow-state.yaml` exists.

If it exists, read `current_phase` and `created_at`, then use AskUserQuestion:
- "Found in-progress application: [Company] — [Role] (started [date], currently at: [phase]). What would you like to do?"
- Options: "Continue from [phase]" / "Reset and start fresh"

If Reset → remove the existing job directory and start fresh.
If Continue → jump to the phase indicated by `current_phase` in workflow-state.yaml.

### Step 3: Setup Workspace (fresh start only)

Create directory structure:
```
{jobs_dir}/{job_id}/
├── job-posting.md          ← write job posting here ONCE, never overwrite
├── workflow-state.yaml
├── artifacts/
├── drafts/
└── final/
```

Initialize `workflow-state.yaml`:
```yaml
job_id: "{job_id}"
company: "{company}"
role: "{role}"
created_at: "{ISO timestamp}"
current_phase: "research"
checkpoints:
  strategy:
    status: "pending"
    approved_at: ~
  resume:
    status: "not_started"
    current_version: 0
    max_iterations: 2
  cover_letter:
    status: "not_started"
    current_version: 0
    max_iterations: 2
  final:
    status: "not_started"
artifacts:
  research: ~
  strategy: ~
  resume_reviews: []
  cover_letter_reviews: []
human_context: []
```

---

## Phase 2: Research & Strategy

Spawn the `researcher` skill as a subagent (Task tool, subagent_type="general-purpose"). Provide:
- The full researcher skill instructions as the task prompt
- Job posting content
- Company name
- First 100 lines of `candidate/profile.yaml` as candidate summary
- Full content of `knowledge/strategy-playbook.md` (if exists)
- Instruction to write output to `{jobs_dir}/{job_id}/artifacts/research.md`

After the researcher completes, create `{jobs_dir}/{job_id}/artifacts/strategy.md`:

```markdown
# Application Strategy: {Company} — {Role}

## Positioning
[Primary angle — one sentence]

## Key Themes
1. [Theme 1]: [Which experiences, why it matters]
2. [Theme 2]: ...
3. [Theme 3]: ...

## Summary Direction
### What does this HM most need?
- [Need 1]
- [Need 2]
### Role's Language to Mirror
- "[exact phrase from JD]"
### Best Match for This Role
- [Which candidate experience speaks directly]
### Causality to Show
- [What background causes them to be good at this]
### Draft Summary Direction
[2-3 sentences of guidance — NOT a template to fill in]

## Keywords (Tier 1 — must include)
[Critical ATS keywords]

## Keywords (Tier 2 — include if natural)
[Secondary keywords]

## Stories to Feature
- Resume: [Achievement IDs from profile.yaml]
- Cover letter: [Narrative from achievements.md]

## Tone
[Based on company culture]

## Notes
[Special considerations]
```

Update `workflow-state.yaml`: `current_phase: "checkpoint_strategy"`, set `artifacts.research` and `artifacts.strategy` paths.

---

## Checkpoint 1: Strategy Review

Present to user:
```
## Research Complete: [Company] — [Role]

### Company Overview
[2-3 sentence summary from research.md]

### Proposed Strategy
[Full content of strategy.md]

### Questions for You
1. Does this positioning resonate with how you want to present yourself?
2. Does the summary direction capture the right angle?
3. Any context about this role/company I should know?
4. Specific achievements you want emphasized?
```

Use AskUserQuestion with options:
- "Looks good — proceed to resume"
- "I have modifications to the strategy"
- "Redirect the strategy entirely"

If modifications → ask user what to change, update strategy.md, add note to `human_context` in workflow-state.yaml.
If redirect → return to Phase 2 with new direction.
If approved → update `workflow-state.yaml`: `checkpoints.strategy.status: "approved"`, set `approved_at`.

---

## Phase 4: Resume Build Loop

Maximum 2 iterations. Track in `checkpoints.resume.current_version`.

### Each iteration:

**Build step:** Spawn `resume-builder` skill as subagent with:
- Full resume-builder skill instructions as task prompt
- Full content of `{jobs_dir}/{job_id}/artifacts/strategy.md`
- Full content of `candidate/profile.yaml`
- Full content of `knowledge/bullet-library.yaml` (if exists)
- Applicable role pack from `knowledge/role-packs/` (if one matches the role type)
- Content of `candidate/resume-config.yaml` (for formatting preferences)
- Content of previous review (only if iteration > 1)
- Instruction to write:
  - `{jobs_dir}/{job_id}/drafts/resume-v{n}.md`
  - `{jobs_dir}/{job_id}/artifacts/resume-rationale-v{n}.md`

**Review step:** Spawn `resume-reviewer` skill as subagent with:
- Full resume-reviewer skill instructions as task prompt
- Full content of `{jobs_dir}/{job_id}/drafts/resume-v{n}.md`
- Full content of `{jobs_dir}/{job_id}/artifacts/strategy.md`
- Original job posting text
- Full content of `knowledge/review-patterns.md` (if exists)
- Instruction to write output to `{jobs_dir}/{job_id}/artifacts/resume-review-v{n}.md`
- Instruction to end the review with exactly one of:
  - `VERDICT: APPROVED`
  - `VERDICT: NEEDS REVISION`

**Loop decision:** Read the last line of the review file.
- `VERDICT: APPROVED` → exit loop
- `VERDICT: NEEDS REVISION` and current_version < 2 → increment version, loop
- `VERDICT: NEEDS REVISION` and current_version = 2 → exit loop (still present to human)

**Version immutability rule:** Once `resume-v{n}.md` is created, never edit it in-place. Each reviewer iteration must create a new `v{n+1}` file. Use `cp drafts/resume-v{n}.md drafts/resume-v{n+1}.md` first, then edit only the new file.

Update `workflow-state.yaml` after each iteration.

---

## Checkpoint 2: Resume Approval

Present to user:
```
## Resume Ready for Review

### Final Version (v{n})
[Full content of drafts/resume-v{n}.md]

### Build Summary
- Iterations run: {n}
- Reviewer verdict: [APPROVED / NEEDS REVISION]
- Key findings: [3-bullet summary from the review]

### Questions
1. Does this accurately represent your experience?
2. Any specific bullets you want to adjust?
3. Ready to proceed to cover letter?
```

Use AskUserQuestion:
- "Approved — proceed to cover letter"
- "I have specific changes to request"
- "Run another revision iteration"

If changes → make edits to a new version file, re-run reviewer, re-present.
If another iteration → increment max_iterations, loop Phase 4.
If approved → update `workflow-state.yaml`: `checkpoints.resume.status: "approved"`.

---

## Phase 6: Cover Letter Build Loop

Same loop structure as Phase 4 (maximum 2 iterations).

**Build step:** Spawn `cover-letter-builder` skill as subagent with:
- Full cover-letter-builder skill instructions as task prompt
- Full content of approved resume (`drafts/resume-v{n}.md`)
- Full content of `{jobs_dir}/{job_id}/artifacts/strategy.md`
- Full content of `{jobs_dir}/{job_id}/artifacts/research.md`
- Full content of `candidate/profile.yaml`
- Full content of `candidate/achievements.md`
- The `human_context` array from workflow-state.yaml
- Content of `candidate/resume-config.yaml` (for formatting preferences)
- Instruction to write:
  - `{jobs_dir}/{job_id}/drafts/cover-letter-v{n}.md`
  - `{jobs_dir}/{job_id}/artifacts/cover-letter-rationale-v{n}.md`

**Review step:** Spawn `cover-letter-reviewer` skill as subagent with:
- Full cover-letter-reviewer skill instructions as task prompt
- Full content of cover letter draft
- Full content of approved resume
- Full content of strategy.md
- Instruction to write `{jobs_dir}/{job_id}/artifacts/cover-letter-review-v{n}.md`
- Instruction to end with `VERDICT: APPROVED` or `VERDICT: NEEDS REVISION`

**Version immutability rule:** Same as resume — never edit a version file in-place. Always create a new version.

---

## Phase 7: Humanizer Pass

Spawn `humanizer` skill as subagent with:
- Full humanizer skill instructions as task prompt
- Full content of final resume draft
- Full content of final cover letter draft
- Full content of `candidate/resume-config.yaml` (for voice and style preferences)
- Instruction to write `{jobs_dir}/{job_id}/artifacts/humanizer-report.md`
- Instruction to apply obvious fixes directly to draft files; flag ambiguous issues in the report

---

## Checkpoint 3: Final Package Review

Spawn `final-package-reviewer` skill as subagent with:
- Full final-package-reviewer skill instructions as task prompt
- Final resume content
- Final cover letter content
- Strategy content
- Instruction to write `{jobs_dir}/{job_id}/artifacts/final-package-review.md`

Present to user:
```
## Final Package Ready

### Resume
[Full content of final resume]

### Cover Letter
[Full content of final cover letter]

### Coherence Analysis
[Summary from final-package-review.md]

### Humanizer Report
- Fixed: [list of auto-fixed issues]
- Flagged for your review: [list of ambiguous items, if any]

Ready to export?
```

Use AskUserQuestion:
- "Approve and export"
- "Make final adjustments to resume"
- "Make final adjustments to cover letter"
- "Run more iteration on both"

Update `workflow-state.yaml`: `checkpoints.final.status: "approved"`.

---

## Phase 9: Export

### Detect export format

If the user ran `/job-application export --format docx`, use DOCX export only.
If the user ran `/job-application export --format gdrive`, use Google Drive export only.
Otherwise, run all available export steps.

### Steps

1. **Save final files:**
   Copy latest resume draft → `{jobs_dir}/{job_id}/final/resume.md`
   Copy latest cover letter draft → `{jobs_dir}/{job_id}/final/cover-letter.md`

2. **DOCX generation** (if `scripts/generate_docx.py` exists):
   ```bash
   python scripts/generate_docx.py --content {jobs_dir}/{job_id}/final/resume.md --type resume
   python scripts/generate_docx.py --content {jobs_dir}/{job_id}/final/cover-letter.md --type cover-letter
   ```

3. **Google Drive upload** (only if `google_drive: true` in config AND `scripts/create_google_doc.py` exists):
   ```bash
   python scripts/create_google_doc.py --content {jobs_dir}/{job_id}/final/resume.md --type resume --company "{company}" --role "{role}"
   python scripts/create_google_doc.py --content {jobs_dir}/{job_id}/final/cover-letter.md --type cover-letter --company "{company}" --role "{role}"
   ```

Present final output with all file paths and Drive links (if applicable).

---

## Phase 10: Retrospective

After export, automatically capture learnings. This phase is automatic — no user checkpoint needed.

1. **Review patterns** — append to `knowledge/review-patterns.md`:
   - Any resume review issues caught and fixed (e.g., "missing ATS keyword", "bullet too long")
   - Format: new entry with `## Application: {date} — {role-type}` header

2. **Bullet library** — append to `knowledge/bullet-library.yaml`:
   - Any bullets that scored 8+ in review, categorized by role type

3. **Strategy playbook** — if a novel positioning angle was used, append to `knowledge/strategy-playbook.md`.

4. Do NOT modify role pack files — those are curated content.

5. Write `{jobs_dir}/{job_id}/retrospective.md`:
   ```markdown
   # Retrospective: {Company} — {Role}
   ## Summary
   - Created: {date}
   - Resume iterations: {n}
   - Cover letter iterations: {n}
   ## Strategy Used
   [Summary of positioning angle]
   ## What Worked
   - [Bullets/strategies approved without changes]
   ## What Changed
   - [Human modifications at checkpoints]
   - [Reviewer-caught issues]
   ## Learnings Captured
   - Added to bullet-library: {count} bullets
   - Added to strategy-playbook: yes/no
   - Added to review-patterns: {count} patterns
   ```

6. Update `workflow-state.yaml`: `current_phase: "complete"`.

---

## Granular Sub-commands

### `/job-application research`

1. Load `candidate/resume-config.yaml`
2. Find the most recently modified job in `{jobs_dir}/` with `current_phase` not "complete" — or ask user which job if multiple in-progress
3. Re-run Phase 2 only (research + strategy creation)
4. Present updated strategy at Checkpoint 1

### `/job-application build`

1. Load config, find current job
2. Verify `artifacts/strategy.md` exists — if not, error: "Run `/job-application research` first"
3. Re-run Phase 4 only (resume build + review loop)
4. Present at Checkpoint 2

### `/job-application cover-letter`

1. Load config, find current job
2. Verify approved resume exists — if not, error: "Approve resume first via Checkpoint 2"
3. Re-run Phase 6 only (cover letter build + review loop)

### `/job-application export`

1. Load config, find current job
2. Use files from `final/` if they exist, otherwise use latest drafts
3. Check for `--format` flag:
   - `--format docx` → run DOCX generation only via `scripts/generate_docx.py`
   - `--format gdrive` → run Google Drive upload only via `scripts/create_google_doc.py`
   - No flag → run all available export steps
4. Re-run Phase 9 only (export)
