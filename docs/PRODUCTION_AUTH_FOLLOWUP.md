# Production Auth Replacement Follow-Up

This is a post-pilot follow-up. Sprint 4 launch prep keeps the current Google,
NextAuth, and backend JWT bridge behavior unchanged so deploy readiness,
monitoring, smoke checks, and pilot operations can ship independently.

## Current Pilot Behavior

- Users sign in through Google OAuth in NextAuth.
- The frontend server-side auth route calls `POST /api/auth/token`.
- The backend mints an application JWT for the existing user id.
- The token bridge requires `X-Auth-Bridge-Secret`, shared only between the
  frontend server and backend.
- Browser clients do not call the backend token bridge directly.

This is acceptable for local and staging because the bridge is protected by a
server-side shared secret and the deployment surface is small. It is not the
final production design because the backend still trusts a shared-secret bridge
instead of independently verifying an identity-provider-issued token or a
stronger first-party session exchange.

## Risks To Address Later

- Shared secret rotation and leakage handling are manual.
- Backend trust depends on the frontend bridge caller instead of direct provider
  token verification.
- There is no dedicated production session-exchange audit trail.
- Regression coverage for the browser-to-NextAuth-to-backend exchange is still
  thinner than the API-level backend tests.

## Non-Goals For Sprint 4 Launch Prep

- Do not change `POST /api/auth/token` request or response shape.
- Do not replace NextAuth.
- Do not alter Google OAuth configuration.
- Do not change frontend session storage or backend JWT claims.
- Do not block pilot deploy readiness on the final production auth design.

## Follow-Up Scope

The production auth sprint should decide and implement one explicit trust model:

1. backend verifies Google or NextAuth-issued identity tokens directly, or
2. frontend and backend use a stronger signed server-to-server session exchange.

That sprint should include:

- threat model and token lifetime decisions
- secret rotation plan
- migration path from the current bridge
- backend tests for valid, expired, malformed, and mismatched tokens
- frontend integration coverage for login, token acquisition, session creation,
  and logout
- deployment checklist for rotating auth secrets without breaking active users

## Verification Expectations

- Existing auth and session tests pass before and after the migration.
- Pilot launch smoke checks still pass:
  - `scripts/smoke-deploy.sh` for deployed service availability
  - `make smoke-local` for local auth/session CRUD flow
- New auth tests prove the backend rejects forged or stale identity material.
- Manual browser verification covers Google sign-in, dashboard load, session
  creation, message send, and logout.
