# Identity/Authorization Podcast Trend Briefing — 2026

**Researched:** 2026-09-22  
**Sources:** Identity at the Center (IDAC) eps. ~390–449; Identerati Office Hours eps. 91–100+; Apple Podcasts, Gluu.org, radio.net, IETF, OpenID Foundation.  
**Purpose:** Seed a card catalog (Laya) with the standards, specs, and concepts that practitioners are actually talking about right now.

---

## Ranked Catalog of Hot Standards, Specs & Named Concepts

Ranking is based on mention frequency and prominence across both shows in 2026. Items appearing as dedicated episodes or recurring themes score highest.

---

### 🔴 TIER 1 — Dominating Discourse (mentioned in multiple episodes, dedicated deep dives)

---

#### 1. Agentic AI Identity / AI Agent Identity Standards
- **What it is:** The emerging body of work defining how AI agents (autonomous, multi-step software) are authenticated, authorized, delegated to, and governed — covering agent identity lifecycle, authority limits, accountability chains, and session termination.
- **Org/Author:** Multiple — IETF OAuth WG, OpenID Foundation AI Identity Management CG, Anthropic/Google/Microsoft contributing drafts
- **URL:** https://openid.net/community/artificial-intelligence-identity-management/ (OpenID AIIM CG)
- **Podcast evidence:** IDAC #390 (Tobin South — "Identity Management for Agentic AI, MCP, OpenID AI Identity Management CG"), #421 (Henrique Teixeira — "AI Identity Control Plane"), #442, #443, #446, #447, #448 — every episode in H2 2026; Identerati Ep. 100 (TBAC/agents nexus)
- **⚠️ Natural language flag:** YES — "let an AI agent act on my behalf," "who is accountable when an agent does something bad"

---

#### 2. Non-Human Identity (NHI) Governance
- **What it is:** Identity lifecycle, discovery, ownership, and access governance for service accounts, API keys, bots, scripts, OAuth clients, and AI agents — the "non-person" identities that now numerically dominate enterprise infrastructure.
- **Org/Author:** Industry term; governance frameworks from IDAC community, Opal Security, Aembit, SGNL
- **URL:** https://opal.dev (example platform); broader: https://github.com/ietf-wg-wimse (WIMSE WG for workload NHI)
- **Podcast evidence:** IDAC #427 (Identiverse 2026 Preview — "non-human access now dramatically outpaces human access"), #447, #448 (Opal Security — "unified platform for human, non-human, and agent identities"), #445, #443 — constant thread throughout 2026
- **⚠️ Natural language flag:** YES — "find all service accounts that still have access after an employee left," "who owns this API key"

---

#### 3. Token-Based Access Control (TBAC)
- **What it is:** An access control model proposed by Gluu/Mike Schwartz that uses the rich context in JWT bundles (including VCs, attestation tokens, WIMSE tokens, transaction tokens) as the primary input to policy decisions — positioned as successor to RBAC/ABAC for multi-token environments.
- **Org/Author:** Gluu (Mike Schwartz), community debate with SGNL, Strata Identity
- **URL:** https://gluu.org/office-episodes/episode-100-is-tbac-the-next-big-thing/ (canonical episode); https://gluu.org/office-episodes/episode-93-is-tbac-the-future-gluu-sgnl-strata-weigh-in/
- **Podcast evidence:** Identerati Office Hours #93, #96, #100 — the signature concept of this show in 2026; referenced in Ep. #91, #94, #95, #96, #98

---

#### 4. Continuous Access Evaluation / Continuous Identity
- **What it is:** The pattern of continuously re-evaluating authorization in real time throughout a session — not just at login — so access can be revoked instantly when risk signals change. Implemented via CAEP/SSF, OAuth status lists, global token revocation.
- **Org/Author:** OpenID Foundation (Shared Signals WG), IETF OAuth WG, Microsoft (originally)
- **URL:** https://openid.net/wg/sharedsignals/
- **Podcast evidence:** IDAC #438 (Sean O'Dell — "continuous identity, shared signals"), #442, #444 (mailbag Q: "continuous session revocation and what 'terminate access' really means"), #447; Identerati #91 ("Powering Continuous Identity with OAuth and OpenID")
- **⚠️ Natural language flag:** YES — "kill access the moment someone is fired," "detect a stolen session in real time," "revoke a token mid-flight"

