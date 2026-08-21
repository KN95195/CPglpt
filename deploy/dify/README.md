# Dify deployment boundary

Dify is deployed as a separate fixed-version Compose project after the base platform stack is fully validated. Its API key and workflow identifiers are stored server-side only in the platform secret store; browsers never call Dify directly.
