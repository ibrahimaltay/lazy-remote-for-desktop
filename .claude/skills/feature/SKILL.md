---
name: feature
description: Run a feature through the full loop (plan, build, test, device QA, promo GIFs, release) by calling the right agents in order and stopping for the user where needed. Use for /feature <name>, or when the user says "let's go through features/<name>".
argument-hint: <feature folder name under docs/features/>
---

Drive docs/features/$ARGUMENTS/ through the loop below. You are the
orchestrator: subagents cannot call each other or ask the user questions, so you
relay between them and the user. Never let an agent skip its own rules (see
.claude/agents/*.md and AGENTS.md).

## 0. Branch

Before anything else, make sure you are on `feature/<name>`, where `<name>` is
$ARGUMENTS with underscores turned into hyphens. If that branch exists, `git switch`
to it; otherwise `git switch -c` it from the current branch (normally main).
Uncommitted changes come along; never commit, stash or discard them. Tell the
user which branch you are on. Never build on main.

## 1. Find where we are

Read docs/features/$ARGUMENTS/plan.md (and git status, `git log` for the branch).
If the folder does not exist, say so and stop. If plan.md does not exist, create
it from docs/features/_template/plan.md. Pick the first matching phase, tell the
user "Resuming at <phase>: <why>", and continue from there:

- No plan.md content / Status `draft` / Decisions empty -> Plan
- Status `in progress` and unchecked Steps -> Build
- Steps done, reviewer not yet clean -> Build (run `reviewer`)
- Steps done and reviewer clean, "Acceptance criteria verified" or "swift test passes" unchecked -> Test
- Tests green, no QA round started or user not yet handed a build -> Deploy
- Open rows in the QA log -> QA fix loop
- Last QA round passed, marketer box unchecked -> Marketing
- Marketing done, not released -> Release

## 2. Phases

**Plan.** Invoke the `architect` agent with the feature folder and design files.
Relay its questions and recommendations to the user with AskUserQuestion and
iterate until decisions are made. Write plan.md yourself (Goal, Design inputs,
Decisions, Scope, Constraints, Steps, Acceptance criteria). STOP: ask the user to
approve plan.md. On approval set `Status: in progress`.

**Build.** Invoke `developer` on plan.md. It ticks Steps as it goes. Then invoke
`reviewer` (read-only). Send its **Must fix** items to `developer`, then rerun
`reviewer`, until none are left; show the **Optional** items to the user. If the
two disagree whether something is a bug, STOP and ask the user.

**Test.** Invoke `tester`. If it reports failures caused by the code, pass them to
`developer`, then rerun `tester`. Repeat until the tester reports green. If the
two disagree whether code or test is wrong, STOP and ask the user. Tick the "Done
when" boxes the tester verified.

**Deploy.** Invoke `deployer` to install on the iPhone (and build the DMG if the
Mac app is affected). Pushing a `feature/*` branch is pre-authorized. Then STOP
and hand over: what was installed and what to check. Wait for the user's verdict.
Do not continue on your own.

**QA fix loop.** The user reports issues. Only the user or `tester` may write QA
log rows: ask `tester` to add what the user reports. For each issue, ask the user
for severity if unclear. Minor bug (plan right, code wrong): `developer`, then
`tester`, then Deploy again. Design or behavior problem (plan wrong): go back to
Plan for that issue, add a Decisions row, ask the user to approve the change.
When the user says a full QA round passed, tick "Last QA round" and continue.

**Marketing.** Invoke `marketer`. It proposes keep/update/merge/delete/add
decisions; STOP and show them to the user for approval before anything is deleted,
replaced or merged. Then let it render. Agents leave results staged (for example
`spotlight-new.gif` next to `spotlight.gif`) because they cannot treat a relayed
approval as the user's. When it finishes, STOP: tell the user which GIF files to
open (path, size, duration) and wait for an explicit OK. Only then do the approved
file swaps (mv, delete) yourself and tick the marketer box. Never move to Release
before the user has reviewed the GIFs.

**Release.** Invoke `deployer` for the release: it works out mac/iphone/both
(needs iPhone update to work -> iphone, needs macOS update -> mac, both -> both)
and drafts plain-English notes in docs/releases/<tag>.md. Run `/ponytail-debt` and
show its `shortcut:` ledger alongside the notes. STOP: the user edits and
approves the notes. Pushing the `feature/*` branch and cutting a `-beta` tag are
pre-authorized; confirm with the user before any production tag or anything on
main. After the release succeeds, set `Status: shipped` in plan.md, then commit
and push that follow-up to the feature branch. For iphone or both releases, the deployer
uploads to TestFlight first (ask before it runs). Then ask the user for a go to open
the PR; on their go, have `deployer` run `scripts/create-pr.sh` and show the URL.
Never merge it.

## Rules

- At every STOP, wait for the user's answer; silence is not approval.
- Pass each agent the feature folder path and tell it what to do; do not paste the
  whole plan into prompts.
- After each phase, say in one or two lines what happened and what comes next.
- If an agent's final report is empty or a placeholder, ask it to resend the real
  report before moving on.
- If an agent reports a missing script, a failed build or anything unexpected,
  stop and tell the user instead of working around it.