---

#### 5. Shared Signals Framework (SSF) / CAEP / RISC
- **What it is:** OpenID Foundation standards for transmitting security events (session revoked, credential compromised, account disabled) between identity providers and relying parties in real time. CAEP (Continuous Access Evaluation Protocol) and RISC (Risk and Incident Sharing & Collaboration) are profiles of SSF.
- **Org/Author:** OpenID Foundation Shared Signals Working Group
- **URL:** https://openid.net/wg/sharedsignals/
- **Podcast evidence:** IDAC #438, #444, #439 (Shared Signals Framework mentioned alongside C2PA); Identerati #91 — SSTs, SSF, CAEP as the infrastructure for continuous identity

---

#### 6. MCP Authorization / Model Context Protocol Auth
- **What it is:** The authorization layer in Anthropic's Model Context Protocol — how AI agents (MCP clients) obtain OAuth 2.1-based authorization to call MCP servers and access resources on behalf of users. The "auth story for agentic tool use."
- **Org/Author:** Anthropic (MCP spec), OIDF AI Identity Management CG, IETF OAuth WG
- **URL:** https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization (OAuth 2.1 + RFC 7591 + RFC 8414); https://spec.modelcontextprotocol.io
- **Podcast evidence:** IDAC #390 (Tobin South — MCP and OpenID AI Identity Management CG); numerous 2026 eps. on "standards for AI agents"
- **⚠️ Natural language flag:** YES — "grant an AI assistant permission to read my calendar," "how does an MCP server know who's calling"

---

#### 7. Transaction Tokens (Txn-Tokens)
- **What it is:** IETF OAuth WG spec (draft-ietf-oauth-transaction-tokens) that carries user identity, workload identity, and authorization context through an entire microservice call chain within a trust domain — preventing hop-to-hop security gaps and replay of access tokens.
- **Org/Author:** Atul Tulshibagwale et al., IETF OAuth Working Group
- **URL:** https://drafts.oauth.net/oauth-transaction-tokens/draft-ietf-oauth-transaction-tokens.html (latest); https://www.ietf.org/archive/id/draft-ietf-oauth-transaction-tokens-11.html; chaining profile: https://www.ietf.org/archive/id/draft-fletcher-transaction-token-chaining-profile-02.html; agents draft: https://www.ietf.org/archive/id/draft-araut-oauth-transaction-tokens-for-agents-00.html
- **Podcast evidence:** IDAC #449 — full dedicated Decoded episode with George Fletcher; referenced in multiple 2026 Identerati episodes on TBAC
- **⚠️ Natural language flag:** YES — "track one user's request as it bounces through five microservices," "one workload calling another safely"

---

#### 8. AuthZEN (OpenID Authorization API)
- **What it is:** OpenID Foundation Working Group and emerging spec defining a standard API between applications (Policy Enforcement Points) and external authorization engines (Policy Decision Points) — the "OAuth for authorization decisions."
- **Org/Author:** OpenID Foundation AuthZEN Working Group
- **URL:** https://openid.net/wg/authzen/
- **Podcast evidence:** IDAC #438 (Sean O'Dell mentions AuthZEN); IDAC #444 (mailbag: "Is externalized authorization ready for mainstream IAM?"); broadly referenced when "externalized authorization" is discussed

---

### 🟠 TIER 2 — Strongly Active (dedicated episodes or consistent thematic presence)

---

#### 9. WIMSE — Workload Identity in Multi-System Environments
- **What it is:** IETF working group defining standards for workload identity propagation and representation in cloud/microservice environments — bridging SPIFFE and OAuth-based approaches.
- **Org/Author:** IETF WIMSE Working Group (chairs: Justin Richer, Pieter Kasselman)
- **URL:** https://datatracker.ietf.org/wg/wimse/about/; https://github.com/ietf-wg-wimse
- **Podcast evidence:** Identerati #100 (explicitly named as producing new tokens for workload identity alongside transaction tokens); IDAC discussions of NHI and workload identity

---

