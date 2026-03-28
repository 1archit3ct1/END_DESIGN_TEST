# NextAura OAuth Provider Flow — EndDesign Spec
# Drop this into the ingestor as type: UI / Screen Design

UI Design: OAuth Provider Connection Flow

Screens:
- Header: [NextAura Logo] [Nav: Providers, Workflows, Status] [User Menu]
- Provider Grid: [Google Card] [GitHub Card] [Twitter Card] [Instagram Card] [Discord Card] [Meta Card]
- Provider Card: [Provider Logo] [Provider Name] [Connected Badge | Connect Button] [Scope Selector]
- Scope Selector: [Read toggle] [Write toggle] [Admin toggle]
- Connect Flow: [Redirect button] [Callback handler] [Token storage] [Status update]
- Credential Lifetime: [Session timer] [Expiry warning] [Revoke button]
- Workflow Gate: [Requirements checklist] [Lock icon] [Unlock workflow button]
- Connection Status: [Live indicator dot] [Last synced timestamp] [Disconnect button]

Functions:
- connectProvider: redirect to OAuth URL with correct scopes
- handleCallback: exchange code for token, validate, store in session
- revokeToken: call provider revoke endpoint, clear local state
- checkGate: verify all required providers connected before unlocking workflow
- syncStatus: poll provider for token validity, update UI
- expireCredentials: clear all tokens when workflow window closes

I/O:
- OAuth endpoints (per provider)
- Session store (in-memory, no persistence)
- Workflow eligibility event
- task_status.json (write on connect/revoke)
