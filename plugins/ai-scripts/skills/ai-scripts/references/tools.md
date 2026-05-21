# Tools Reference

## caption_util

**Directory:** `caption_util/`
**Purpose:** Combine/split caption files for batch editing; rename files by extension.

### Usage

```bash
# Via shell wrapper (requires bin/ on PATH)
caption_util combine|split|rename [options]

# Direct Python
python caption_util/caption_util.py combine|split|rename [options]
```

### Subcommands

- **combine** — Merge multiple caption files into a single file for batch editing
- **split** — Split a combined caption file back into individual files
- **rename** — Rename files by extension

### Conventions

- Backup files are created automatically before overwriting

---

## llm_fetch

**Directory:** `llm_fetch/`
**Purpose:** Clone HuggingFace models (full repo, subdir, or single file), convert to GGUF, optionally quantize (requires llama.cpp).

### Usage

```bash
# Via shell wrapper
llm_fetch <repo-url> [--quant_type Q4_K_M] [--model_dir /path]

# Direct Python
python llm_fetch/llm_fetch.py <repo-url> [options]
```

### Features

- Supports full repo clone, subdirectory, and single-file blob/resolve URLs from HuggingFace
- Uses proper URL parsing for HuggingFace URLs
- GGUF conversion and optional quantization via llama.cpp
- Model directory configured via `llm_fetch.config.yaml`

### Configuration

- Config file: `llm_fetch.config.yaml` (gitignored; see `llm_fetch.example.yaml` as template)
- `LlamaCppDir` in config or ensure llama.cpp tools are in PATH
- Config includes version field for compatibility checking

### Dependencies

- `llm_fetch/requirements.txt`
- llama.cpp tools for conversion/quantization
- Shell wrapper manages venv automatically

---

## token_count

**Directory:** `token_count/`
**Purpose:** Count tokens using HuggingFace tokenizers.

### Usage

```bash
# Via shell wrapper
token_count --model "model-id" "text"

# Direct Python
python token_count/token_count.py --model "model-id" "text"
```

### Dependencies

- `token_count/requirements.txt`
- `token_count.sh` auto-creates and manages a `.venv` with hash-based dependency tracking

---

## token_embedding_search

**Directory:** `token_embedding_search/`
**Purpose:** Find semantically similar tokens using model embeddings (cosine similarity).

### Usage

```bash
# Via shell wrapper
token_embedding_search --model "model-id" "text"

# Direct Python
python token_embedding_search/token_embedding_search.py --model "model-id" "text"
```

---

## generate_rare_token

**Directory:** `generate_rare_token/`
**Purpose:** Find rare single-token candidates by distance from a common-token centroid.

### Usage

```bash
# Via shell wrapper
generate_rare_token --model "model-id" -n 50

# Direct Python
python generate_rare_token/generate_rare_token.py --model "model-id" -n 50
```
