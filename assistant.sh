#!/bin/sh
OWNER='Arizona-Math'
REPO='Math589Assignment0'
LOCAL='./Math589Assignment0'
GITHUB_TOKEN=`cat $HOME/Domains/GitHub/ForOpenAI.txt`
OPENAI_API_KEY=`cat $HOME/Domains/OpenAI/GeneralKey.txt`

export GITHUB_TOKEN
export OPENAI_API_KEY

python repo_007.py \
  --repo https://github.com/${OWNER}/${REPO}.git \
  --task "Review code and propose patches" \
  --base main \
  --branch-prefix ai/patch \
  --files "$LOCAL/**/*.py"
