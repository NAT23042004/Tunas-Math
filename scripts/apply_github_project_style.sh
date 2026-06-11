#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  printf 'Usage: %s <owner> <project-number>\n' "$0" >&2
  exit 2
fi

OWNER="$1"
PROJECT_NUMBER="$2"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

require_command gh
require_command jq

FIELDS_JSON=""

refresh_fields() {
  FIELDS_JSON="$(gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" --format json --limit 50)"
}

field_id() {
  local name="$1"
  jq -r --arg name "$name" '.fields[] | select(.name == $name) | .id' <<<"$FIELDS_JSON"
}

option_id() {
  local field="$1"
  local option="$2"
  jq -r \
    --arg field "$field" \
    --arg option "$option" \
    '.fields[] | select(.name == $field) | .options[]? | select(.name == $option) | .id' \
    <<<"$FIELDS_JSON"
}

single_select_option_input() {
  local field="$1"
  local name="$2"
  local color="$3"
  local description="$4"
  local id

  id="$(option_id "$field" "$name")"

  if [[ -n "$id" ]]; then
    jq -n \
      --arg id "$id" \
      --arg name "$name" \
      --arg color "$color" \
      --arg description "$description" \
      '{id: $id, name: $name, color: $color, description: $description}'
  else
    jq -n \
      --arg name "$name" \
      --arg color "$color" \
      --arg description "$description" \
      '{name: $name, color: $color, description: $description}'
  fi
}

build_single_select_options() {
  local field="$1"
  local specs="$2"

  while IFS=$'\t' read -r name color description; do
    single_select_option_input "$field" "$name" "$color" "$description"
  done <<<"$specs" | jq -s '.'
}

ensure_single_select_field() {
  local name="$1"
  local options="$2"

  if [[ -z "$(field_id "$name")" ]]; then
    gh project field-create "$PROJECT_NUMBER" \
      --owner "$OWNER" \
      --name "$name" \
      --data-type SINGLE_SELECT \
      --single-select-options "$options" \
      --format json >/dev/null
    refresh_fields
  fi
}

update_field_options() {
  local field_name="$1"
  local options_json="$2"
  local field

  field="$(field_id "$field_name")"
  if [[ -z "$field" ]]; then
    printf 'Project field not found: %s\n' "$field_name" >&2
    exit 1
  fi

  local query='mutation($fieldId: ID!, $options: [ProjectV2SingleSelectFieldOptionInput!]) {
    updateProjectV2Field(input: { fieldId: $fieldId, singleSelectOptions: $options }) {
      projectV2Field {
        ... on ProjectV2SingleSelectField {
          name
        }
      }
    }
  }'

  jq -n \
    --arg query "$query" \
    --arg fieldId "$field" \
    --argjson options "$options_json" \
    '{ query: $query, variables: { fieldId: $fieldId, options: $options } }' |
    gh api graphql --input - --silent
}

refresh_fields

ensure_single_select_field "Status" "Backlog,Ready,In progress,In review,Done"
ensure_single_select_field "Evidence" "Not Started,Tests Added,Docs Updated,Demo Verified,CI Passed"
ensure_single_select_field "Priority" "P0,P1,P2"
ensure_single_select_field "Size" "XS,S,M,L,XL"

refresh_fields

update_status() {
  local options
  options="$(build_single_select_options "Status" $'Backlog\tGRAY\tNot ready for implementation\nReady\tBLUE\tReady to start\nIn progress\tYELLOW\tCurrently being worked on\nIn review\tPURPLE\tWaiting for review\nDone\tGREEN\tCompleted and verified')"
  update_field_options "Status" "$options"
}

update_priority() {
  local options
  options="$(build_single_select_options "Priority" $'P0\tRED\tCritical or blocking\nP1\tORANGE\tImportant for current milestone\nP2\tYELLOW\tNormal priority')"
  update_field_options "Priority" "$options"
}

update_size() {
  local options
  options="$(build_single_select_options "Size" $'XS\tGREEN\tVery small task\nS\tBLUE\tSmall task\nM\tYELLOW\tMedium task\nL\tORANGE\tLarge task\nXL\tRED\tVery large task; split if possible')"
  update_field_options "Size" "$options"
}

update_evidence() {
  local options
  options="$(build_single_select_options "Evidence" $'Not Started\tGRAY\tNo verification evidence yet\nTests Added\tBLUE\tTests or assertions added\nDocs Updated\tPURPLE\tDocumentation updated\nDemo Verified\tORANGE\tManual or CLI demo verified\nCI Passed\tGREEN\tCI or full local gates passed')"
  update_field_options "Evidence" "$options"
}

update_status
update_priority
update_size
update_evidence

printf 'Applied common GitHub Project field style to %s project %s.\n' "$OWNER" "$PROJECT_NUMBER"
