GROUPS_TEMPLATE = """You are designing a skill taxonomy for a software recruitment platform in 2026.

Define the top level groups used to organise technical skills. Each group must be a distinct area a developer would recognise, broad enough to hold at least 30 technologies, and narrow enough to be useful as a filter.

Include one group for programming languages so that languages are not scattered across domain groups.

Rules:
- Return between 10 and 14 groups
- Groups must not overlap; each technology should have one obvious home
- key: lowercase, English, underscore separated, stable identifier
- labels: an object mapping language codes to the label shown in the interface. Provide "tr" and "en".
- description: what belongs in this group, in English, one short sentence

Respond with only a JSON array, no other text:
[{{"key": "frontend", "labels": {{"tr": "Frontend", "en": "Frontend"}}, "description": "browser side frameworks, libraries and build tools"}}]"""


SKILLS_TEMPLATE = """You are curating a technical skill taxonomy for a software recruitment platform in 2026.

List technologies that belong in the group "{group}" ({description}) and appear in current job postings.

Rules:
- Only specific named tools, languages, frameworks, libraries, platforms or services
- No software categories such as "antivirus software" or "access management"
- No legacy or discontinued technology
- Use the canonical form a developer would write on a CV
- Return between {minimum} and {maximum} entries

Aliases must be alternative ways of writing the SAME technology: abbreviations, spacing and punctuation variants, or former names. Never list a related product, a sub-framework, a plugin or a competing tool as an alias. If unsure, return an empty list.

Correct: {{"name": "PostgreSQL", "aliases": ["Postgres", "psql"]}}
Correct: {{"name": "Kubernetes", "aliases": ["K8s"]}}
Wrong: {{"name": "Svelte", "aliases": ["SvelteKit"]}} — SvelteKit is a separate framework
Wrong: {{"name": "CSS", "aliases": ["SASS", "SCSS"]}} — those are separate languages

Respond with only a JSON array, no other text:
[{{"name": "React", "aliases": ["React.js", "ReactJS"]}}]"""