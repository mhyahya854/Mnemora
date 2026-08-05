---
title: "Everything We Are Deleting"
project: "Mnemora"
status: "AUTHORITATIVE"
updated: "2026-07-28"
document_role: "Master Plan 2 of 3"
---

# Mnemora — Everything We Are Deleting

> **Project identity and scope lock:** Mnemora uses an OpenWhispr-derived architecture. Its retained product scope is Dictation, Meeting recording, Local transcription, SQLite, Notes, Diarization, and Exact and semantic search. This deletion specification removes excluded systems without changing that retained scope.

## Governing Rule

This document defines every original system, capability, dependency, UI surface, configuration, database field, runtime path, and architectural layer that must be removed from Mnemora. A feature is not deleted merely because a button disappears. Graphify must prove and remove every applicable layer across the full architectural stack.

## Binding Deletion Interlock

Before deleting any file, symbol, dependency, schema field, setting, route, or asset, require these gates:

1. Static import/export audit
2. Dynamic import and string-reference audit
3. Renderer/preload/IPC/route/event/worker registration audit
4. Database/migration/settings/localStorage/environment audit
5. Native/asset/build/packaging audit
6. Test/fixture audit
7. Licence/future-plan dependency audit

A zero-result text search is not sufficient.

Every feature deletion must review the full applicable chain:

```text
UI
→ navigation
→ route
→ component
→ hook/store
→ preload
→ TypeScript contract
→ IPC channel
→ IPC handler
→ service
→ database/filesystem/native effect
→ settings
→ environment variables
→ dependency
→ tests
→ fixtures
→ translations
→ build
→ packaging
```

Add explicit deletion requirements for:

* Stale cloud translation strings
* Stale provider placeholders
* Stale runtime URLs
* Stale environment variables
* Stale preload methods
* Stale IPC declarations
* Stale IPC types
* Stale database metadata
* Stale packaging entries
* Stale feature flags
* Stale tests
* Stale fixtures
* Stale OpenWhispr identity outside legal/migration history

Historical migrations must not be deleted merely because they contain removed names. Add new forward migrations instead. Preserve user upgrade paths.

## 1. Active OpenWhispr identity

- Delete or replace the active OpenWhispr product name, display name, logos, icons, tray/loading/onboarding/About identity, executable, installer, package name, app ID, custom protocol, app-data/cache/log/database namespaces, localStorage/environment prefixes, release URLs, update feed, original GitHub publish target, Gizmo Labs signing configuration, Windows publisher identity, macOS signing identity, and stale packaged strings.
- Retain old names only for legal attribution, source history, legacy data migration, or legacy protocol compatibility.
- Stale OpenWhispr identity outside legal/migration history must be explicitly deleted across all UI, packaging, and configuration layers.

## 2. Authentication and accounts

- Delete sign-in/out, account creation, social login, OAuth, SSO, verification, password reset, account deletion, profile, account settings, session/grace/refresh logic, bearer/auth/session tokens, cookies, auth keychain entries, localStorage keys, environment variables, callbacks, routes, onboarding, IPC, preload, types, tests, translations, and remote auth endpoints.
- Remove `better-auth`, `@better-auth/sso`, and other auth-only packages after all consumers are gone.

## 3. Cloud synchronization

- Delete SyncService, auto-sync startup, background timers, note/folder/tag/snippet/transcript/recording/speaker sync, remote conflict resolution, cloud queues/retries/status/errors/notifications, cloud IDs/revisions/timestamps, auth/workspace/team sync, IPC, preload, types, settings, environment variables, tests, docs, translations, and cloud persistence fallbacks.

## 4. Workspaces, organisations, and teams

- Delete workspace services/stores/switchers/creation/deletion/selection/settings/members/teams/roles/permissions/billing/developer/API keys; organisation management and ownership; team management/membership/permissions/ownership/billing; role assignment; collaboration access control; routes/navigation; fields/migrations/flags/translations/tests/docs.

## 5. Invitations and sharing

- Delete invitations, tokens, links, acceptance/rejection, invitation bridge, teammate dialogs, shared-note visibility, shared folders/notes, share links/tokens/dialogs/menus, public share routes, APIs, stores, services, IPC, preload, fields, flags, translations, tests, and remote permissions.

## 6. Hosted transcription providers

