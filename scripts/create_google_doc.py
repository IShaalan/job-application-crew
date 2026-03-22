#!/usr/bin/env python3
"""
Create professionally formatted Google Docs from markdown resume/cover letter.

Uses Google Docs API to create native Google Docs with proper formatting:
- Open Sans font throughout
- Gray shading for section headers
- Proper spacing and margins
- Bold formatting for key elements

Prerequisites:
- Google Cloud project with Docs API enabled
- OAuth credentials in config/credentials.json
- Run once to authorize
- candidate/resume-config.yaml with contact info

Usage:
    python scripts/create_google_doc.py --content PATH --type resume|cover-letter --company NAME --role ROLE

Examples:
    python scripts/create_google_doc.py \
        --content jobs/acme/drafts/resume-v3.md \
        --type resume \
        --company "Acme" \
        --role "Senior PM AI"
"""

import os
import sys
import re
import yaml
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_resume_config(config_path=None):
    """Load candidate resume configuration (contact info, export settings).

    Searches for resume-config.yaml in:
    1. Explicit config_path argument
    2. candidate/resume-config.yaml (relative to project root)
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'candidate', 'resume-config.yaml'
        )
    if not os.path.exists(config_path):
        print(f"Error: Resume config not found at {config_path}")
        print("Create candidate/resume-config.yaml with your contact info.")
        print("See starter-kit/candidate/ for a template.")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_drive_config() -> dict:
    """Load configuration from drive_config.yaml."""
    config_path = PROJECT_ROOT / "config" / "drive_config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def build_contact_line(resume_config: dict) -> str:
    """Build the contact line string from resume config.

    Reads contact info from resume-config.yaml and assembles the pipe-separated
    contact line with markdown links where appropriate.
    """
    contact = resume_config.get('contact', {})
    parts = []

    email = contact.get('email', '')
    if email:
        parts.append(email)

    phone = contact.get('phone', '')
    if phone:
        parts.append(phone)

    location = contact.get('location', '')
    if location:
        parts.append(location)

    # LinkedIn - use markdown link if URL provided
    linkedin = contact.get('linkedin', {})
    if isinstance(linkedin, dict):
        display = linkedin.get('display', '')
        url = linkedin.get('url', '')
        if display and url:
            parts.append(f"[{display}]({url})")
        elif display:
            parts.append(display)
    elif isinstance(linkedin, str) and linkedin:
        parts.append(linkedin)

    # Website - use markdown link if URL provided
    website = contact.get('website', {})
    if isinstance(website, dict):
        display = website.get('display', '')
        url = website.get('url', '')
        if display and url:
            parts.append(f"[{display}]({url})")
        elif display:
            parts.append(display)
    elif isinstance(website, str) and website:
        parts.append(website)

    # Any additional contact fields
    for extra in contact.get('extra', []):
        if isinstance(extra, dict):
            display = extra.get('display', '')
            url = extra.get('url', '')
            if display and url:
                parts.append(f"[{display}]({url})")
            elif display:
                parts.append(display)
        elif isinstance(extra, str) and extra:
            parts.append(extra)

    return ' | '.join(parts)


def find_or_create_folder(drive_service, folder_name: str, parent_id: str) -> str:
    """Find existing folder or create new one."""
    # Search for existing folder
    query = (f"name='{folder_name}' and "
             f"'{parent_id}' in parents and "
             f"mimeType='application/vnd.google-apps.folder' and "
             f"trashed=false")

    results = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    files = results.get('files', [])

    if files:
        print(f"Found existing folder: {folder_name}")
        return files[0]['id']

    # Create new folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }

    folder = drive_service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()

    print(f"Created new folder: {folder_name}")
    return folder['id']

def parse_contact_markdown(text: str) -> tuple:
    """Parse markdown links in contact line text.

    Returns (cleaned_text, links) where:
    - cleaned_text has [display](url) replaced with just display
    - links is a list of {'text': str, 'url': str, 'start': int, 'end': int} in cleaned_text
    """
    links = []
    cleaned = ""
    last_end = 0

    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
        # Add text before this match
        cleaned += text[last_end:match.start()]
        display = match.group(1)
        url = match.group(2)
        start = len(cleaned)
        cleaned += display
        links.append({'text': display, 'url': url, 'start': start, 'end': start + len(display)})
        last_end = match.end()

    cleaned += text[last_end:]
    return cleaned, links


# Formatting constants (based on Globant template analysis)
FONT_FAMILY = "Open Sans"
FONT_SIZE_NAME = 24
FONT_SIZE_TITLE = 13
FONT_SIZE_SECTION = 13
FONT_SIZE_JOB_TITLE = 12
FONT_SIZE_BODY = 11

# Gray background color (RGB: 0.937, 0.937, 0.937)
GRAY_BG = {'red': 0.937, 'green': 0.937, 'blue': 0.937}

# Spacing in points
SPACING_SECTION = 6
SPACING_BODY = 6

# Margins in points (14.4pt = 0.2 inches)
MARGIN_PT = 14.4  # 0.2 inches per user preference


def get_docs_service():
    """Create and return Google Docs API service."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: Google API libraries not installed.")
        print("Install with: pip install google-api-python-client google-auth-oauthlib")
        sys.exit(1)

    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file'
    ]

    credentials_path = PROJECT_ROOT / "config" / "credentials.json"
    token_path = PROJECT_ROOT / "config" / "token_docs_write.json"

    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                print(f"Error: Credentials file not found at {credentials_path}")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    return docs_service, drive_service


