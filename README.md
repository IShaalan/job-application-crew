# job-application-crew

Your AI-powered job application crew. Research, resume, cover letter -- one command.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blue.svg)]()

## Built from experience

This system was refined over 95+ real job applications. The PM role pack is battle-tested. Software Engineer and Designer packs are seed content that improves with use.

## Quick Start

```bash
# 1. Install the plugin
claude plugin add shaalan-sam/job-application-crew

# 2. Create a directory for your job search
mkdir my-job-search && cd my-job-search

# 3. Start Claude Code from that directory
claude

# 4. Inside Claude Code, set up your profile (one-time)
/job-application init

# 5. Apply to a job
/job-application <paste job posting URL or text>
```

## How It Works

Each application runs through a 10-phase workflow with 3 human checkpoints:

1. **Input** -- Paste a job posting URL or text
2. **Research** -- Company deep-dive and JD analysis
3. **Strategy** -- Positioning, keyword tiers, fit score
4. CHECKPOINT 1: Review and approve strategy before building
5. **Resume Build** -- Targeted resume from your profile + strategy
6. **Resume Review** -- ATS / Recruiter / Hiring Manager scoring loop
7. CHECKPOINT 2: Review and approve resume before cover letter
8. **Cover Letter Build** -- Story-driven letter matched to strategy
9. **Cover Letter Review** -- Tone, accuracy, and coherence check
10. **Final Package Review** -- Cross-document consistency check
11. CHECKPOINT 3: Approve final package
12. **Export** -- Markdown, DOCX, or Google Drive
13. **Retrospective** -- Learnings feed back into your knowledge base

You stay in control at every checkpoint. The system builds, reviews, and iterates automatically between checkpoints.

## What You Get

For each application, the system produces:

- **Strategy doc** -- Company research, keyword tiers, positioning rationale
- **Targeted resume** -- ATS-optimized, reviewed against recruiter and hiring manager lenses
- **Cover letter** -- Story-driven, grounded in real experience
- **Review artifacts** -- Scores and improvement notes from each review pass

See a complete example in [`examples/sample-application/`](examples/sample-application/).

## Role Packs

| Pack | Status | Variants |
|------|--------|----------|
| **Product Manager** | Battle-tested (95+ applications) | AI PM, Technical PM, Growth PM, Platform PM, Enterprise PM, Startup Generalist PM |
| **Software Engineer** | Seed content | Backend, Frontend, Full-Stack, Platform/Infra, ML Engineer |
| **Designer** | Seed content | Product Designer, UX Researcher, Visual/Brand, Design Lead |

Role packs include tailored bullet libraries, review patterns, and strategy playbooks. The PM pack is production-grade. SE and Designer packs provide a solid starting point that improves as you use them.

## Commands

```
/job-application init                    # One-time profile setup
/job-application <job posting>           # Full workflow
/job-application research                # Re-run research phase
/job-application build                   # Re-run resume build
/job-application cover-letter            # Re-run cover letter
/job-application enrich                  # Add achievement stories
/job-application export                  # Export final files
/job-application export --format docx    # Export as DOCX
/job-application export --format gdrive  # Export to Google Drive
```

## Export Options

- **Markdown** (default) -- Copy-paste into any editor. No dependencies.
- **DOCX** (optional) -- Requires `pip install python-docx`.
- **Google Drive** (optional) -- Run `python scripts/setup_google_drive.py` for one-time OAuth setup.

## Privacy

All data stays on your machine. No telemetry, no uploads, no external API calls. Your candidate profile, job applications, and accumulated knowledge are local files only. The optional Google Drive export is the only feature that sends data externally -- and only when you explicitly choose it.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (requires a Claude Pro, Max, or Team subscription)
- Python 3.8+ (for export scripts, optional)

## How Your Knowledge Grows

Every application makes the system smarter. After each job application:

- **Review patterns** accumulate in `knowledge/review-patterns.md` -- common mistakes, what works for different role types, positioning insights.
- **Bullet library** grows in `knowledge/bullet-library.yaml` -- proven phrasings indexed by skill and domain.
- **Strategy playbook** expands in `knowledge/strategy-playbook.md` -- what framing works for AI PM vs. Platform PM vs. Growth PM.

By application 10, the system knows your strengths, your failure modes, and which stories land for which roles. By application 50, it writes first drafts that need minimal revision.

## Development

To test the plugin locally without installing from GitHub:

```bash
# Clone the repo
git clone https://github.com/shaalan-sam/job-application-crew.git

# Create a test directory
mkdir /tmp/test-job-search

# Run Claude Code with the local plugin
claude --plugin-dir ./job-application-crew --cwd /tmp/test-job-search

# Inside Claude Code, test the workflow
/job-application init
```

To reset and test again:

```bash
rm -rf /tmp/test-job-search && mkdir /tmp/test-job-search
```

## Contributing

Role packs improve with use. Contributions welcome -- especially from Software Engineer and Designer users who can help battle-test those packs. See [CLAUDE.md](CLAUDE.md) for contribution guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.

Built by [Sam Shaalan](https://shaalan.xyz).
