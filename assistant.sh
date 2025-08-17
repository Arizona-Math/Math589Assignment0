#!/bin/sh
OWNER='Arizona-Math'
REPO='Assignment0'
LOCAL='./A/Assignment0'
GITHUB_TOKEN=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
OPENAI_API_KEY=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

python repo_007.py \
  --repo https://github.com/${OWNER}/${REPO}.git \
  --task "Review code and propose patches" \
  --base main \
  --files "$LOCAL/**/*.py"
