# Review Patterns

Common issues caught by the reviewer agent. Updated automatically during retrospective phase.

---

## How This File Is Used

The resume and cover letter reviewers check for these patterns during every review. When the retrospective phase finds recurring issues, they're added here to prevent future occurrences.

---

## Product Management Specific Patterns

### PM-1: Missing Business Impact
**Pattern**: Bullets describe features shipped without business outcomes
**Example**: "Launched new onboarding flow for mobile app"
**Fix**: "Launched new onboarding flow, improving Day-7 retention from 35% to 48% and reducing support tickets by 30%"
**Severity**: HIGH

### PM-2: Engineering Language Instead of PM Language
**Pattern**: Bullets sound like an engineer wrote them
**Example**: "Implemented microservices architecture using Kubernetes"
**Fix**: "Drove adoption of microservices architecture, reducing deployment time from 2 weeks to 2 days and enabling 3x faster feature releases"
**Severity**: MEDIUM

### PM-3: Vague Stakeholder References
**Pattern**: "Worked with stakeholders" without specificity
**Example**: "Collaborated with cross-functional stakeholders"
**Fix**: "Aligned engineering, design, and marketing (15+ people) on 6-month roadmap, securing $2M budget allocation"
**Severity**: MEDIUM

### PM-4: Feature Factory Language
**Pattern**: Emphasis on shipping without strategic context
**Example**: "Shipped 12 features in Q3"
**Fix**: "Prioritized and shipped 12 features based on customer research, driving 25% increase in paid conversion"
**Severity**: MEDIUM

### PM-5: Missing Customer/User Connection
**Pattern**: No mention of customers, users, or research
**Example**: "Defined product requirements and led development"
**Fix**: "Conducted 40+ customer interviews to identify pain points, then defined requirements that addressed top 3 requests"
**Severity**: HIGH

---

## AI/ML Product Specific Patterns

### AI-1: Buzzword Without Substance
**Pattern**: AI/ML terms without concrete application
**Example**: "Leveraged AI to drive innovation in the product"
**Fix**: "Launched ML-powered recommendation engine, increasing average order value by 23%"
**Severity**: HIGH

### AI-2: Missing Model Performance Metrics
**Pattern**: AI features without accuracy/performance context
**Example**: "Built fraud detection system using machine learning"
**Fix**: "Built ML fraud detection achieving 94% precision at 85% recall, reducing false positives by 60%"
**Severity**: MEDIUM

### AI-3: Technical Without Business
**Pattern**: AI work described technically without business value
**Example**: "Trained transformer model on customer data"
**Fix**: "Trained NLP model for automated support triage, routing 70% of tickets correctly and reducing response time by 4 hours"
**Severity**: HIGH

---

## General Resume Patterns

### GEN-1: Passive Voice
**Pattern**: Achievement stated passively
**Example**: "The product roadmap was defined by me"
**Fix**: "Defined product roadmap..."
**Severity**: LOW

### GEN-2: Responsibility vs. Achievement
**Pattern**: Job description instead of accomplishment
**Example**: "Responsible for product strategy and roadmap"
**Fix**: "Developed product strategy that drove 40% revenue growth over 18 months"
**Severity**: HIGH

### GEN-3: Vague Scale Indicators
**Pattern**: "Large team", "significant growth", "major initiative"
**Example**: "Led large cross-functional team"
**Fix**: "Led 15-person cross-functional team"
**Severity**: MEDIUM

### GEN-4: Unsubstantiated Adjectives
**Pattern**: Claims without evidence
**Example**: "Exceptional product leader"
**Fix**: Remove adjective, show evidence through achievements
**Severity**: HIGH

### GEN-5: Missing Context for Unknown Companies
**Pattern**: Assumes reader knows the company
**Example**: "At TechStartup, launched mobile app"
**Fix**: "At TechStartup (Series B edtech, 200 employees), launched mobile app reaching 500K students"
**Severity**: LOW

---

## Cover Letter Patterns

### CL-1: Resume Repetition
**Pattern**: Cover letter restates resume bullets verbatim
**Example**: Same achievement, same wording
**Fix**: Add depth, story, "why", or learning that resume can't capture
**Severity**: HIGH

