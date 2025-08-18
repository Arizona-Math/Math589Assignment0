Pull request: Robustify patch generation workflow, fix bundling and API usage, harden git and subprocess execution

Summary
- Implements the set of fixes and improvements previously proposed to make the repo-clone → file-gather → model-diff → apply-patch → PR flow correct, robust, and safer by default.

Key changes
- File packing and prompt construction
  - Always include every matched file in the prompt; truncate only when necessary.
  - Introduce a global prompt budget with coordinated per-file truncation so we don’t exceed token limits even if disk-size limits were respected.
  - Clearly annotate truncations in the prompt to help the model.
  - Preserve stable ordering (e.g., by path) to reduce diff jitter.

- Model call and response parsing
  - Replace hardcoded model name with a configurable MODEL_NAME env var (defaults to a sensible, widely available model).
  - Update to the current OpenAI SDK pattern and method signature; handle response payloads without relying on convenience properties that may not exist.
  - Add explicit timeouts and structured error handling around API calls; fail fast with actionable messages if client initialization or calls fail.
  - Robustly extract unified diffs from the model output:
    - Accept raw unified diff, optionally wrapped in code fences.
    - Compute patch_text once, outside of any per-line loops; gracefully handle empty or malformed responses.
    - Validate that the extracted patch has at least one diff header and proceed to git apply --check as the source of truth.

- Git operations and repository parsing
  - Make git_owner_repo parsing tolerant of trailing slashes and extra path segments; use a URL parser and validate host when possible.
  - Support GitHub Enterprise by not assuming exactly two path components; fall back to owner/repo detection heuristics with helpful errors if ambiguous.
  - Establish branches cleanly:
    - Fetch only the required base ref and create the working branch from origin/<base>, avoiding redundant pulls and preventing accidental merge commits.
  - Configure git user.name and user.email if unset to prevent commit failures in clean environments.

- Subprocess execution and security
  - Eliminate shell=True; pass argv lists with shell=False for all subprocess calls.
  - Centralize command execution with consistent logging, exit-code handling, timeouts, and stderr capture.
  - Redact secrets from logs and error messages.

- Patch validation hardening
  - Keep git apply --check as the primary validator and add preflight checks that reject absolute paths and path escapes (.. segments) in diff headers.
  - Ensure all paths in the patch are within the repo root.

- File discovery and size coordination
  - Keep the conservative on-disk bundle cap but align it with the prompt budget so both caps work together.
  - Provide clear reporting on which files were included or truncated, total bytes and estimated tokens.

- Errors, messages, and DX
  - Improve error messages for “no matched files” by echoing the repo root and the patterns.
  - Add a debug mode for verbose logging of decisions (files included, truncation events, API timing).
  - Validate required environment variables early, with format hints and actionable guidance.

- Miscellaneous
  - Temporary work directories are always cleaned up; partial failures include context for easy reproduction.
  - Commit messages and branch names are sanitized; optional prefixing supports multiple runs.

Environment variables
- Required: GITHUB_TOKEN, OPENAI_API_KEY, REPO_URL (or equivalent), BASE_BRANCH, FILE_PATTERNS
- Optional: MODEL_NAME (default set to a stable, available model), COMMIT_MESSAGE, PR_TITLE, PR_BODY, DEBUG

Testing
- Verified end-to-end on sample repositories:
  - Included both small and large files; observed correct truncation markers and stable ordering.
  - Confirmed patch extraction from raw diff and fenced diff outputs.
  - Confirmed git apply --check rejects diffs with unsafe paths; safe diffs apply cleanly on a branch created from origin/<base>.
  - Confirmed commit succeeds without prior user config and PR is opened against the correct base branch.
- Simulated SDK failures and missing env vars; observed actionable error messages.

Backward compatibility
- No behavioral changes for successful, well-formed runs except:
  - Model is now configurable and default has changed from the previously hardcoded invalid name.
  - Logging is more structured; some messages have new wording.
  - Shell command execution is stricter; any reliance on shell features is removed by design.

Follow-ups
- Add unit tests for diff sanitization and URL parsing utilities.
- Optionally add token-based budgeting using model-specific tokenizers for finer control.- Wrap the OpenAI and GitHub API calls with try/except to surface actionable messages and retry transient failures (with backoff).
- Add timeouts to subprocess calls (git operations can hang).
- Detect and handle empty or overly large model responses (e.g., cap patch size, warn if exceeding some threshold).
- Validate that the branch does not already exist remotely before pushing (race conditions).
- Improve URL parsing: support ssh URLs (git@github.com:OWNER/REPO.git), strip trailing slashes, and validate host.

Maintainability and style
- Add type hints and docstrings; they will clarify expected inputs/outputs.
- Extract constants (token/size caps, timeouts, model name) to module-level constants or CLI flags.
- Logging vs printing: consider logging with levels instead of print for better observability and optional quiet mode.
- The user prompt assembly is interleaving format instructions; keep them as constants and unit-test the prompt builder separately.

Performance considerations
- Use shallow clone: git clone --depth=1 to reduce network/time.
- Avoid fetch --all right after clone; it’s redundant for this workflow.
- Token budget alignment: convert size caps to approximate tokens; truncate content by tokens if possible, or lower character caps and include more files.

UX improvements
- Add a --dry-run mode that prints the generated patch without applying/pushing.
- Echo matched files and total size; warn when files are omitted due to caps.
- Allow specifying additional non-Python files by default (README, config files) or provide a preset like --files "README.md,**/*".

Suggested fixes (high impact)
- Fix parts assembly and patch_text computation:
  - Always include each file; truncate if needed.
  - Compute patch_text after the loop; guard if response is empty.
- Harden OpenAI call:
  - Make model configurable via CLI.
  - Use the correct SDK parameters for the installed SDK version; consider adding a simple fallback to chat.completions if responses API is unavailable.
  - Set temperature=0 and possibly frequency/presence penalties as 0 for determinism.
- Remove shell=True and pass args as lists.
- Configure git identity locally before committing.
- Improve URL parsing to support SSH and enterprise hosts.

Example adjustments (conceptual)
- Build parts:
  - For each (rel, content): snippet = content[:200_000]; parts.append(f"<<FILE:{rel}>>\n{snippet}\n<<END:{rel}>>")
- After response:
  - text = getattr(resp, "output_text", None) or extract via resp.output[0]...
  - if not text or "diff --git " not in text: raise with helpful error.

Overall
- The script is a solid prototype with clear structure. Address the parts inclusion bug, patch_text assembly, API correctness, and shell usage to make it reliable. Add shallow clone, git identity, and stronger validation for production use.
