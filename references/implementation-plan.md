# Implementation plan

Agreed scope: an English weekly Git-to-Notion skill, manually invoked, Friday through Thursday in Malaysia time. One task per meaningful outcome, combining FE/BE when appropriate.

## Built

- Standard-library Python collector with local-only reads, exact author ownership, timestamp boundaries, project filtering, merge exclusion and explicit error reporting.
- Project mappings seeded from inspected repo paths: Partnership, GTM, Lab Booking, LMS and Tracey pairs plus solo repos.
- Two author emails verified in recent work commits; historical local-machine author identity also included from Rentapp/firstApp history.
- Private Weekly Git Tasks database created with Task, Detail, Project, Week start, Week end and Commit references. Destination stored in projects.json.
- Instruction-driven grouping and Notion publishing; no additional dependency or separate Notion client.

## Validate and calibrate

1. Run deterministic checks for timezone boundaries, author filtering, merged history and branch coverage using disposable Git repos.
2. Collect a real reporting period and inspect relevant patches for a short English preview.
3. Review that first preview with the user before publishing actual tasks; adjust grouping/detail only from feedback.
4. On publishing, query existing evidence before every write and verify returned pages; test repeat execution against actual entries when publication is requested.

## Limits

No scheduled job, remote fetch, browser, source-code modifications, or automatic status claims. Locally visible unmerged work is included and must not be described as shipped. Rebased/cherry-picked work may need patch-based manual reconciliation. Excluded plugin repos, .oh-my-zsh, uBlock-Safari and the unreadable gtm-fe-snackbar-sit checkout; add any excluded project only when needed. Project inclusion is broad initially, but repos without matching owned commits produce no tasks.