- Delete OpenAI transcription/realtime, Groq, Deepgram, AssemblyAI, Corti, Tinfoil, Azure, Amazon, Google-hosted transcription, enterprise providers, remote OpenAI-compatible endpoints, self-hosted remote servers, provider auth/keys/tests/errors/retries/usage/billing/sockets/uploads/chunking/model selectors/settings/env/IPC/preload/docs/translations, and every cloud fallback.
- Locate and delete names such as `assemblyAiStreaming`, `deepgramStreaming`, `openaiRealtimeStreaming`, `cortiAuth`, `cortiStreaming`, `cortiTranscription`, `tinfoilCatalog`, `tinfoilSecureClient`, `tinfoilTranscription`, `selfHostedTranscription`, `transcriptionAuth`, `enterpriseAiProviders`, and `enterpriseProviderErrors`.

## 7. Hosted AI and provider systems

- Delete OpenAI, Anthropic, Google AI, Vertex, Groq reasoning, Azure AI, Bedrock, Tinfoil AI, hosted compatible models, enterprise provider configuration, selectors, keys, tests, errors, usage/quota logic, remote inference, hosted summarization/rewriting/extraction/reasoning/note enhancement.
- Remove `ai`, all unused `@ai-sdk/*`, unused `@aws-sdk/*`, `tinfoil`, and all hosted-provider SDKs after consumers are removed.

## 8. AI agents and chat

- Delete AI/voice agent, agent hotkey/window/overlay/name/personality/prompts/commands/detection/function calling/tool calling/action processing, background actions, chat UI/history/stores, transcript/note/meeting chat, reasoning services, local reasoning bridge for the first release, AI note actions, rewrite, summaries, action items, enhancement, processing overlays/toasts, agent settings, inference editor, routes, IPC, preload, types, tests, translations, and docs.
- Audit likely areas such as AgentOverlay, components/agent, components/chat, ReasoningModelSelector, ChatAgentSettings, DictationAgentSettings, InferenceConfigEditor, services/ai, BaseReasoningService, ReasoningService, LocalReasoningService, localReasoningBridge, chatStore, actionStore, actionProcessingStore, prompt configuration, and tool registries.

## 9. Agent tools and remote actions

- Delete web search, calendar tool, AI clipboard/create-note/update-note tools, remote actions, remote tool registry, agent-only definitions, tool-call routes/IPC/tests/docs.
- Do not delete normal clipboard support or direct local services.

## 10. Google Calendar and remote calendars

- Delete OAuth, manager, API calls, access/refresh tokens, event types, upcoming event/meeting fetching, integration cards, settings, linked meetings/metadata/reminders, calendar tool, IPC, preload, types, fields/migrations/env/tests/translations/docs.

## 11. MCP, public API, and CLI authentication

- Delete MCP card/server/startup/configuration, public network API, notes/transcript/automation APIs, routes/listeners, token/key generation, remote auth, CLI login, developer screens/settings, agent API skills, remote API docs/tests, and automation routes.
- Retain internal typed Electron IPC only.

## 12. API-key and provider configuration

- Delete API-key services/settings/storage/validation/IPC/preload/types/tests/translations; all OpenAI/Anthropic/Groq/Google/Azure/AWS/Bedrock/Deepgram/AssemblyAI/Corti/Tinfoil credentials; enterprise provider settings; remote endpoint URLs; organisation IDs; model selectors; connection tests; status indicators.
- Remove OS keyring support if no retained local feature uses it.

## 13. Billing, usage, referrals, and upgrades

- Delete subscription/account-tier/plan/credit/quota/counter/blocking displays, billing routes/settings/pricing, upgrade prompts/buttons, enterprise sales, referral dashboards/modals/cards/links, team/workspace/organisation billing, feature gating, subscription checks, IPC/preload/fields/tests/translations/docs.

## 14. Automatic updates

- Delete `electron-updater`, updater service/hooks/polling/timers/checks/download/install/overlay/routes/IPC/preload/types/settings/tests/translations, GitHub release checks, old update feed, old publish target, and automatic update URLs.

## 15. Runtime model and binary downloads

- Delete runtime download actions/UI/IPC/preload/settings/tests/URLs for Whisper models/binaries/server, embedding models, diarization, VAD, Qdrant, Sherpa-ONNX, Parakeet, llama-server, Hugging Face, and GitHub binaries.
- Build-time acquisition may remain only if isolated from production runtime.

## 16. External runtime networking

- Delete or block external HTTP/HTTPS/WS/WSS/EventSource, external redirects, auth/cloud/calendar/sync/update/embedding/vector/analytics/telemetry/web-search/model-download requests, automatic external documentation links, browser callbacks, external listeners, and hidden remote fallbacks.
- Only IPC, local files/assets, localhost, loopback, local Whisper, local Qdrant, and approved bundled local services remain.

