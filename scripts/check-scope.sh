#!/usr/bin/env bash
# Fails if the current change touches anything outside one feature slice.
#
# Usage: scripts/check-scope.sh <slice>
#   <slice>        top-level package under academy.devdojo, e.g. "enrollment"
#   BASE_BRANCH    branch to compare against (default: main; origin/<branch> is preferred when present)
#
# Compares merge-base(<base>, HEAD) with the working tree, including staged, unstaged and
# untracked files. Allowed paths for slice <s>:
#   src/main/java/academy/devdojo/<s>/**
#   src/test/java/academy/devdojo/<s>/**
#   src/main/resources/<s>/**
#   src/test/resources/<s>/**
#   src/main/resources/db/migration/<s>/**
# Everything else fails, including config/, pom.xml, .mvn/, scripts/, .github/ and docs/.
set -euo pipefail

readonly BASE_PACKAGE_PATH="academy/devdojo"

slice="${1:-}"
if [[ ! "$slice" =~ ^[a-z][a-z0-9]*$ ]]; then
    echo "usage: scripts/check-scope.sh <slice>   (slice = lowercase top-level package name, e.g. enrollment)" >&2
    exit 2
fi

cd "$(git rev-parse --show-toplevel)"

base_branch="${BASE_BRANCH:-main}"
if git rev-parse --verify --quiet "origin/${base_branch}" >/dev/null; then
    base_ref="origin/${base_branch}"
elif git rev-parse --verify --quiet "${base_branch}" >/dev/null; then
    base_ref="${base_branch}"
else
    echo "check-scope: base branch '${base_branch}' not found (set BASE_BRANCH)" >&2
    exit 2
fi
merge_base="$(git merge-base "${base_ref}" HEAD)"

allowed_prefixes=(
    "src/main/java/${BASE_PACKAGE_PATH}/${slice}/"
    "src/test/java/${BASE_PACKAGE_PATH}/${slice}/"
    "src/main/resources/${slice}/"
    "src/test/resources/${slice}/"
    "src/main/resources/db/migration/${slice}/"
)

# --no-renames lists both sides of a move, so moving a file out of a protected path is caught.
changed_files="$(
    {
        git diff --name-only --no-renames "${merge_base}"
        git ls-files --others --exclude-standard
    } | sort -u
)"

violations=0
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    if [[ "$file" == config/* || "$file" == "pom.xml" ]]; then
        echo "PROTECTED  ${file}  (guardrail configuration; only a human may change it)"
        violations=$((violations + 1))
        continue
    fi
    in_scope=false
    for prefix in "${allowed_prefixes[@]}"; do
        if [[ "$file" == "$prefix"* ]]; then
            in_scope=true
            break
        fi
    done
    if [[ "$in_scope" == false ]]; then
        echo "OUT OF SCOPE  ${file}  (not part of slice '${slice}')"
        violations=$((violations + 1))
    fi
done <<< "$changed_files"

if ((violations > 0)); then
    echo
    echo "check-scope: ${violations} file(s) outside slice '${slice}' changed relative to ${base_ref}."
    echo "Allowed paths:"
    printf '  %s\n' "${allowed_prefixes[@]}"
    echo "Revert those changes, or ask a human if the change is genuinely needed outside the slice."
    exit 1
fi

echo "check-scope: all changes are inside slice '${slice}' (compared to ${base_ref})."