#### 10. Zero Standing Privilege (ZSP) / Just-in-Time (JIT) Access
- **What it is:** The pattern of eliminating permanently-assigned privileged access in favor of provisioning access only at the moment it's needed, for the exact duration required, then revoking it — sometimes via TBAC or PAM tooling.
- **Org/Author:** Industry concept; operationalized by PAM vendors (CyberArk, Opal, etc.)
- **URL:** (no single spec; related to ABAC/PBAC patterns and PAM discipline)
- **Podcast evidence:** IDAC #442, #443, #447, #448 — mentioned in almost every 2026 episode; IDAC #444 (mailbag: ZSP and JIT access); Identerati #93 (TBAC as enabler of ZSP)
- **⚠️ Natural language flag:** YES — "make sure no one has standing admin access," "grant access only when the task is actually running"

---

#### 11. IPSIE — Interoperability Profiling for Secure Identity in the Enterprise
- **What it is:** OpenID Foundation Working Group producing vendor-agnostic interoperability profiles of OAuth, OIDC, SCIM, Shared Signals, passkeys, etc. — so two independent IAM implementations are actually guaranteed to work together.
- **Org/Author:** OpenID Foundation IPSIE Working Group
- **URL:** https://openid.net/wg/ipsie/
- **Podcast evidence:** Identerati #94 ("The IPSIE Standard: A New Era of Identity Interoperability") — full dedicated episode

---

#### 12. Identity Threat Detection and Response (ITDR)
- **What it is:** A security discipline (and emerging product category) for detecting, investigating, and responding to identity-based attacks in real time — extends traditional threat detection to cover credential stuffing, session hijacking, lateral movement via identity.
- **Org/Author:** Gartner coined the term; product category includes vendors like Silverfort, Illusive, Vectra
- **URL:** https://gluu.org/office-episodes/episode-92-tracking-identity-threats-before-they-track-you/
- **Podcast evidence:** Identerati #92 ("Tracking Identity Threats Before They Track You"); IDAC #405 (RSM 2026 Attack Vectors Report); recurring theme in security-focused IDAC episodes
- **⚠️ Natural language flag:** YES — "detect when an attacker is using a legitimate account," "catch identity-based lateral movement before the breach"

---

#### 13. Passkeys / WebAuthn / FIDO2
- **What it is:** The FIDO Alliance / W3C standard for phishing-resistant, passwordless authentication using public key cryptography stored on-device — now in "what comes after deployment" phase (recovery flows, NHI passkeys, enterprise rollout).
- **Org/Author:** FIDO Alliance, W3C WebAuthn WG
- **URL:** https://fidoalliance.org/passkeys/; https://www.w3.org/TR/webauthn-3/
- **Podcast evidence:** IDAC #447 (Authenticate 2026 Preview — "passkeys are solved, so what comes next"; passkey recovery as weak link); IDAC #444 (mailbag: "Passkeys, account recovery, and help desk social engineering"); FIDO Authenticate 2026 conference promos throughout

---

#### 14. EU Digital Identity Wallet / ARF / EUDIW
- **What it is:** The European Union Digital Identity Architecture and Reference Framework — mandating digital identity wallets for EU citizens by 2026/2027, enabling selective disclosure of credentials (mDL, PID, diplomas) at scale.
- **Org/Author:** European Commission; EUDI Wallet Consortium
- **URL:** https://digital-strategy.ec.europa.eu/en/policies/eudi-wallet; https://github.com/eu-digital-identity-wallet
- **Podcast evidence:** IDAC #444 (mailbag Prague question: "What should enterprises do about EU digital identity wallets?"), #427 (Identiverse 2026 Preview); Identerati #98 (Eclipse Decentralized Claims Protocol — EU Dataspace context)

---

#### 15. Verifiable Credentials (VCs) / OpenID4VC / SD-JWT VC
- **What it is:** W3C Verifiable Credentials spec + OpenID Foundation's OpenID for Verifiable Credential Issuance (OID4VCI) and Presentation (OID4VP) — machine-verifiable, cryptographically signed credential presentations, used in wallets, mDL, EUDIW, and increasingly in NHI/TBAC contexts.
- **Org/Author:** W3C VC WG; OpenID Foundation DCP Working Group
- **URL:** https://www.w3.org/TR/vc-data-model-2.0/; https://openid.net/wg/digital-credentials-protocols/
- **Podcast evidence:** Identerati #98, #100 (VCs as "decentralized tokens" in TBAC); IDAC #427 (Identiverse 2026 Preview mentions verifiable credentials)