### CL-2: Generic Company Enthusiasm
**Pattern**: "I'm excited about your mission" without specificity
**Example**: "I'm passionate about your company's innovative approach"
**Fix**: Reference specific product, blog post, recent news, or personal experience
**Severity**: HIGH

### CL-3: Weak Opening
**Pattern**: "I am writing to apply for..."
**Example**: "I am writing to express my interest in the PM position"
**Fix**: Open with a hook - company connection, specific problem, or relevant insight
**Severity**: HIGH

### CL-4: Missing "Why This Company"
**Pattern**: Letter could apply to any company
**Example**: No company-specific details
**Fix**: Include 2-3 specific references to company's product, culture, or challenges
**Severity**: HIGH

### CL-5: Desperation Signals
**Pattern**: Language that undermines confidence
**Example**: "I hope you'll consider me", "I would be grateful for any opportunity"
**Fix**: Confident, direct language: "I'd welcome the opportunity to discuss..."
**Severity**: MEDIUM

---

## Critical Framing Principles

### FRAME-1: Match the Hiring Manager's Mental Model
**Pattern**: Resume written generically without understanding WHY this role exists
**Process Before Writing**:
1. Why is this company hiring for this role? What problem are they solving?
2. What is the human (HM/recruiter) actually looking for? Not keywords -- the real need.
3. What would make them say "this person gets it"?
**Severity**: CRITICAL - This determines everything else

### FRAME-2: Internal PM vs External PM Framing
**Pattern**: Using external customer metrics for internal platform roles
**Example BAD**: "Secured $22M pipeline through AI-native platform"
**Example GOOD**: "Built internal AI monitoring system that gave GTM teams visibility into conversation quality"
**Rule**: If role is for INTERNAL tools/platforms, DO NOT lead with revenue, user acquisition, sales pipeline
**Severity**: HIGH

### FRAME-3: Title Must Match Job Posting
**Pattern**: No title or mismatched title at top of resume
**Fix**: Always add title line under name that mirrors job posting
```
# Your Name
## Senior Product Manager - AI & Internal Platforms
```
**Severity**: HIGH

### FRAME-4: Level Must Match Job Posting
**Pattern**: Using inflated title that signals overqualified
**Example BAD**: "Principal Product Manager" when job is "Senior PM"
**Example GOOD**: Match the level in the job posting exactly
**Severity**: MEDIUM

### FRAME-5: Founder/Cofounder Flag
**Pattern**: Using "Cofounder" title when role doesn't value founder experience
**Rule**: Only mention "Founder" or "Cofounder" if job posting explicitly values entrepreneurial experience
**Example BAD**: "Co-founder & Principal PM" for corporate role
**Example GOOD**: "Product Manager - AI"
**Severity**: HIGH

---

## Key Achievements Section Rules

### KA-1: Key Achievements Must Match HM Priorities
**Pattern**: Generic impressive metrics that don't match what HM cares about
**Rule**: Key Achievements must answer the HM's actual question about the role
**For Internal Roles**:
- "Built internal observability system that surfaced X to internal teams"
- "Unified N fragmented tools into single platform"
- "Created structured feedback loops that reduced friction by X%"
- NOT "Secured $XM in pipeline"
- NOT "Grew user base by X%"
**Severity**: CRITICAL

---

## Review Scoring Framework

Every resume review MUST include scores using this framework:

### ATS Review (X/10)
Identify 3 specific reasons it might FAIL ATS screening:
- Missing keywords (exact phrase matches)
- Formatting issues
- Section gaps

### Recruiter 5-Second Scan (X/10)
Identify 3 reasons a recruiter might REJECT in 5 seconds:
- Unclear value proposition
- Poor visual hierarchy
- Missing key qualifications
- Unknown company names without context

### Hiring Manager Review (X/10)
Identify 3 reasons a manager might PASS (not hire):
- Insufficient relevant achievements
- Weak problem-solution examples
- Poor cultural fit signals
- Gaps in required experience

**Rule**: Do NOT be agreeable. Find real problems. If the resume seems perfect, look harder.

---

## Keyword Strategy Patterns

