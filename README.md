# invoice-generator-skill

An agent skill that turns a plain-text file of invoice details into a finished PDF invoice. The agent organizes the information, asks you for anything missing, then calls the hosted **Invoice API** and saves the PDF.

- API (hosted): https://invoice-api.tyrolabs.dev
- Six templates: classic, modern, minimal, bold, elegant, compact. Optional logo (PNG/JPEG).

## What it does

1. You keep invoice info in any text file, however messy (see `reference/example-input.txt`).
2. The agent reads `SKILL.md`, maps the text to the API schema (`reference/schema.md`) and **asks you for missing information**, plus template and optional logo.
3. It runs `scripts/generate_invoice.sh`, which posts to the API and downloads `invoice-<number>.pdf`.

Requirements: `bash` and `curl`. No Python needed on your machine.

## Install

This repository *is* the skill folder (`SKILL.md` is at the root), so installing means putting a copy of it in the right skills directory under the name `invoice-generator`. Cloning keeps it easy to update with `git pull`.

Pick your tool. Paths are user-level (all projects). Restart the tool, or start a new session, after installing.

### Claude Code

```bash
git clone https://github.com/hasinhayder/invoice-generator-skill ~/.claude/skills/invoice-generator
```

Project-only: use `.claude/skills/invoice-generator` inside the project instead.

### Command Code

```bash
git clone https://github.com/hasinhayder/invoice-generator-skill ~/.commandcode/skills/invoice-generator
```

Project-only: `.commandcode/skills/invoice-generator`. You can also try it without installing: `commandcode --skill /path/to/invoice-generator-skill`. Browse installed skills with `/skills`.

### OpenCode

```bash
git clone https://github.com/hasinhayder/invoice-generator-skill ~/.config/opencode/skills/invoice-generator
```

Project-only: `.opencode/skills/invoice-generator`. OpenCode also discovers skills in `~/.claude/skills` and `~/.agents/skills`, so a Claude Code install already works there.

### Codex

```bash
git clone https://github.com/hasinhayder/invoice-generator-skill ~/.agents/skills/invoice-generator
```

Project-only: `.agents/skills/invoice-generator` in the repository. Older Codex versions read `~/.codex/skills/invoice-generator` instead; use that path if the skill is not picked up. In Codex, mention it explicitly with `$invoice-generator` or just ask for an invoice.

### One checkout, several tools

Clone once and symlink:

```bash
git clone https://github.com/hasinhayder/invoice-generator-skill ~/src/invoice-generator-skill
for d in ~/.claude/skills ~/.commandcode/skills ~/.config/opencode/skills ~/.agents/skills; do
  mkdir -p "$d" && ln -s ~/src/invoice-generator-skill "$d/invoice-generator"
done
```

> Skill locations and discovery rules change between releases. Claude Code and Command Code paths are confirmed; for OpenCode and Codex check the tool's own skills documentation if the skill does not show up.

## Usage

Ask your agent, for example:

> Create an invoice from `~/invoices/globex-october.txt`

It will reply with anything it needs (missing dates, % vs fixed discount, template choice, logo path) and then give you the path to the PDF.

## Test it manually

```bash
curl https://invoice-api.tyrolabs.dev/health
scripts/generate_invoice.sh my-invoice.json --logo logo.png --out .
```

JSON format: `reference/schema.md`.

## Layout

```
SKILL.md                    agent instructions (the workflow)
scripts/generate_invoice.sh API call + PDF download
reference/schema.md         field reference
reference/example-input.txt messy sample input
```
