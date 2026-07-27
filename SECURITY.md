# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| 0.1.x   | Best effort |

## Reporting a vulnerability

Please open a **private** security advisory on GitHub (Security → Advisories → New draft), or email the maintainer via the address on their GitHub profile.

Do not file public issues for exploitable vulnerabilities until a fix is available.

## Scope notes

This library executes **user-provided node functions** in-process. It does not sandbox LLM output, tools, or `eval`. Treat untrusted node code like any other Python you run.
