---
description: Snapshot the current session — update CLAUDE.md, ERRORS.md, and memory
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, PowerShell
---

Save a checkpoint of this session by updating CLAUDE.md, ERRORS.md, and the persistent memory system. All files are plain Markdown (.md) — never create Word documents or any other format.

## Step 1: Review the session

Scan the conversation for:
- Project structure changes (new files, moved files, renamed files)
- Bugs found and how they were fixed
- Errors encountered and their root causes / resolutions
- Decisions made (why one approach was chosen over another)
- Environment or configuration quirks discovered
- Anything that would have saved time if known at the start

## Step 2: Update CLAUDE.md

CLAUDE.md lives at the project root (`CLAUDE.md`). Create it if it does not exist.

CLAUDE.md should contain:
- **Project overview** — what this project is and what it does (1–3 sentences)
- **File structure** — key directories and what lives in each
- **How to install / develop** — the exact commands to install, run, or update
- **Environment** — Minecraft install path, platform notes, any quirks
- **Key files** — the most important files and their purpose
- **Gotchas** — non-obvious things that would trip up a future session

Rules for CLAUDE.md:
- One line per fact; no verbose paragraphs
- Only add things that are not obvious from reading the files
- Do not duplicate what ERRORS.md tracks

Read the existing CLAUDE.md before editing. Preserve any content that is still accurate. Add new sections or lines for anything discovered this session. Remove anything that is now outdated.

## Step 3: Update ERRORS.md

ERRORS.md lives at the project root (`ERRORS.md`). Create it if it does not exist.

Each entry should follow this format:

```
## <short title of the error>

**Symptom:** What the error looked like / what failed
**Root cause:** Why it happened
**Fix:** Exactly what was done to resolve it
**Date:** YYYY-MM-DD
```

Read the existing ERRORS.md before editing. Add new entries for any errors encountered this session. Do not remove old entries — they are a historical log. If there were no errors this session, create the file with a header comment and no entries.

## Step 4: Update memory

The memory system for this project lives at the path shown in the system instructions under "auto memory" — it is the `memory/` subdirectory inside the project's folder under `~/.claude/projects/`. The index file is `MEMORY.md` inside that directory.

**Create MEMORY.md as a new Markdown file if it does not exist.** Initialize it with a `# Memory Index` heading and then add pointer lines as memories are written.

Follow the memory system rules:
- Save **user** memories: preferences, expertise, how Blake likes to work
- Save **feedback** memories: corrections or confirmations of non-obvious approaches
- Save **project** memories: decisions, goals, deadlines, context behind the work
- Save **reference** memories: where to find things (Minecraft data path, key file locations)
- Do NOT save: code patterns derivable from reading files, git history, debugging recipes already captured in ERRORS.md

For each memory worth saving:
1. Write a file in the memory directory (e.g., `project_minecraft_paths.md`) with the frontmatter format and body
2. Add or update its entry in `MEMORY.md`

Check existing memory files before writing new ones — update rather than duplicate.

## Step 5: Report what changed

After all files are written, output a brief summary:

```
Checkpoint saved.

CLAUDE.md  — [added / updated / no changes]
ERRORS.md  — [N new entries / no changes]
Memory     — [N files written or updated]
```