### KW-1: Keyword Tiering - Don't Over-Index on Tier 3
**Pattern**: Trying to hit every keyword mentioned in JD, including throwaway examples
**Problem**: JDs often list examples like "such as forecasting, anomaly detection, recommendations" - these are Tier 3, not core requirements
**Process**:
- **Tier 1 (Must nail)**: Core requirements repeated throughout JD, in title, or in required qualifications
- **Tier 2 (Should include)**: Mentioned multiple times but not primary focus
- **Tier 3 (OK to skip)**: Examples in lists, nice-to-haves, one-time mentions
**Rule**: Prioritize Tier 1 coverage over forcing Tier 3 keywords awkwardly
**Severity**: MEDIUM

### KW-2: Skills Section Prioritization
**Pattern**: Listing skills alphabetically or by impressiveness rather than by JD relevance
**Fix**: Order skills by keyword tier - Tier 1 keywords first, then Tier 2
**Example**: For AI PM role, lead with "Agentic Workflows, Model Validation & Monitoring" not "Predictive Analytics"
**Severity**: MEDIUM

---

## Metric Consistency Patterns

### METRIC-1: Same Achievement, Different Framing Across Documents
**Pattern**: Resume says "automating tasks by 70%" but cover letter says "cut time-to-completion by 70%"
**Problem**: Could be interpreted as different things (70% of tasks vs 70% time reduction)
**Fix**: Use identical framing for the same metric across resume and cover letter
**Severity**: MEDIUM

---

## Cover Letter Story Patterns

### CL-6: Verify Story Origin - Don't Assume "Inherited"
**Pattern**: Assuming candidate "inherited" a problem when they actually built the initial version and pivoted
**Problem**: "Inherited a chatbot" vs "Built a chatbot, then pivoted based on user data" are very different stories
**Impact**: Second version shows learning and data-driven decision making; first sounds like fixing someone else's mistake
**Rule**: Always verify the origin of the story with the candidate
**Severity**: HIGH

### CL-7: UX Pivot vs Technical Architecture Stories
**Pattern**: Conflating UX/workflow insights with technical architecture decisions
**Problem**: "We pivoted to embedded AI workflows" (UX insight) is different from "We architected multi-model routing" (technical decision)
**Rule**: Match the story type to what the role cares about
- For product/UX-focused roles: Lead with the workflow/user insight
- For technical/platform roles: Lead with the architecture decision
**Severity**: MEDIUM

### CL-8: Memorable Lines Must Be Authentic
**Pattern**: Generic memorable lines that could apply to anyone
**Good Examples**:
- "Don't make users wrestle with AI, make AI work invisibly within the process they already know"
- "Agents that automate complex operations beat chatbots every time"
**Rule**: Memorable lines should encapsulate a genuine insight from the candidate's experience
**Severity**: LOW

---

## AI PM Specific Patterns

### AI-4: Model Monitoring Must Be Demonstrated, Not Just Listed
**Pattern**: "Model monitoring" in skills section but no bullet demonstrating it
**Problem**: HMs for AI roles specifically look for operational AI experience
**Fix**: Name specific tools (Langfuse, Weights & Biases, MLflow) and what you monitored (quality drift, latency, cost)
**Example**: "Established model monitoring using Langfuse, tracking quality drift, latency, and cost metrics across production AI agents"
**Severity**: HIGH for AI PM roles

### AI-5: Chatbot vs Agentic Workflow Distinction
**Pattern**: Using "AI" or "chatbot" generically when the work was actually agentic workflows
**Insight**: There's a meaningful distinction:
- **Chatbot**: User prompts -> AI responds -> User refines (reactive)
- **Agentic workflow**: AI embedded in workflow -> generates near-ready output -> User edits (proactive)
**Rule**: If you built proactive AI that works without user prompting, call it out explicitly
**Severity**: MEDIUM

### AI-6: AI PM != Technical AI Role - Don't Sacrifice Core PM Skills
**Pattern**: Over-indexing on AI/ML technical skills while missing core PM competencies
**Problem**: Resume reads like a technical AI engineer, not a Product Manager who works on AI
**What gets missed when over-indexing on AI:**
- Cross-functional leadership (design, GTM, leadership - not just data science)
- Customer discovery and research
- Prioritization decisions
- Stakeholder communication and transparency
- Roadmap ownership

