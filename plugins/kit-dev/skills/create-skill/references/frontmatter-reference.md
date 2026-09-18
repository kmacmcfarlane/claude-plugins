# YAML Frontmatter Reference

YAML frontmatter is optional metadata at the start of SKILL.md files, enclosed in `---` delimiters. All fields except `name` are optional. Commands work without any frontmatter.

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
- Max 1024 characters (under ~60 chars recommended if clean `/help` display matters)
- No XML tags (< or >)
- Include specific tasks/phrases users might say
- Mention file types if relevant
- Start with a verb (Review, Deploy, Generate)

## Optional fields

```yaml
---
name: skill-name
description: [required description]
allowed-tools: Read, Write, Edit
model: sonnet
argument-hint: [file-path] [options]
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

### allowed-tools (optional)
- Restricts which tools the skill can use
- Default: inherits from conversation permissions
- Be as restrictive as possible

**Formats:**

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
- Values: `sonnet`, `opus`, `haiku`
- Default: inherits from conversation
- Use `haiku` for simple/fast tasks, `opus` for complex analysis, omit for default `sonnet`

### argument-hint (optional)
- Brief hint shown in autocomplete
- Use square brackets for each argument: `[file-path]`, `[issue-number] [options]`
- Use descriptive names, not `arg1`/`arg2`

### disable-model-invocation (optional)
- `false` (default): Skill can be invoked programmatically by Claude via SlashCommand tool
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

# Wrong - Bash without command filter
allowed-tools: Bash

# Correct
---
name: my-cool-skill
description: Does things. Use when user asks to do things.
allowed-tools: Bash(git:*), Read
---
```