def parse_markdown_resume(content: str) -> Dict[str, Any]:
    """Parse markdown resume into structured sections."""
    sections = {
        'name': '',
        'title': '',
        'contact': [],  # Now a list to hold multiple contact lines
        'summary': '',
        'key_achievements': [],
        'experience': [],
        'skills': [],
        'education': [],
        'certifications': [],
        'builder_projects': [],
        'community': []
    }

    lines = content.split('\n')
    current_section = None
    current_job = None
    buffer = []
    collecting_contact = False

    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines (but don't reset collecting_contact for empty lines)
        if not line_stripped:
            continue

        # Horizontal rules - stop collecting contact, but don't skip (might separate experience sections)
        if line_stripped in ['---', '***']:
            collecting_contact = False
            continue

        # H1 - Name
        if line.startswith('# ') and not sections['name']:
            sections['name'] = line[2:].strip()
            collecting_contact = True  # Contact line follows name directly
            continue

        # Bold title line: **Senior Product Manager**
        if (sections['name'] and not sections['title'] and not current_section
                and line_stripped.startswith('**') and line_stripped.endswith('**')
                and line_stripped.count('**') == 2):
            sections['title'] = line_stripped.strip('*')
            continue

        # H2 - Could be title or section header
        if line.startswith('## '):
            header = line[3:].strip()
            collecting_contact = False

            # Check if it's the job title (right after name)
            if not sections['title'] and not current_section:
                sections['title'] = header
                collecting_contact = True  # Contact info follows title
                continue

            # Otherwise it's a section header
            # Save any pending job before switching sections (fixes IBM being dropped)
            if current_job:
                sections['experience'].append(current_job)

            section_map = {
                'Summary': 'summary',
                'Key Achievements': 'key_achievements',
                'Professional Experience': 'experience',
                'Experience': 'experience',
                'Skills': 'skills',
                'Education': 'education',
                'Certifications': 'certifications',
                'Builder Projects': 'builder_projects',
                'Community': 'community',
                'Community Involvement': 'community'
            }

            current_section = section_map.get(header, None)
            current_job = None
            continue

        # H3 - Job title in experience
        if line.startswith('### ') and current_section == 'experience':
            # Save previous job if exists
            if current_job:
                sections['experience'].append(current_job)

            job_line = line[4:].strip()
            # Parse: "Job Title | Company"
            parts = job_line.split(' | ')
            current_job = {
                'title': parts[0] if parts else job_line,
                'company': parts[1] if len(parts) > 1 else '',
                'location': '',
                'bullets': []
            }
            continue

        # Bold job header in experience: **Title | Company | Location | Dates**
        if (current_section == 'experience' and line_stripped.startswith('**')
                and line_stripped.endswith('**') and line_stripped.count('**') == 2):
            # Save previous job if exists
            if current_job:
                sections['experience'].append(current_job)
            # Parse all four parts from the single bold line
            job_line = line_stripped.strip('*')
            parts = [p.strip() for p in job_line.split(' | ')]
            location_parts = parts[2:] if len(parts) > 2 else []
            current_job = {
                'title': parts[0] if parts else job_line,
                'company': parts[1] if len(parts) > 1 else '',
                'location': ' | '.join(location_parts),
                'bullets': []
            }
            continue

        # Location line (after job title)
        if current_job and not current_job['location'] and ' | ' in line_stripped and not line_stripped.startswith('-'):
            current_job['location'] = line_stripped
            continue

        # Contact lines (after title, before first section header)
        # Contains email OR linkedin/website OR has pipe separators
        if collecting_contact and not line_stripped.startswith('#') and not line_stripped.startswith('-'):
            # Check if it looks like contact info (has @ or linkedin or pipe separators or domain)
            if '@' in line_stripped or 'linkedin' in line_stripped or '|' in line_stripped or '.xyz' in line_stripped or '.com' in line_stripped:
                sections['contact'].append(line_stripped)
                continue

        # Bullet points
        if line_stripped.startswith('- '):
            bullet = line_stripped[2:].strip()

            # Strip [OPTIONAL] marker and track it for post-export note
            if '[OPTIONAL]' in bullet:
                bullet = bullet.replace('[OPTIONAL]', '').strip()
                if '_optional_bullets' not in sections:
                    sections['_optional_bullets'] = []
                sections['_optional_bullets'].append(bullet[:60])

            if current_section == 'key_achievements':
                sections['key_achievements'].append(bullet)
            elif current_section == 'experience' and current_job:
                current_job['bullets'].append(bullet)
            elif current_section == 'certifications':
                sections['certifications'].append(bullet)
            elif current_section == 'community':
                sections['community'].append(bullet)
            continue

        # Skills lines (bold headers)
        if current_section == 'skills' and line_stripped.startswith('**'):
            sections['skills'].append(line_stripped)
            continue

        # Education lines
        if current_section == 'education' and line_stripped.startswith('**'):
            sections['education'].append(line_stripped)
            continue

        # Summary paragraph
        if current_section == 'summary':
            sections['summary'] += line_stripped + ' '
            continue

        # Builder projects (bold title lines)
        if current_section == 'builder_projects':
            sections['builder_projects'].append(line_stripped)
            continue

        # Community section - catch non-bullet lines (plain text, bold inline entries)
        if current_section == 'community':
            sections['community'].append(line_stripped)
            continue

    # Don't forget the last job
    if current_job:
        sections['experience'].append(current_job)

    # Clean up summary
    sections['summary'] = sections['summary'].strip()

    return sections


def build_resume_requests(sections: Dict[str, Any]) -> List[Dict]:
    """Build Google Docs API requests for resume formatting."""
    requests = []
    index = 1  # Document starts at index 1

    def add_text(text: str, bold: bool = False, font_size: int = FONT_SIZE_BODY,
                 shading: bool = False, space_above: int = 0, space_below: int = 0,
                 center: bool = False) -> int:
        """Add text with formatting and return the new index."""
        nonlocal index

        if not text:
            return index

        # Add newline if not present
        if not text.endswith('\n'):
            text += '\n'

        start_index = index
        end_index = index + len(text)

        # Insert text
        requests.append({
            'insertText': {
                'location': {'index': start_index},
                'text': text
            }
        })

        # Text formatting
        text_style = {
            'weightedFontFamily': {'fontFamily': FONT_FAMILY},
            'fontSize': {'magnitude': font_size, 'unit': 'PT'}
        }
        if bold:
            text_style['bold'] = True

        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start_index, 'endIndex': end_index - 1},
                'textStyle': text_style,
                'fields': 'weightedFontFamily,fontSize,bold'
            }
        })

        # Paragraph formatting
        para_style = {
            'spaceAbove': {'magnitude': space_above, 'unit': 'PT'},
            'spaceBelow': {'magnitude': space_below, 'unit': 'PT'},
            'lineSpacing': 100
        }

        if center:
            para_style['alignment'] = 'CENTER'

        if shading:
            para_style['shading'] = {'backgroundColor': {'color': {'rgbColor': GRAY_BG}}}

        requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start_index, 'endIndex': end_index},
                'paragraphStyle': para_style,
                'fields': 'spaceAbove,spaceBelow,lineSpacing,alignment,shading'
            }
        })

        index = end_index
        return index

    def add_section_header(text: str) -> int:
        """Add a section header with gray background, centered. No space inside shading."""
        return add_text(text.upper(), bold=False, font_size=FONT_SIZE_SECTION,
                       shading=True, space_above=SPACING_SECTION, space_below=0, center=True)

    # Track ranges that need bullets applied at the end
    bullet_ranges = []

    def add_bullet(text: str, bold_prefix: bool = False, space_above: int = 0) -> int:
        """Add a bullet point using native Google Docs bullets."""
        nonlocal index

        # Clean any remaining markdown from text
        clean_text = text.replace('**', '')

        # Check if bullet starts with bold prefix (e.g., "**3x faster**:")
        has_bold_prefix = text.startswith('**') and '**:' in text
        bold_part = ''
        rest_part = clean_text

        if has_bold_prefix:
            # Extract bold part
            bold_end = text.index('**:', 2)
            bold_part = text[2:bold_end]
            rest_part = text[bold_end+3:].strip()
            clean_text = f"{bold_part}: {rest_part}"

        bullet_text = f"{clean_text}\n"
        start_index = index
        end_index = index + len(bullet_text)

        # Insert text (no bullet character - we'll use native bullets)
        requests.append({
            'insertText': {
                'location': {'index': start_index},
                'text': bullet_text
            }
        })

        # Format the whole line
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start_index, 'endIndex': end_index - 1},
                'textStyle': {
                    'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                    'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'}
                },
                'fields': 'weightedFontFamily,fontSize,bold'
            }
        })

        # Make the prefix bold if present
        if has_bold_prefix and bold_part:
            bold_end_idx = start_index + len(bold_part)
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_index, 'endIndex': bold_end_idx},
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })

        # Add paragraph spacing if specified
        if space_above > 0:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_index, 'endIndex': end_index},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': space_above, 'unit': 'PT'}
                    },
                    'fields': 'spaceAbove'
                }
            })

        # Track this range for bullet formatting
        bullet_ranges.append({'startIndex': start_index, 'endIndex': end_index})

        index = end_index
        return index

    # Build the document

    # 1. Name (centered, large)
    add_text(sections['name'], bold=False, font_size=FONT_SIZE_NAME, center=True)

    # 2. Title (centered, minimal space below)
    add_text(sections['title'], bold=False, font_size=FONT_SIZE_TITLE,
             space_below=2, center=True)

    # 3. Contact (with gray background, hyperlinks)
    # Track link ranges to apply later
    link_ranges = []

    for i, contact_line in enumerate(sections['contact']):
        # Parse markdown links: [display](url) -> display text + link metadata
        cleaned_contact, md_links = parse_contact_markdown(contact_line)
        contact_text = cleaned_contact + "\n"
        start_index = index

        requests.append({
            'insertText': {
                'location': {'index': start_index},
                'text': contact_text
            }
        })

        # Format text
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start_index, 'endIndex': start_index + len(contact_text) - 1},
                'textStyle': {
                    'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                    'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'}
                },
                'fields': 'weightedFontFamily,fontSize'
            }
        })

        # Paragraph style with shading and center
        requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start_index, 'endIndex': start_index + len(contact_text)},
                'paragraphStyle': {
                    'alignment': 'CENTER',
                    'shading': {'backgroundColor': {'color': {'rgbColor': GRAY_BG}}},
                    'spaceAbove': {'magnitude': 0 if i > 0 else SPACING_SECTION, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 0, 'unit': 'PT'}
                },
                'fields': 'alignment,shading,spaceAbove,spaceBelow'
            }
        })

        # Add hyperlinks from parsed markdown links (email is NOT linked)
        for md_link in md_links:
            link_ranges.append({
                'start': start_index + md_link['start'],
                'end': start_index + md_link['end'],
                'url': md_link['url']
            })

        index = start_index + len(contact_text)

    # Apply hyperlinks
    for link in link_ranges:
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': link['start'], 'endIndex': link['end']},
                'textStyle': {
                    'link': {'url': link['url']}
                },
                'fields': 'link'
            }
        })

    # 4. Summary
    add_text(sections['summary'], space_above=SPACING_BODY, space_below=SPACING_SECTION)

    # 5. Key Achievements
    add_section_header('Key Achievements')
    for i, achievement in enumerate(sections['key_achievements']):
        # First bullet gets extra spacing after header
        space = 6 if i == 0 else 0
        add_bullet(achievement, bold_prefix=True, space_above=space)

    # 6. Professional Experience
    add_section_header('Professional Experience')
    for job in sections['experience']:
        # Job title (bold) + company + location/dates (not bold, smaller font)
        title_part = job['title']
        rest_parts = []
        if job['company']:
            rest_parts.append(job['company'])
        if job['location']:
            # Replace "United Arab Emirates" with "UAE"
            location = job['location'].replace('United Arab Emirates', 'UAE')
            rest_parts.append(location)

        rest_text = " | ".join(rest_parts) if rest_parts else ""

        # Insert job title (bold)
        start_index = index
        title_text = title_part
        if rest_text:
            title_text += " | "

        requests.append({
            'insertText': {
                'location': {'index': start_index},
                'text': title_text
            }
        })

        # Format title as bold
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start_index, 'endIndex': start_index + len(job['title'])},
                'textStyle': {
                    'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                    'fontSize': {'magnitude': FONT_SIZE_JOB_TITLE, 'unit': 'PT'},
                    'bold': True
                },
                'fields': 'weightedFontFamily,fontSize,bold'
            }
        })

        # Format " | " as not bold if present
        if rest_text:
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_index + len(job['title']), 'endIndex': start_index + len(title_text)},
                    'textStyle': {
                        'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                        'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'},
                        'bold': False
                    },
                    'fields': 'weightedFontFamily,fontSize,bold'
                }
            })

        index = start_index + len(title_text)

        # Insert rest (company + location) - not bold, body font size
        if rest_text:
            rest_with_newline = rest_text + "\n"
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': rest_with_newline
                }
            })

            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': index, 'endIndex': index + len(rest_with_newline) - 1},
                    'textStyle': {
                        'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                        'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'},
                        'bold': False
                    },
                    'fields': 'weightedFontFamily,fontSize,bold'
                }
            })

            # Paragraph style for the whole line
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_index, 'endIndex': index + len(rest_with_newline)},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': SPACING_SECTION, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 2, 'unit': 'PT'}
                    },
                    'fields': 'spaceAbove,spaceBelow'
                }
            })

            index = index + len(rest_with_newline)
        else:
            # Just title, add newline
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': "\n"
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_index, 'endIndex': index + 1},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': SPACING_SECTION, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 2, 'unit': 'PT'}
                    },
                    'fields': 'spaceAbove,spaceBelow'
                }
            })
            index = index + 1

        # Bullets
        for bullet in job['bullets']:
            add_bullet(bullet)

    # 7. Skills - with bold category prefixes
    if sections['skills']:
        add_section_header('Skills')
        for skill_line in sections['skills']:
            # Parse bold prefix: "**AI/ML**: content" -> bold "AI/ML:", regular "content"
            # Note: pattern is **text**: not **text:**
            if skill_line.startswith('**') and '**:' in skill_line:
                bold_end = skill_line.index('**:')
                bold_part = skill_line[2:bold_end]
                rest_part = skill_line[bold_end+3:].strip()

                full_line = f"{bold_part}: {rest_part}\n"
                start_index = index

                requests.append({
                    'insertText': {
                        'location': {'index': start_index},
                        'text': full_line
                    }
                })

                # Format whole line - reset bold to false first
                requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line) - 1},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                            'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'},
                            'bold': False
                        },
                        'fields': 'weightedFontFamily,fontSize,bold'
                    }
                })

                # Make prefix bold (including colon)
                bold_end_idx = start_index + len(bold_part) + 1  # +1 for colon
                requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_index, 'endIndex': bold_end_idx},
                        'textStyle': {'bold': True},
                        'fields': 'bold'
                    }
                })

                # Paragraph style with spacing after header
                requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line)},
                        'paragraphStyle': {
                            'spaceAbove': {'magnitude': 6, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 2, 'unit': 'PT'}
                        },
                        'fields': 'spaceAbove,spaceBelow'
                    }
                })

                index = start_index + len(full_line)
            else:
                clean_line = skill_line.replace('**', '')
                add_text(clean_line, space_above=6, space_below=2)

    # 8. Education - with bold degree name
    if sections['education']:
        add_section_header('Education')
        for edu_line in sections['education']:
            # Parse: "**Degree** | University | Year"
            if edu_line.startswith('**') and '**' in edu_line[2:]:
                bold_end = edu_line.index('**', 2)
                bold_part = edu_line[2:bold_end]
                rest_part = edu_line[bold_end+2:].strip()
                if rest_part.startswith('|'):
                    rest_part = rest_part[1:].strip()

                full_line = f"{bold_part} | {rest_part}\n" if rest_part else f"{bold_part}\n"
                start_index = index

                requests.append({
                    'insertText': {
                        'location': {'index': start_index},
                        'text': full_line
                    }
                })

                # Format whole line
                requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line) - 1},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                            'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'},
                            'bold': False
                        },
                        'fields': 'weightedFontFamily,fontSize,bold'
                    }
                })

                # Make degree bold
                requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_index, 'endIndex': start_index + len(bold_part)},
                        'textStyle': {'bold': True},
                        'fields': 'bold'
                    }
                })

                # Paragraph style with spacing after header
                requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line)},
                        'paragraphStyle': {
                            'spaceAbove': {'magnitude': 6, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 2, 'unit': 'PT'}
                        },
                        'fields': 'spaceAbove,spaceBelow'
                    }
                })

                index = start_index + len(full_line)
            else:
                clean_line = edu_line.replace('**', '')
                add_text(clean_line, space_above=6, space_below=2)

    # 9. Certifications - NO bullets, bold cert name (first part before |)
    if sections['certifications']:
        add_section_header('Certifications')
        for cert in sections['certifications']:
            # Parse: "Cert Name | Issuer | Date" - first part becomes bold
            if ' | ' in cert:
                parts = cert.split(' | ', 1)
                bold_part = parts[0].replace('**', '')  # Remove any existing markdown
                rest_part = parts[1].replace('**', '') if len(parts) > 1 else ''

                full_line = f"{bold_part} | {rest_part}\n"
            else:
                bold_part = cert.replace('**', '')
                full_line = f"{bold_part}\n"

            start_index = index

            requests.append({
                'insertText': {
                    'location': {'index': start_index},
                    'text': full_line
                }
            })

            # Format whole line
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line) - 1},
                    'textStyle': {
                        'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                        'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'},
                        'bold': False
                    },
                    'fields': 'weightedFontFamily,fontSize,bold'
                }
            })

            # Make cert name bold
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_index, 'endIndex': start_index + len(bold_part)},
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })

            # Paragraph style with spacing
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line)},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': 6, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 2, 'unit': 'PT'}
                    },
                    'fields': 'spaceAbove,spaceBelow'
                }
            })

            # NO bullet for certifications
            index = start_index + len(full_line)

    # 10. Builder Projects - with bold project names
    if sections['builder_projects']:
        add_section_header('Builder Projects')
        for project in sections['builder_projects']:
            # Parse bold prefix: "**Project Name** - description" or "**Project Name:** description"
            if project.startswith('**'):
                # Find end of bold part
                bold_end = project.find('**', 2)
                if bold_end > 0:
                    bold_part = project[2:bold_end]
                    rest_part = project[bold_end+2:].strip()
                    # Remove leading dash or colon
                    if rest_part.startswith('-') or rest_part.startswith(':'):
                        rest_part = rest_part[1:].strip()

                    full_line = f"{bold_part} - {rest_part}\n"
                    start_index = index

                    requests.append({
                        'insertText': {
                            'location': {'index': start_index},
                            'text': full_line
                        }
                    })

                    # Format whole line
                    requests.append({
                        'updateTextStyle': {
                            'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line) - 1},
                            'textStyle': {
                                'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                                'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'}
                            },
                            'fields': 'weightedFontFamily,fontSize,bold'
                        }
                    })

                    # Make project name bold
                    requests.append({
                        'updateTextStyle': {
                            'range': {'startIndex': start_index, 'endIndex': start_index + len(bold_part)},
                            'textStyle': {'bold': True},
                            'fields': 'bold'
                        }
                    })

                    # Paragraph style
                    requests.append({
                        'updateParagraphStyle': {
                            'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line)},
                            'paragraphStyle': {
                                'spaceAbove': {'magnitude': 4, 'unit': 'PT'},
                                'spaceBelow': {'magnitude': 4, 'unit': 'PT'}
                            },
                            'fields': 'spaceAbove,spaceBelow'
                        }
                    })

                    index = start_index + len(full_line)
                    continue

            # Fallback: clean up markdown
            clean_project = project.replace('**', '')
            add_text(clean_project, space_above=4, space_below=4)

    # 11. Community - NO bullets, with bold role prefixes
    if sections['community']:
        add_section_header('Community Involvement')
        for item in sections['community']:
            # Parse bold prefix: "**Mentor** | details"
            if item.startswith('**') and '** |' in item:
                bold_end = item.index('** |')
                bold_part = item[2:bold_end]
                rest_part = item[bold_end+4:].strip()

                full_line = f"{bold_part} | {rest_part}\n"
            else:
                # Fallback: clean up markdown
                bold_part = ""
                full_line = item.replace('**', '').replace('*', '') + "\n"

            start_index = index

            requests.append({
                'insertText': {
                    'location': {'index': start_index},
                    'text': full_line
                }
            })

            # Format whole line - not bold by default
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line) - 1},
                    'textStyle': {
                        'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                        'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'},
                        'bold': False
                    },
                    'fields': 'weightedFontFamily,fontSize,bold'
                }
            })

            # Make role bold if present
            if bold_part:
                requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_index, 'endIndex': start_index + len(bold_part)},
                        'textStyle': {'bold': True},
                        'fields': 'bold'
                    }
                })

            # Paragraph style with spacing - NO bullets
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_index, 'endIndex': start_index + len(full_line)},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': 6, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 2, 'unit': 'PT'}
                    },
                    'fields': 'spaceAbove,spaceBelow'
                }
            })

            index = start_index + len(full_line)

    # Apply native bullet formatting to all bullet ranges
    for bullet_range in bullet_ranges:
        requests.append({
            'createParagraphBullets': {
                'range': {
                    'startIndex': bullet_range['startIndex'],
                    'endIndex': bullet_range['endIndex']
                },
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
            }
        })

    return requests