**Rule**: For AI PM roles, ensure BOTH:
1. Core PM skills: cross-functional, customer discovery, prioritization, communication
2. AI/ML depth: technical understanding, model monitoring, data science partnership

**Checklist before approving AI PM resume:**
- [ ] Summary mentions cross-functional leadership (not just data science)?
- [ ] Customer discovery/research demonstrated in bullets?
- [ ] Prioritization decisions shown?
- [ ] GTM collaboration mentioned?
- [ ] Communication to leadership/stakeholders shown?
- [ ] THEN verify AI/ML technical depth

**Severity**: HIGH - This makes candidate look like wrong fit for PM role

---

## Formatting Rules

### FMT-1: Bullet Points Must End with Full Stop
**Pattern**: Bullet points missing period at the end
**Example BAD**: "Launched AI platform reducing costs by 80%"
**Example GOOD**: "Launched AI platform reducing costs by 80%."
**Rule**: Every bullet point must end with "."
**Severity**: LOW but consistent

### FMT-2: Short Month Format
**Pattern**: Using full month names in dates
**Example BAD**: "December 2025"
**Example GOOD**: "Dec 2025"
**Rule**: Always use 3-letter month abbreviations
**Severity**: LOW

### FMT-3: Contact Line Must Be Single Line
**Pattern**: Contact information wrapping to multiple lines
**Fix**: Keep all contact info on one line: Email | Phone | Location | LinkedIn | Website
**Rule**: If too long, abbreviate (e.g., "City, ST" instead of "City, Country")
**Severity**: MEDIUM - affects visual hierarchy

### FMT-4: LinkedIn as Short Text with Hyperlink
**Pattern**: Full LinkedIn URL displayed in contact line
**Example BAD**: "https://www.linkedin.com/in/your-linkedin"
**Example GOOD**: "linkedin.com/in/your-linkedin" or "LinkedIn" (hyperlinked)
**Rule**: Use short text, add hyperlink in Google Doc
**Severity**: LOW

### FMT-5: Old Roles Should Be Title-Only
**Pattern**: Adding bullet points to very old non-PM roles
**Rule**: Pre-PM roles (Software Engineer, Sales Engineer from 10+ years ago) should be title/company/dates only
**Reason**: Shows engineering foundation without taking space from relevant PM experience
**Severity**: MEDIUM

### FMT-6: Required Experience Entries - NEVER OMIT
**Pattern**: Missing foundational engineering roles
**Required roles (MUST appear in EVERY resume, title-only):**
1. Your earliest relevant role establishing technical/domain foundation
2. Intermediate roles showing career progression
3. Transition roles bridging to your current function

**Why**:
- Earliest roles establish pedigree and credibility
- Engineering/technical roles establish technical foundation
- These make you credible with technical teams

**Severity**: HIGH - These MUST be checked in every review

---

## Cross-Document Consistency

### CROSS-1: Resume and Cover Letter Title Must Match
**Pattern**: Different titles in resume header vs cover letter header
**Example BAD**: Resume says "Senior PM - Agentic AI", Cover letter says "Senior PM - AI & Internal Platforms"
**Rule**: Title must be identical in both documents
**Severity**: HIGH - looks sloppy, confuses reader

---

## Bullet Discipline Patterns

### FMT-7: Bullet Word Limit
**Pattern**: Bullets running long because they contain two ideas or redundant phrasing
**Rule**: Every bullet must be 25 words or fewer. Count before finalizing.
**Why long bullets happen**: Trying to cram cross-functional context, the what, and the metric into one sentence. Split or cut -- don't compress.
**Check**: Long bullets almost always contain a hidden second idea. Find it and either make it a separate bullet or drop it.
**Severity**: MEDIUM

### FMT-8: Bullet Count Management for Page Fit
**Pattern**: Too many bullets in the top sections, leaving no space for older experience or pushing to page 2
**Rule**: Key Achievements + top 3-4 experience sections = 13-14 bullets total
- 13 = without an optional bullet (space-constrained)
- 14 = with an optional bullet (comfortable fit)
**Check in every build**: Count bullets in those sections before finalizing the draft.
**Severity**: MEDIUM