---

#### 16. OAuth 2.1
- **What it is:** The consolidated, security-hardened successor to OAuth 2.0 — removes implicit flow and ROPC, mandates PKCE, clarifies redirect URI matching. Now draft-ietf-oauth-v2-1; MCP auth explicitly requires it.
- **Org/Author:** IETF OAuth Working Group (Dick Hardt, Aaron Parecki, Torsten Lodderstedt)
- **URL:** https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-12
- **Podcast evidence:** Referenced directly in MCP Authorization spec (ep. #390); Identerati #100 (OAuth WG producing new tokens); foundational to almost every episode

---

#### 17. Privileged Access Management (PAM) — Modern/AI-era
- **What it is:** The evolution of PAM for cloud-native and AI-agent environments — covering JIT provisioning, agent authority containment, orphaned token cleanup, and PAM for NHI. Discussed as the "enforcement arm" for zero standing privilege.
- **Org/Author:** Industry discipline; vendors CyberArk, Opal, BeyondTrust, Delinea
- **URL:** https://gluu.org/office-episodes/episode-97-patterns-and-anti-patterns-in-privileged-access-management-pam/
- **Podcast evidence:** Identerati #97 ("Patterns and Anti-patterns in PAM"); IDAC #443 ("PAM, least privilege, and just-in-time agent access"); constant thread
- **⚠️ Natural language flag:** YES — "lock down who can get admin access to production," "automatically revoke privilege when a task completes"

---

#### 18. SPIFFE / SPIRE — Workload Identity
- **What it is:** CNCF standards for assigning cryptographic, short-lived SVIDs (SPIFFE Verifiable Identity Documents) to software workloads — the practical, open-source substrate that WIMSE builds upon.
- **Org/Author:** CNCF (Cloud Native Computing Foundation); Hewlett Packard Enterprise, Scytale
- **URL:** https://spiffe.io/; https://github.com/spiffe/spire
- **Podcast evidence:** Referenced in NHI and workload identity discussions; WIMSE WG cites SPIFFE as prior art; IDAC discussions of "one workload calling another safely"

---

### 🟡 TIER 3 — Active and Relevant (regularly mentioned, sometimes dedicated episodes)

---

#### 19. FAPI 2.0 — Financial-grade API
- **What it is:** OpenID Foundation security profile for high-assurance APIs (banking, healthcare, government) — mandates DPoP, PAR, JARM, and narrow scoping. The "gold standard" OAuth profile increasingly cited in enterprise IAM.
- **Org/Author:** OpenID Foundation FAPI Working Group
- **URL:** https://openid.net/wg/fapi/
- **Podcast evidence:** Referenced in "externalized authorization" and open banking discussions; Identerati #96 (iShare — EU TBAC in open banking uses FAPI-adjacent patterns)

---

#### 20. DPoP — Demonstrating Proof of Possession
- **What it is:** IETF RFC 9449 — binds OAuth access tokens to a specific client's keypair, preventing token replay if stolen. Required by FAPI 2.0, increasingly recommended for enterprise OAuth.
- **Org/Author:** IETF OAuth Working Group
- **URL:** https://datatracker.ietf.org/doc/html/rfc9449
- **Podcast evidence:** Referenced in FAPI 2.0 and token security discussions; IDAC #449 (token security across microservices — related concept)

---

#### 21. Rich Authorization Requests (RAR)
- **What it is:** IETF RFC 9396 — lets OAuth clients express fine-grained, structured authorization intent (e.g., "transfer $50 to account X") in the authorization request, rather than just scopes. Enables TBAC-style rich context.
- **Org/Author:** IETF OAuth Working Group (Torsten Lodderstedt, Justin Richer)
- **URL:** https://datatracker.ietf.org/doc/html/rfc9396
- **Podcast evidence:** Part of the "externalized authorization" and TBAC discussions — how do you get rich context into a token?

---

#### 22. OAuth 2.0 Token Exchange (RFC 8693)
- **What it is:** Standard for exchanging one token type for another — e.g., converting a user's access token into an impersonation or delegation token for a service. Foundation for agentic delegation and Txn-Token issuance.
- **Org/Author:** IETF OAuth Working Group
- **URL:** https://datatracker.ietf.org/doc/html/rfc8693
- **Podcast evidence:** IDAC #449 (transaction tokens and delegated authorization — token exchange as mechanism); agentic identity discussions

---

#### 23. SCIM — System for Cross-domain Identity Management
- **What it is:** IETF RFC 7644 — standard protocol for provisioning and deprovisioning user identities across enterprise systems. Increasingly referenced as the lifecycle management layer in IPSIE and NHI governance.
- **Org/Author:** IETF; IPSIE WG uses SCIM as a component
- **URL:** https://datatracker.ietf.org/doc/html/rfc7644; https://www.simplecloud.info/
- **Podcast evidence:** Referenced in IPSIE (ep. 94) as one of the specs IPSIE profiles; identity lifecycle in NHI governance discussions

---

#### 24. OpenID Provider Commands (OPC)
- **What it is:** Proposed protocol (Dick Hardt, Karl McGuinness) for an OpenID Provider to send backchannel "command tokens" to Relying Parties — activate, suspend, archive, delete, unauthorize accounts — solving account lifecycle management at scale.
- **Org/Author:** Dick Hardt, Karl McGuinness (individuals, not yet a formal WG)
- **URL:** https://gluu.org/office-episodes/episode-99-openid-provider-commands-new-jwt-tokens-for-rp-acct-mgt/
- **Podcast evidence:** Identerati #99 — full dedicated episode with the authors

---

#### 25. "Death of Identity" / Post-Identity Architecture
- **What it is:** Provocative thesis (Bob Blakley) that traditional "identity" — the notion of a persistent, verifiable person — is dissolving under AI agents, delegation chains, and post-quantum challenges. Forces a rethink of authentication's purpose.
- **Org/Author:** Bob Blakley (independent researcher)
- **URL:** https://www.youtube.com/live/MAoWerMAdEw (Identerati Ep. 162); https://www.linkedin.com/posts/identerati-office-hours_the-death-of-identity-activity-7410406756276682752-VDNf
- **Podcast evidence:** Identerati #162 / "kick off 2026" special episode with Bob Blakley — announced as landmark episode; widely discussed across identity community on LinkedIn
- **⚠️ Natural language flag:** YES — "what even IS identity in a world of AI agents"

---

#### 26. C2PA — Content Provenance and Authenticity
- **What it is:** Coalition for Content Provenance and Authenticity — open technical spec for attaching cryptographic provenance metadata to media (images, video, audio, documents), proving origin and chain of custody in the age of deepfakes.
- **Org/Author:** C2PA (Adobe, Microsoft, Sony, BBC, ARM, Intel)
- **URL:** https://c2pa.org/
- **Podcast evidence:** IDAC #439 (Mike Kiser, SailPoint — "C2PA, Content Provenance and Authenticity, Digital Watermarking, Decentralized Identity Foundation, Intent-Based Access Control"); identity of content/media as emerging IAM frontier

---

#### 27. Intent-Based Access Control (IBAC)
- **What it is:** Emerging concept for access control that factors in the declared intent of a requester (especially an AI agent) — granting or restricting access based on what the agent claims it will do with the resource. Related to MCP's authorization model.
- **Org/Author:** Industry concept; referenced by Opal Security, SailPoint
- **URL:** (no single spec yet; see IDAC #439, #448 discussions)
- **Podcast evidence:** IDAC #439 ("Intent-Based Access Control"), #448 (Opal Security — "Can an agent declare its own intent?")
- **⚠️ Natural language flag:** YES — "only let the AI read data if its purpose matches what I authorized"

---

#### 28. PKCE — Proof Key for Code Exchange (RFC 7636)
- **What it is:** IETF extension to OAuth authorization code flow that prevents authorization code interception attacks — now mandatory in OAuth 2.1 for all public clients. Discussed as baseline hygiene.
- **Org/Author:** IETF OAuth Working Group
- **URL:** https://datatracker.ietf.org/doc/html/rfc7636
- **Podcast evidence:** Foundational to OAuth 2.1 (any episode touching OAuth); passkeys discussions

---

#### 29. mDL — Mobile Driver's License (ISO 18013-5)
- **What it is:** ISO standard for digital driving licenses on mobile devices, now deployed by US states and EUDIW. The "first mass deployment" of selective-disclosure identity credentials.
- **Org/Author:** ISO TC204; AAMVA; operationalized via OpenID4VP
- **URL:** https://www.iso.org/standard/69084.html; https://aamva.org/technology/mobile-driver-license/
- **Podcast evidence:** IDAC #427 and #447 (digital identity wallets, FIDO Authenticate 2026 agenda covering digital credentials); Identerati EU digital identity wallet discussions

---

#### 30. OAuth Status List (draft-ietf-oauth-status-list)
- **What it is:** IETF draft for a compact, privacy-preserving status list mechanism for checking whether a JWT or VC has been revoked — without revealing which specific credential is being checked.
- **Org/Author:** IETF OAuth Working Group
- **URL:** https://datatracker.ietf.org/doc/draft-ietf-oauth-status-list/
- **Podcast evidence:** Identerati #91 ("OAuth Status List JWTs" as alternative to SSF-based continuous identity)

---

#### 31. Global Token Revocation (draft-ietf-oauth-global-token-revocation)
- **What it is:** IETF draft for propagating a single revocation event across all authorization servers and resource servers in a federation — so firing an employee or detecting a breach triggers instant revocation everywhere.
- **Org/Author:** IETF OAuth Working Group
- **URL:** https://datatracker.ietf.org/doc/draft-ietf-oauth-global-token-revocation/
- **Podcast evidence:** Identerati #91, #99 (context for why continuous identity infra is needed); IDAC #444 (mailbag: "what does 'terminate access' really mean")

---

#### 32. MOSIP — Modular Open Source Identity Platform
- **What it is:** Open-source digital public infrastructure for national identity systems, deployed in 8+ countries; increasingly discussed in the context of bringing FIDO/VC standards to Global South deployments.
- **Org/Author:** MOSIP (International Institute of Information Technology, Bangalore)
- **URL:** https://mosip.io/
- **Podcast evidence:** Identerati #90 ("The Ecosystem Driving MOSIP's Mission") — dedicated episode

---

#### 33. Decentralized Identity / DIDs / DIF
- **What it is:** W3C Decentralized Identifiers (DIDs) and the broader Decentralized Identity Foundation ecosystem — identifiers that don't depend on a central registry. Referenced in VC, EUDIW, and the Eclipse Decentralized Claims discussions.
- **Org/Author:** W3C DID Working Group; Decentralized Identity Foundation (DIF)
- **URL:** https://www.w3.org/TR/did-core/; https://identity.foundation/
- **Podcast evidence:** IDAC #439 (Decentralized Identity Foundation mentioned alongside C2PA); Identerati #98 (Eclipse Decentralized Claims Protocol)

---

#### 34. AI Identity Control Plane
- **What it is:** Conceptual architecture (Henrique Teixeira/Gartner framing) proposing a dedicated management plane for AI agent identities — analogous to how cloud identity has a control plane (IAM) separate from data plane operations.
- **Org/Author:** Henrique Teixeira (Gartner); emerging industry concept
- **URL:** https://www.identityatthecenter.com/ (IDAC #421)
- **Podcast evidence:** IDAC #421 dedicated episode; referenced in #427 and subsequent AI governance episodes

---

#### 35. Prompt Injection / AI Trust Boundaries
- **What it is:** The security vulnerability where malicious content in an AI agent's input manipulates the agent's behavior — forcing it to act outside its authorized scope. Treated as an identity and access control problem.
- **Org/Author:** Security research community; OWASP LLM Top 10
- **URL:** https://owasp.org/www-project-top-10-for-large-language-model-applications/
- **Podcast evidence:** IDAC #443 ("Prompt injection and untrusted content" — full discussion within AI governance episode); referenced in trust boundary discussions

---

#### 36. OpenID Federation (OIDF Federation)
- **What it is:** OpenID spec for large-scale, multi-party federation without pre-registration — entities express trust through signed metadata and trust chains. Used in EUDIW, Swedish BankID successor, academic federations.
- **Org/Author:** OpenID Foundation AB/Connect Working Group
- **URL:** https://openid.net/specs/openid-federation-1_0.html
- **Podcast evidence:** Background to EUDIW architecture discussions; iShare episode (Identerati #96) uses federation trust patterns

---

#### 37. iShare / EU Data Spaces
- **What it is:** European cross-sector data sharing framework using TBAC/JWT-based access control for B2B data sharing under EU sovereignty rules — live in agriculture, logistics, and health sectors.
- **Org/Author:** iShare Foundation; EU Data Spaces initiative
- **URL:** https://ishare.eu/
- **Podcast evidence:** Identerati #96 ("iShare: Bringing Trust to Data with JWT-Based Access") — full dedicated episode

---

#### 38. Eclipse Decentralized Claims Protocol / Dataspaces
- **What it is:** Eclipse Foundation specification for secure data access using VC-based credentials in a decentralized "Dataspace" architecture — cross-enterprise data sharing where trust is asserted via credentials, not pre-established relationships.
- **Org/Author:** Eclipse Foundation
- **URL:** https://projects.eclipse.org/projects/technology.dataspace-protocol
- **Podcast evidence:** Identerati #98 — full dedicated episode

---

---

## Natural-Language Query → Standard Mapping
*These are the queries where a semantic model (Laya) beats string search. Each maps to one or more catalog entries above.*

| # | Natural Language Query | Maps To |
|---|------------------------|---------|
| 1 | "Let an AI agent act on my behalf without giving it all my permissions" | Agentic AI Identity, MCP Authorization, OAuth Token Exchange (RFC 8693), Transaction Tokens |
| 2 | "Kill access the moment someone is fired" | Continuous Access Evaluation, Shared Signals / CAEP, Global Token Revocation, IPSIE |
| 3 | "Detect when an attacker is using a real employee's stolen session in real time" | ITDR, Shared Signals / CAEP, RISC, Continuous Identity |
| 4 | "Track one user's request as it hops through five microservices without losing who originally called" | Transaction Tokens (Txn-Tokens), WIMSE, SPIFFE/SPIRE |
| 5 | "One workload calling another workload safely inside our cloud" | WIMSE, SPIFFE/SPIRE, Transaction Tokens, TBAC |
| 6 | "Prove I'm over 18 without showing my birthday" | Verifiable Credentials, SD-JWT VC, mDL (ISO 18013-5), OpenID4VP |
| 7 | "Make sure no one has standing admin access to production — only grant it when a task actually runs" | Zero Standing Privilege / JIT Access, PAM, TBAC, AuthZEN |
| 8 | "Find all service accounts and API keys that still have access after their owner left the company" | Non-Human Identity (NHI) Governance, IGA, PAM |
| 9 | "Ask an external policy engine whether this user can do this action, without embedding logic in my app" | AuthZEN (OpenID Authorization API), P*P architectures (PDP/PEP), ABAC/PBAC |
| 10 | "Revoke a token that's already been issued, everywhere it might be used" | Global Token Revocation, OAuth Status List, CAEP/SSF, IPSIE |
| 11 | "Grant the AI assistant permission to book meetings for me, but only this week" | MCP Authorization, OAuth 2.1 scopes, Agentic Identity (delegated authority), Intent-Based Access Control |
| 12 | "Prove this photo wasn't edited by AI" | C2PA (Content Provenance and Authenticity) |
| 13 | "Make our OAuth deployment actually work with a vendor we just bought" | IPSIE, OAuth 2.1, OpenID Connect, SCIM |
| 14 | "What even is identity when the thing acting is an AI agent, not a human?" | "Death of Identity" (Bob Blakley), Agentic AI Identity, AI Identity Control Plane |
| 15 | "Stop an AI agent from doing things its human creator isn't allowed to do" | Agentic AI Identity (authority containment), Intent-Based Access Control, Non-Human Identity governance, MCP Authorization scoping |

---

## Evidence Summary: Key Episodes Referenced

### Identity at the Center (IDAC) — 2026 Episodes
| Ep. | Guest / Topic | Key Standards Touched |
|-----|--------------|----------------------|
| #390 | Tobin South — Agentic AI, MCP, OpenID AIIM CG | Agentic Identity, MCP Auth, OpenID AIIM CG |
| #405 | David Lloret — RSM 2026 Attack Vectors | ITDR, NHI, AI-driven attacks |
| #421 | Henrique Teixeira — AI Identity Control Plane | Agentic Identity, Control Plane architecture |
| #425 | EIC 2026 Recap — Berlin | Agentic AI, CIAM, AI regulation |
| #427 | Heather Flanagan + Andi Hindle — Identiverse 2026 Preview | NHI, Passkeys, VCs, Agentic AI, ZSP, Auth as next hard problem |
| #438 | Sean O'Dell — Identiverse 2026 | Continuous Identity, Shared Signals, AuthZEN, AI identity questions |
| #439 | Mike Kiser — C2PA, Content Provenance | C2PA, Intent-Based Access Control, DIF |
| #442 | Bravura Security — Identiverse After Dark | ZSP, Agentic Auth, NHI, Standards for AI agents |
| #443 | John Huyette + Omer Arshed — AI Risk (RSM) | AI governance, PAM, Prompt Injection, Trust Boundaries |
| #444 | August Mailbag | Externalized Auth, Passkey recovery, EUDIW, Continuous Access |
| #445 | Twine Security — AI Digital Employee | NHI, IGA, AI agents, Least privilege |
| #446 | Rick Scot — Rethinking Identity for AI Agents | Agent identity taxonomy, Session termination, Shadow AI |
| #447 | Andi Hindle — Authenticate 2026 Preview | Passkeys, NHI Auth, ZSP, Continuous Identity, EUDIW |
| #448 | Howard Ting / Opal Security — NHI + Agent Governance | NHI governance, Agent intent, IGA, ZSP, Intent-Based Access |
| #449 | George Fletcher — Transaction Tokens | Txn-Tokens, OAuth WG, Agentic delegation, Cross-domain trust |

### Identerati Office Hours — Key 2026 Episodes
| Ep. | Topic | Key Standards Touched |
|-----|-------|----------------------|
| #91 | Continuous Identity with OAuth and OpenID | SSF/CAEP, OAuth Status List, Global Token Revocation, TBAC |
| #92 | ITDR — Tracking Identity Threats | ITDR, real-time identity threat detection |
| #93 | Is TBAC the Future? (Gluu, SGNL, Strata) | TBAC, ZSP, ABAC, RBAC comparison |
| #94 | IPSIE Standard | IPSIE, OAuth, OIDC, SCIM, Shared Signals |
| #95 | Are JWTs Bad for Authz? | JWT claims, token bloat, revocation, TBAC |
| #96 | iShare: JWT-Based Access | iShare, TBAC, EU data sovereignty, FAPI-adjacent |
| #97 | PAM Patterns and Anti-Patterns | PAM, least privilege, JIT |
| #98 | Eclipse Decentralized Claims | Decentralized Claims, VCs, Dataspaces, TBAC |
| #99 | OpenID Provider Commands | OPC (Hardt/McGuinness), JWT backchannel lifecycle |
| #100 | Is TBAC the Next Big Thing? | TBAC, WIMSE, Transaction Tokens, VCs, RBAC evolution |
| #162 | "Death of Identity" — Bob Blakley | Post-identity architecture, agent-era identity philosophy |

---

## Notes on Coverage Gaps / Things to Watch

1. **RAR (Rich Authorization Requests, RFC 9396)** — referenced in TBAC and authorization discussions but not yet a dedicated episode. Significant for "fine-grained authz" cards.
2. **DPoP (RFC 9449)** — implied everywhere FAPI 2.0 is discussed but not explicitly dedicated-episode featured. Should be in the catalog.
3. **PKCE (RFC 7636)** — foundational, now implicit. A card should exist but it's "solved" hygiene.
4. **SAML sunset** — referenced obliquely in IPSIE and "replacement" discussions. No dedicated episode but practitioners assume it's dying; relevant as a "what not to build on" card.
5. **OpenID Federation** — quietly important for EUDIW but not IDAC headline material yet.
6. **First-Party Native Authentication (1PNA, draft-ietf-oauth-first-party-native-flows)** — mentioned in Identerati episode context for passkeys; may appear more in fall 2026.
7. **AI "Bill of Materials" (AI BOM)** — IDAC #443 floated this as a concept for AI governance (analogous to SBOM). Not a standard yet but watch this space.

---

*Compiled from: Apple Podcasts IDAC feed (eps. 442–449 descriptions), radio.net IDAC listing, Gluu.org Identerati episode archive (eps. 91–100), IETF datatracker, OpenID Foundation WG pages, web search. All episode dates are 2026 unless otherwise noted.*