def create_cover_letter_doc(docs_service, drive_service, content: str, title: str,
                            folder_id: str = None, job_title_override: str = None,
                            resume_config: dict = None) -> Dict:
    """Create a Google Doc with formatted cover letter content.

    Args:
        job_title_override: If provided, uses this as the job title in header.
                           Otherwise extracts from resume title pattern in 'title' param.
        resume_config: Loaded resume config dict with contact info.
    """

    # Create empty document
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']
    print(f"Created document: {title}")
    print(f"Document ID: {doc_id}")

    requests = []
    index = 1
    link_ranges = []

    # Header info - read from config
    if resume_config is None:
        resume_config = load_resume_config()

    name = resume_config.get('contact', {}).get('name', 'Candidate')

    # Extract job title: prefer override, then parse from cover letter content, then fallback
    if job_title_override:
        job_title = job_title_override
    else:
        # Try to extract title from the cover letter markdown content
        # Look for bold title line: **Title** (line 2 typically)
        job_title = None
        for cl_line in content.split('\n'):
            cl_stripped = cl_line.strip()
            if cl_stripped.startswith('**') and cl_stripped.endswith('**') and cl_stripped.count('**') == 2:
                job_title = cl_stripped.strip('* ')
                break
        if not job_title:
            job_title = "Product Manager"

    contact_line = build_contact_line(resume_config)

    # === HEADER (copied from resume logic) ===

    # 1. Name (centered, large)
    name_text = name + "\n"
    requests.append({'insertText': {'location': {'index': index}, 'text': name_text}})
    requests.append({
        'updateTextStyle': {
            'range': {'startIndex': index, 'endIndex': index + len(name_text) - 1},
            'textStyle': {
                'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                'fontSize': {'magnitude': FONT_SIZE_NAME, 'unit': 'PT'}
            },
            'fields': 'weightedFontFamily,fontSize'
        }
    })
    requests.append({
        'updateParagraphStyle': {
            'range': {'startIndex': index, 'endIndex': index + len(name_text)},
            'paragraphStyle': {
                'alignment': 'CENTER',
                'lineSpacing': 100
            },
            'fields': 'alignment,lineSpacing'
        }
    })
    index += len(name_text)

    # 2. Title (centered)
    title_text = job_title + "\n"
    requests.append({'insertText': {'location': {'index': index}, 'text': title_text}})
    requests.append({
        'updateTextStyle': {
            'range': {'startIndex': index, 'endIndex': index + len(title_text) - 1},
            'textStyle': {
                'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                'fontSize': {'magnitude': FONT_SIZE_TITLE, 'unit': 'PT'}
            },
            'fields': 'weightedFontFamily,fontSize'
        }
    })
    requests.append({
        'updateParagraphStyle': {
            'range': {'startIndex': index, 'endIndex': index + len(title_text)},
            'paragraphStyle': {
                'alignment': 'CENTER',
                'spaceBelow': {'magnitude': 2, 'unit': 'PT'},
                'lineSpacing': 100
            },
            'fields': 'alignment,spaceBelow,lineSpacing'
        }
    })
    index += len(title_text)

    # 3. Contact line (with gray background, hyperlinks) - same as resume
    cleaned_contact, md_links = parse_contact_markdown(contact_line)
    contact_text = cleaned_contact + "\n"
    start_idx = index

    requests.append({'insertText': {'location': {'index': index}, 'text': contact_text}})
    requests.append({
        'updateTextStyle': {
            'range': {'startIndex': index, 'endIndex': index + len(contact_text) - 1},
            'textStyle': {
                'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'}
            },
            'fields': 'weightedFontFamily,fontSize'
        }
    })
    requests.append({
        'updateParagraphStyle': {
            'range': {'startIndex': index, 'endIndex': index + len(contact_text)},
            'paragraphStyle': {
                'alignment': 'CENTER',
                'shading': {'backgroundColor': {'color': {'rgbColor': GRAY_BG}}},
                'spaceAbove': {'magnitude': SPACING_SECTION, 'unit': 'PT'},
                'spaceBelow': {'magnitude': 0, 'unit': 'PT'},
                'lineSpacing': 100
            },
            'fields': 'alignment,shading,spaceAbove,spaceBelow,lineSpacing'
        }
    })

    # Add hyperlinks from parsed markdown links (email is NOT linked)
    for md_link in md_links:
        link_ranges.append({
            'start': start_idx + md_link['start'],
            'end': start_idx + md_link['end'],
            'url': md_link['url']
        })

    index += len(contact_text)

    # Apply hyperlinks
    for link in link_ranges:
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': link['start'], 'endIndex': link['end']},
                'textStyle': {'link': {'url': link['url']}},
                'fields': 'link'
            }
        })

    # Add spacing after header
    spacer = "\n"
    requests.append({'insertText': {'location': {'index': index}, 'text': spacer}})
    index += len(spacer)

    # Parse cover letter body
    lines = content.split('\n')
    body_lines = []
    in_signature = False
    skip_next_company_line = False

    for line in lines:
        line_stripped = line.strip()

        # Skip markdown headers and horizontal rules
        if line_stripped.startswith('#') or line_stripped in ['---', '***']:
            continue

        # Skip company name line (comes after date, before "Dear")
        # Pattern: line that's just company name like "Acme Hiring Team" before "Dear"
        if skip_next_company_line and not line_stripped.lower().startswith('dear') and line_stripped and 'Hiring Team' in line_stripped:
            skip_next_company_line = False
            continue

        # After a date line, the next non-empty line might be company name to skip
        if re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d', line_stripped):
            skip_next_company_line = True

        # Detect signature section
        if line_stripped.lower().startswith('best regards') or line_stripped.lower().startswith('regards'):
            in_signature = True

        body_lines.append((line_stripped, in_signature))

    # Group into paragraphs, keeping signature lines separate
    paragraphs = []
    current_para = []
    current_is_sig = False

    for line_text, is_sig in body_lines:
        if is_sig:
            # Flush current paragraph
            if current_para:
                paragraphs.append((' '.join(current_para), False))
                current_para = []
            # Each signature line is its own "paragraph"
            if line_text:
                paragraphs.append((line_text, True))
        else:
            if not line_text:
                if current_para:
                    paragraphs.append((' '.join(current_para), False))
                    current_para = []
            else:
                current_para.append(line_text)

    if current_para:
        paragraphs.append((' '.join(current_para), False))

    # Add each paragraph/line
    for para, is_signature in paragraphs:
        if not para:
            continue

        if is_signature:
            # Signature lines with specific spacing
            para_text = para + "\n"
            space_below = 0
            # "Best regards" gets 1.5 spacing, rest get 1.15
            if 'regards' in para.lower():
                line_spacing = 150
            else:
                line_spacing = 115
        else:
            # Regular paragraphs: modest spacing, 1.15 line height
            para_text = para + "\n"
            space_below = 8
            line_spacing = 115

        start_index = index

        requests.append({
            'insertText': {
                'location': {'index': start_index},
                'text': para_text
            }
        })

        # Check if this is a date line (starts with month name)
        is_date = re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d', para)

        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start_index, 'endIndex': start_index + len(para_text) - 1},
                'textStyle': {
                    'weightedFontFamily': {'fontFamily': FONT_FAMILY},
                    'fontSize': {'magnitude': FONT_SIZE_BODY, 'unit': 'PT'},
                    'bold': True if is_date else False
                },
                'fields': 'weightedFontFamily,fontSize,bold'
            }
        })

        requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start_index, 'endIndex': start_index + len(para_text)},
                'paragraphStyle': {
                    'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': space_below, 'unit': 'PT'},
                    'lineSpacing': line_spacing
                },
                'fields': 'spaceAbove,spaceBelow,lineSpacing'
            }
        })

        index = start_index + len(para_text)

    # Apply all requests
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print(f"Applied {len(requests)} formatting requests")

    # Update document margins (same as resume - 0.2")
    margin_requests = [{
        'updateDocumentStyle': {
            'documentStyle': {
                'marginTop': {'magnitude': MARGIN_PT, 'unit': 'PT'},
                'marginBottom': {'magnitude': MARGIN_PT, 'unit': 'PT'},
                'marginLeft': {'magnitude': MARGIN_PT, 'unit': 'PT'},
                'marginRight': {'magnitude': MARGIN_PT, 'unit': 'PT'}
            },
            'fields': 'marginTop,marginBottom,marginLeft,marginRight'
        }
    }]

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': margin_requests}
    ).execute()
    print("Applied page margins")

    # Move to folder if specified
    if folder_id:
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents='root',
            fields='id, parents'
        ).execute()
        print(f"Moved to folder: {folder_id}")

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"Document URL: {doc_url}")

    return {
        'id': doc_id,
        'url': doc_url,
        'title': title
    }


