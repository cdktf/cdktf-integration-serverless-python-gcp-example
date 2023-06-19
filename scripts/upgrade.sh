#!/bin/bash
# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

set -ex

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE:-$0}")/.." && pwd)
CDKTF_VERSION=$1

if [ -z "$CDKTF_VERSION" ]; then
  echo "Usage: $0 <cdktf-version> <kubernetes-prebuilt-version>"
  exit 1
fi

echo "Updating to cdktf version $CDKTF_VERSION"

git checkout -b "cdktf-$CDKTF_VERSION"

cd $PROJECT_ROOT

sed -i "s/cdktf = \"~=.*\"/cdktf = \"~=$CDKTF_VERSION\"/" "$PROJECT_ROOT/Pipfile"
sed -i "s/npm install -g cdktf-cli@.*/npm install -g cdktf-cli@$CDKTF_VERSION/" "$PROJECT_ROOT/.github/workflows/synth.yml"

git add .
git commit -m "feat: update to cdktf $CDKTF_VERSION"
git push origin "cdktf-$CDKTF_VERSION"

BODY=$(cat <<EOF
- [ ] update \`cdktf-cdktf-provider-google-beta\` and \`cdktf-cdktf-provider-local\` in \`Pipfile\` to a version compatible with cdktf $CDKTF_VERSION
EOF
)

gh pr create --fill --base main --head "cdktf-$CDKTF_VERSION" --title "feat: update to cdktf $CDKTF_VERSION" --body "$BODY" --label "cdktf-update-$CDKTF_VERSION"