## 17. Cloud audio and streaming

- Delete provider upload preparation, provider-specific stream conversion, remote sockets/auth/retry/chunk upload/queues/sessions/reconnect logic and cloud real-time streaming.
- Retain local conversion/chunking required for local engines.

## 18. Remote speaker systems

- Delete remote diarization, cloud recognition, account-based profiles, cross-device/workspace/team profile sync, cloud fingerprints, APIs, IDs, tests, and settings.

## 19. Cloud metadata in local data

- Remove safely through forward migrations: cloud note/transcript/recording/folder/sync/revision/owner/account/workspace/organisation/team IDs, sharing visibility/tokens, remote versions/conflicts/timestamps, billing/subscription state, credentials, calendar tokens, and remote integration state.
- Historical migrations must not be deleted merely because they contain removed names. Add new forward migrations instead. Preserve user upgrade paths.
- Never delete user content while removing metadata.

## 20. Navigation and UI

- Delete account/sign-in/profile/upgrade/usage/billing/referral/workspace/organisation/team/member/invitation/share/integration/calendar/API-key/developer/MCP/agent/chat/provider/cloud-sync/remote-model/download/update navigation, screens, empty panels, dead buttons/routes/overlays/dialogs/settings, stale copy, cloud errors, and upgrade text.

## 21. Onboarding

- Delete account/sign-in/verification/password/cloud-provider/API-key/workspace/team/calendar/agent/hosted-model/subscription/pricing/sync/runtime-download/referral/upgrade steps.

## 22. Settings

- Delete settings and state for account, auth, cloud sync, workspaces, teams, invitations, sharing, calendar, agents, chat, hosted inference/transcription, API keys, enterprise providers, billing, usage, referrals, upgrades, updater, runtime downloads, endpoints, web search, public API, and MCP.
- Remove stale settings from stores, SQLite, localStorage, environment variables, preload, types, tests, and translations.

## 23. Notifications and hotkeys

- Delete agent/voice-agent hotkeys, update/account/session/usage/quota/upgrade/sync/calendar/referral/provider/billing notifications, and automatic external-link prompts.

## 24. Native and packaging remnants

- Delete native helpers used only by removed systems, unused binaries, dead native build scripts, runtime native downloads, original signing/publisher/update/publish settings, packaging entries for removed services, old asset names/protocol/app IDs, and unnecessary network permissions.

## 25. Dependencies

- Delete `better-auth`, `@better-auth/sso`, `ai`, unused `@ai-sdk/*`, unused `@aws-sdk/*`, `tinfoil`, `electron-updater`, remote provider SDKs, auth/SSO/cloud/billing/referral/calendar/public-API packages, unused WebSockets/keyring/download packages, and every dependency without a verified retained consumer.

## 26. Dead code and bloat

- After Graphify proof, delete unused imports/exports/files/branches/components/hooks/stores/services/helpers/workers/IPC/preload/types/routes/events/adapters/schemas/flags/folders/scripts/duplicates/wrappers/pass-throughs/validation/conversion/types/factories/state/compatibility layers/commented implementations/backups/.old/.bak/copies/generated artefacts/stale translations/env/tests/docs/dependencies.

## 27. Generic dumping grounds

- Reduce or remove helpers, utils, services, common, misc, other, temp, new, old, legacy, stuff, and general only after assigning every retained symbol a precise capability owner and moving it safely.

## 28. Markdown from Codebase

- Move every tracked `.md`, `.markdown`, `.mdown`, and `.mkd` file out of Codebase into Graphify, including README, agent instructions, plans, architecture, status, tests plans, handoffs, prompts, troubleshooting, release notes, imported reports, and generated maps.
- Legal files in Codebase must use plain-text filenames without extensions (`LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`). No `.md` legal exceptions are permitted in Codebase.
- User-generated Markdown export remains supported as an output feature.

## Protected Until Proven Otherwise

- Real user recordings, transcripts, notes, databases, exports, and backups
- Database migrations (historical migrations must be preserved)
- Native and installer resources
- Dynamic assets and localisation
- Templates and public assets
- Test fixtures
- Legal notices
- Runtime-loaded modules
- Required generated files
- Models, binaries, and platform-specific implementations

## Final Deletion Acceptance

Every deletion requires passing all 7 gates of the Binding Deletion Interlock, auditing the full 18-layer architectural chain, adding forward migrations while preserving historical migrations and upgrade paths, and ensuring zero stale references remain in imports, IPC, preload, types, database metadata, environment variables, translations, packaging, tests, or fixtures. An entry must be recorded in the Graphify deletion ledger.
