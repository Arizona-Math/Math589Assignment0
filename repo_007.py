#!/usr/bin/env python3
import argparse, os, shlex, subprocess, tempfile, textwrap, json, pathlib, glob, requests, sys
from datetime import datetime
from urllib.parse import urlparse

# --- tiny helpers ------------------------------------------------------------

def run(cmd, cwd=None, check=True):
    print(f"$ {cmd}")
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if p.stdout: print(p.stdout)
    if p.stderr: print(p.stderr, file=sys.stderr)
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return p

def read_files(repo_dir, patterns):
    paths = set()
    for pat in patterns:
        for p in glob.glob(os.path.join(repo_dir, pat), recursive=True):
            if os.path.isfile(p):
                paths.add(os.path.relpath(p, repo_dir))
    # Basic size guard ~500 KB total
    files, total = [], 0
    for rel in sorted(paths):
        b = os.path.getsize(os.path.join(repo_dir, rel))
        if total + b > 500_000:
            continue
        with open(os.path.join(repo_dir, rel), "r", encoding="utf-8", errors="ignore") as f:
            files.append((rel, f.read()))
        total += b
    return files

def git_owner_repo(repo_url):
    # supports https://github.com/OWNER/REPO.git
    path = urlparse(repo_url).path
    owner, repo = path.strip("/").split("/")[:2]
    return owner, repo.replace(".git", "")

# --- OpenAI call -------------------------------------------------------------

def ask_gpt5_for_patch(task, files):
    # Compose compact prompt with file contents
    preface = textwrap.dedent(f"""
    You are a senior engineer. Perform the task below.
    Return a single unified diff (patch) that can be applied from repo root with `git apply`.
    Keep context minimal but correct. If creating new files, include them in the patch.
    Do not include markdown fences or commentary — only the raw unified diff.
    """).strip()

    # Few-shot style instruction about format
    guidance = "PATCH FORMAT: start each file with 'diff --git a/… b/…' and use '--- a/…' and '+++ b/…'."

    # Build file bundle (truncate long files conservatively)
    parts = []
    for rel, content in files:
        snippet = content
        if len(snippet) > 200_000:
            snippet = snippet[:200_000]
        parts.append(f"<<FILE:{rel}>>\n{snippet}\n<<END:{rel}>>")

    user_input = "\n\n".join([
        f"TASK:\n{task}",
        guidance,
        "FILES:\n" + "\n".join(parts)
    ])

    # OpenAI Responses API (Python client)
    # Docs: Responses API + GPT-5 models. 
    from openai import OpenAI
    client = OpenAI()
    resp = client.responses.create(
        model="gpt-5",
        input=[{"role":"system","content":preface},
               {"role":"user","content":user_input}],
        max_output_tokens=80_000,  # plenty for multi-file patches
    )
    # Extract text
    out_chunks = []
    for item in resp.output_text.splitlines():
        out_chunks.append(item)
    patch_text = "\n".join(out_chunks).strip()

    # sanity check
    if "diff --git " not in patch_text:
        raise RuntimeError("Model did not return a unified diff.")
    return patch_text

# --- GitHub PR ---------------------------------------------------------------

def create_pull_request(github_token, owner, repo, head_branch, base_branch, title, body):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    payload = {
        "title": title,
        "head": head_branch,
        "base": base_branch,
        "body": body,
        "maintainer_can_modify": True
    }
    r = requests.post(url, headers={
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }, json=payload, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"PR creation failed: {r.status_code} {r.text}")
    return r.json()["html_url"]

# --- main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Let GPT-5 propose a patch and open a PR.")
    ap.add_argument("--repo", required=True, help="HTTPS URL to repo (e.g., https://github.com/OWNER/REPO.git)")
    ap.add_argument("--task", required=True, help="Natural language task for GPT-5.")
    ap.add_argument("--base", default="main", help="Base branch (default: main)")
    ap.add_argument("--files", default="**/*.py", help="Comma-separated glob patterns relative to repo root")
    ap.add_argument("--branch-prefix", default="ai/patch", help="Prefix for new branch name")
    args = ap.parse_args()

    openai_key = os.getenv("OPENAI_API_KEY")
    gh_token   = os.getenv("GITHUB_TOKEN")
    if not openai_key or not gh_token:
        print("Please set OPENAI_API_KEY and GITHUB_TOKEN in your environment.", file=sys.stderr)
        sys.exit(1)

    owner, repo = git_owner_repo(args.repo)
    branch_name = f"{args.branch-prefix}/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    with tempfile.TemporaryDirectory() as d:
        run(f"git clone {shlex.quote(args.repo)} .", cwd=d)
        run(f"git fetch --all", cwd=d)
        run(f"git checkout {shlex.quote(args.base)}", cwd=d)
        run(f"git pull origin {shlex.quote(args.base)}", cwd=d)
        run(f"git checkout -b {shlex.quote(branch_name)}", cwd=d)

        patterns = [p.strip() for p in args.files.split(",")]
        files = read_files(d, patterns)
        if not files:
            print("No files matched the provided patterns.", file=sys.stderr)
            sys.exit(1)

        patch = ask_gpt5_for_patch(args.task, files)

        patch_path = os.path.join(d, "ai.patch")
        with open(patch_path, "w", encoding="utf-8") as f:
            f.write(patch)

        # Try to apply and commit
        run("git apply --check ai.patch", cwd=d)
        run("git apply ai.patch", cwd=d)
        run('git add -A', cwd=d)
        msg = f"AI patch: {args.task}"
        run(f'git commit -m {shlex.quote(msg)}', cwd=d)
        run(f"git push -u origin {shlex.quote(branch_name)}", cwd=d)

        # Open PR
        title = f"[AI] {args.task}"
        body = textwrap.dedent(f"""
        This PR was generated by GPT-5 based on the task:

        > {args.task}

        Please review carefully. The patch was applied from a unified diff produced by the model.
        """).strip()

        pr_url = create_pull_request(gh_token, owner, repo, branch_name, args.base, title, body)
        print(f"Pull Request created: {pr_url}")

if __name__ == "__main__":
    main()
