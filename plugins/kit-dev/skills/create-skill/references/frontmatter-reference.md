# YAML Frontmatter Reference

YAML frontmatter is optional metadata at the start of SKILL.md files, enclosed in `---` delimiters. Claude Code itself requires none of the fields (`name` defaults to the folder name, `description` is recommended). Commands work without any frontmatter.

## House rule for this repo

This section is the one place the allowed key list lives; other docs point here.

- **Required**: every skill declares these five keys: `name`, `description`,
  `disable-model-invocation`, `allowed-tools`, `argument-hint`.
- **Allowed**: any other field Claude Code's skills docs (code.claude.com/docs/en/skills)
  define: `when_to_use`, `arguments`, `user-invocable`, `disallowed-tools`, `model`,
  `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`,
  `license`, `compatibility`. Only the ones this repo uses are detailed below; the docs
  are authoritative for the rest.
- **Rejected**: every other key, and any key written twice. Keys are matched exactly, so
  `Model` or `when-to-use` fails.

Why the set is closed: an undocumented key is usually a typo that Claude Code silently
ignores. It also breaks portability: claude.ai uploads, the Skills API and
`package_skill.py` hard-fail on any key outside the Agent Skills spec
(`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). The
house-required `disable-model-invocation` and `argument-hint` already put these skills
outside that set, so they are Claude Code skills only.

The librarian review checklist (§2) enforces this rule.

## Required fields

```yaml
---
name: skill-name-in-kebab-case
description: What it does and when to use it. Include specific trigger phrases.
---
```

### name (required)
- kebab-case only
- No spaces or capitals
- Should match folder name
- Never use "claude" or "anthropic" (reserved)

### description (required)
- MUST include BOTH: what the skill does AND when to use it (trigger conditions)
- Max 1024 characters (the Agent Skills spec limit; the house checklist enforces it)
- Claude Code truncates `description` and `when_to_use` combined at 1,536 characters in the skill listing, so put the key use case first
- No XML tags (< or >)
- Include specific tasks/phrases users might say
- Mention file types if relevant
- Start with a verb (Review, Deploy, Generate)

## Other fields (house-required ones marked)

```yaml
---
name: skill-name
description: "[required description]"
allowed-tools: Read, Write, Edit
model: sonnet
argument-hint: "[file-path] [options]"
disable-model-invocation: true
license: MIT
compatibility: Requires network access and Python 3.10+
metadata:
  author: Company Name
  version: 1.0.0
  mcp-server: server-name
  category: productivity
  tags: [project-management, automation]
---
```

### allowed-tools (house-required)
- Pre-approves the listed tools for the turn that invokes the skill: Claude can use them without a permission prompt. The grant clears when the user sends the next message.
- It never restricts: every tool stays callable, and permission settings still govern the tools that are not listed. (Removing tools is a different field, `disallowed-tools`.)
- Omitted (or empty): nothing is pre-approved, and every tool call goes through permission settings as usual. The docs do not say this in so many words; it follows because they grant only the listed tools.
- List only the tools that should run without prompting; never pre-approve side effects nobody needs (writes, pushes, deletes, network calls the skill does not make).

**Formats:** a space- or comma-separated string, or a YAML list.

Comma-separated string:
```yaml
allowed-tools: Read, Write, Edit
```

YAML array:
```yaml
allowed-tools:
  - Read
  - Write
  - Bash(git:*)
```

Bash with command filters:
```yaml
allowed-tools: Bash(git:*), Bash(npm:*), Read
```

### model (optional)
- Values: anything `/model` accepts (e.g. `sonnet`, `opus`, `haiku`), or `inherit` to keep the active model
- Applies for the rest of the invoking turn; the session model resumes on the next prompt
- Omitted: the session model is used

### argument-hint (house-required)
- Brief hint shown in autocomplete
- Always a double-quoted string: `argument-hint: "[file-path] [options]"`. Unquoted, a value that starts with `[` is a YAML flow sequence: `[file-path]` loads as a list, not a string, and `[file-path] [options]` fails to parse, taking the whole frontmatter with it, so a stricter YAML loader drops the skill without a word. Escape an inner double quote as `\"`. The dev-cycle review checklist's strict-YAML check (in the dev-flow plugin) catches both.
- Use square brackets for each argument: `[file-path]`, `[issue-number] [options]`
- Use descriptive names, not `arg1`/`arg2`

### disable-model-invocation (house-required)
- `false` (default): Claude can load the skill automatically when it is relevant
- `true`: Skill is user-invoked only via `/<skill-name>` — use for commands requiring human judgment or with destructive effects

### context (optional)
- Set to `fork` to run the skill in an isolated subagent

### license (optional)
- Use if making skill open source
- Common: MIT, Apache-2.0

### compatibility (optional)
- 1-500 characters
- Indicates environment requirements: intended product, required system packages, network access needs, etc.

### metadata (optional)
- Any custom key-value pairs
- Suggested fields: author, version, mcp-server, category, tags, documentation, support

## Security restrictions

### Forbidden in frontmatter
- XML angle brackets (< >)
- Skills with "claude" or "anthropic" in name (reserved)

### Why
Frontmatter appears in Claude's system prompt. Malicious content could inject instructions.

### Allowed
- Any standard YAML types (strings, numbers, booleans, lists, objects)
- Custom metadata fields
- Long descriptions (up to 1024 characters)

## Common mistakes

```yaml
# Wrong - missing delimiters
name: my-skill
description: Does things

# Wrong - unclosed quotes
name: my-skill
description: "Does things

# Wrong - name has spaces or capitals
name: My Cool Skill

# Wrong - unquoted argument-hint starting with [ (a list; with a second [...] group, a parse error)
argument-hint: [file-path] [options]

# Risky - pre-approves every Bash command, side effects included
allowed-tools: Bash

# Correct
---
name: my-cool-skill
description: Does things. Use when user asks to do things.
allowed-tools: Bash(git:*), Read
---
```