### FMT-9: Optional Marker for Space Management
**Pattern**: Forcing a decision between "keep everything" (too long) and "remove a good bullet" (too short)
**Rule**: Mark one bullet as optional so the user controls the cut based on actual page rendering.
**Which bullet to mark**: The least role-relevant bullet for this specific application -- not the weakest metric. A bullet with great numbers but wrong signal (e.g., PLG/user acquisition bullet for an orchestration PM role) is the right one to mark.
**How to mark**: Note in the strategy doc which bullet is optional. Never put [OPTIONAL] text in the resume markdown itself.
**Severity**: LOW -- process quality, not content quality

### FMT-10: Em-Dashes Survive Review Passes
**Pattern**: Em-dash flagged and removed in one location, but another survives in the same or adjacent sentence
**Why it happens**: Edits are made paragraph by paragraph; the grep-style scan isn't done across the whole document after edits.
**Rule**: After ANY edit to a document, do a dedicated full-document em-dash scan before closing the loop. Search for "---" (em-dash) explicitly.
**Common hiding spots**: Appositive phrases ("My X, my Y --- they're..."), mid-sentence pivots ("The model wasn't wrong --- the workflow was").
**Severity**: HIGH -- em-dashes are the #1 AI-writing signal

---

## Domain Translation Patterns

### DOMAIN-1: Domain-Specific Experience -> Industry-Neutral Language
**Pattern**: Domain-specific framing makes experience look narrow when applying to roles outside your domain
**Problem words**: Any jargon specific to your current industry that doesn't translate
**Translation approach**:
| Domain-specific term | Domain-neutral replacement |
|---------------------|---------------------------|
| domain experts | users |
| domain-specific end users | end users |
| domain-specific workflow | workflow context |
| specialized domain | regulated domain / document-heavy domain |
| domain-scale deployment | enterprise deployment |
| Domain-Expert-in-the-Loop | human-in-the-loop |
| domain-specific quality drift | quality drift |
**Rule**: Translate ALL domain-specific terms in Key Achievements and experience bullets when applying outside your domain. Domain-neutral framing lets your architecture story transfer to any industry.
**Severity**: HIGH when applying outside your domain

---

## Cover Letter Grammar Patterns

### CL-9: Verb-Object Mismatch with "Building"
**Pattern**: "I've spent X years building the problem" -- you build a solution, not a problem
**Common forms**:
- BAD: "the problem I've spent two years building"
- BAD: "building this challenge"
- GOOD: "the problem space I've spent two years building toward"
- GOOD: "the problem I've spent two years solving"
- GOOD: "what I've spent two years building"
**Why it happens**: Trying to mirror "building" (a valued JD word) back to the reader while connecting to the problem framing. The verb applies to the wrong noun.
**Severity**: MEDIUM -- grammatical error that undermines credibility

---

## Workflow/Export Patterns

### WF-1: Google Drive Subfolder Creation
**Pattern**: Docs exported directly to Drive root instead of company subfolder
**Problem**: Export script was not auto-reading config or creating subfolders
**Fix**: Script should auto-read output folder config and create `{company}-{role}` subfolder
**Rule**: Do NOT pass folder IDs manually - let script auto-create subfolder
**Severity**: MEDIUM

### WF-2: Google Drive File Naming Convention
**Pattern**: Files named inconsistently (e.g., "Company - Role - Resume")
**Required format**: `{CandidateName}-{doc_type}-{company}-{role}`
- Resume: `JaneDoe-Resume-Acme-Senior-PM`
- Cover Letter: `JaneDoe-CoverLetter-Acme-Senior-PM`
**Severity**: LOW

---

## Adding New Patterns

When the retrospective phase identifies a recurring issue, add it here:

```markdown
### [CODE]: [Pattern Name]
**Pattern**: [What the issue is]
**Example**: "[Bad example]"
**Fix**: "[Good example]"
**Severity**: HIGH/MEDIUM/LOW
**Added**: [Date] from [Company-Role] application
```
