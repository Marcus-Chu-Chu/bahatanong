# BahaTanong

*Baha* (flood) + *tanong* (question): a grounded, bilingual (English/Tagalog) data agent
over the [BahaMap](https://github.com/Marcus-Chu-Chu/bahamap) Metro Manila flood-exposure
atlas. Ask it a question; it writes SQL or searches 1,710 bilingual briefs, and every
number in its answer is validated against the tool results before you see it.

**Status:** under construction (target: live 2026-09-13). Built with Claude Code.

## Use it in Claude Desktop

Requires [uv](https://docs.astral.sh/uv/). First run downloads the embedding model (~470 MB).

```json
{
  "mcpServers": {
    "bahatanong": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Marcus-Chu-Chu/bahatanong", "bahatanong-mcp"]
    }
  }
}
```

Then ask Claude: *"Using bahatanong, which Marikina barangay has the most exposed residents?"*
