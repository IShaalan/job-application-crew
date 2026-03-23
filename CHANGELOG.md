# Changelog

## 1.1.0 (2026-03-22)

- Use Skill tool invocations instead of manual subagent spawning (major performance fix)
- Add no-bash rule to all analysis skills
- Add user-configurable workflow settings (builder/reviewer model, max iterations)
- Add export setup step to onboarding wizard (DOCX, Google Drive)
- Add pre-flight achievement health check before every application
- Add version sub-command
- Fix onboarder: faster bootstrap, better import prompt, show actual content in fixed/dynamic step
- Fix skill frontmatter: context:fork, user-invocable, model/effort settings
- Update README for local plugin usage (--plugin-dir)

## 1.0.0 (2026-03-22)

Initial release.

- 9 skills: onboarder, enricher, researcher, resume-builder, resume-reviewer, cover-letter-builder, cover-letter-reviewer, final-package-reviewer, humanizer
- 3 role packs: Product Manager (battle-tested), Software Engineer (seed), Designer (seed)
- Export options: Markdown (default), DOCX (optional), Google Drive (optional)
- Baseline knowledge from 95+ real PM applications (anonymized)
- File-based story extraction from existing cover letters and documents