def create_resume_doc(docs_service, drive_service, content: str, title: str, folder_id: str = None) -> Dict:
    """Create a Google Doc with formatted resume content."""

    # Parse the markdown
    sections = parse_markdown_resume(content)

    # Create empty document
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']
    print(f"Created document: {title}")
    print(f"Document ID: {doc_id}")

    # Build formatting requests
    requests = build_resume_requests(sections)

    # Apply all requests
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print(f"Applied {len(requests)} formatting requests")

    # Update document margins
    margin_requests = [{
        'updateDocumentStyle': {
            'documentStyle': {
                'marginTop': {'magnitude': MARGIN_PT, 'unit': 'PT'},
                'marginBottom': {'magnitude': MARGIN_PT, 'unit': 'PT'},
                'marginLeft': {'magnitude': MARGIN_PT, 'unit': 'PT'},
                'marginRight': {'magnitude': MARGIN_PT, 'unit': 'PT'}
            },
            'fields': 'marginTop,marginBottom,marginLeft,marginRight'
        }
    }]

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': margin_requests}
    ).execute()
    print("Applied page margins")

    # Move to folder if specified
    if folder_id:
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents='root',
            fields='id, parents'
        ).execute()
        print(f"Moved to folder: {folder_id}")

    # Get document URL
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"Document URL: {doc_url}")

    return {
        'id': doc_id,
        'url': doc_url,
        'title': title,
        'optional_bullets': sections.get('_optional_bullets', [])
    }


def main():
    parser = argparse.ArgumentParser(description='Create formatted Google Doc from markdown')
    parser.add_argument('--content', type=Path, required=True,
                       help='Path to markdown content file')
    parser.add_argument('--type', choices=['resume', 'cover-letter'], default='resume',
                       help='Document type')
    parser.add_argument('--company', type=str, required=True,
                       help='Company name')
    parser.add_argument('--role', type=str, required=True,
                       help='Role title')
    parser.add_argument('--job-title', type=str, default=None,
                       help='Job title for header (e.g., "Senior Product Manager - Agentic AI"). If not provided, derived from --role.')
    parser.add_argument('--folder-id', type=str, default=None,
                       help='Google Drive folder ID (optional - reads from config if not provided)')
    parser.add_argument('--no-subfolder', action='store_true',
                       help='Do not create company-role subfolder (put directly in output folder)')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to resume-config.yaml (default: candidate/resume-config.yaml)')

    args = parser.parse_args()

    print("Google Docs Creator")
    print("=" * 50)

    # Load resume config (contact info, export settings)
    resume_config = load_resume_config(args.config)

    # Check content file
    if not args.content.exists():
        print(f"Error: Content file not found: {args.content}")
        sys.exit(1)

    # Read content
    with open(args.content, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for Google Drive config
    drive_config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config', 'drive_config.yaml'
    )
    if not os.path.exists(drive_config_path) and not args.folder_id:
        print("Google Drive not configured. Run scripts/setup_google_drive.py to set up.")
        print("Or provide --folder-id to specify a target folder directly.")
        return

    # Generate title using pattern from config
    drive_config = load_drive_config()

    # Build file name from resume config
    candidate_name = resume_config.get('contact', {}).get('name', 'Candidate')
    name_slug = candidate_name.replace(' ', '')

    # Allow override of name pattern from export settings in resume config
    export_settings = resume_config.get('export', {})
    name_pattern = export_settings.get(
        'name_pattern',
        drive_config.get('file_pattern', '{name}-{doc_type}-{company}-{role}')
    )

    # doc_type without space for filename
    doc_type_filename = 'Resume' if args.type == 'resume' else 'CoverLetter'

    title = name_pattern.format(
        name=name_slug,
        company=args.company,
        role=args.role.replace(' ', '-'),
        doc_type=doc_type_filename
    )

    print(f"Content: {args.content}")
    print(f"Type: {args.type}")
    print(f"Title: {title}")

    # Get services
    print("\nConnecting to Google APIs...")
    docs_service, drive_service = get_docs_service()

    # Determine target folder
    folder_id = args.folder_id
    if not folder_id:
        output_folder_id = drive_config.get('output_folder_id')

        if output_folder_id:
            if args.no_subfolder:
                folder_id = output_folder_id
                print(f"Using output folder from config: {output_folder_id}")
            else:
                # Create subfolder using pattern from config
                folder_pattern = drive_config.get('folder_pattern', '{company}-{role}')
                subfolder_name = folder_pattern.format(
                    company=args.company,
                    role=args.role.replace(' ', '-')
                )
                print(f"\nCreating/finding subfolder: {subfolder_name}")
                folder_id = find_or_create_folder(drive_service, subfolder_name, output_folder_id)
        else:
            print("Warning: No folder-id provided and no output_folder_id in config. Doc will be in Drive root.")

    # Create document
    print("\nCreating document...")
    if args.type == 'resume':
        result = create_resume_doc(docs_service, drive_service, content, title, folder_id)
    else:
        result = create_cover_letter_doc(docs_service, drive_service, content, title, folder_id, args.job_title, resume_config)

    print("\n" + "=" * 50)
    print("SUCCESS!")
    print(f"Document: {result['title']}")
    print(f"URL: {result['url']}")

    # Show optional bullets that were stripped during export
    optional_bullets = result.get('optional_bullets', [])
    if optional_bullets:
        print("\nOPTIONAL BULLETS (removed [OPTIONAL] tag, included in export):")
        print("   If the resume is tight on space, consider removing:")
        for ob in optional_bullets:
            print(f"   - {ob}...")


if __name__ == "__main__":
    main()
