# InsightConnect Plugins - Personal Development Repo

Custom and enhanced plugins for Rapid7 InsightConnect SOAR, developed by Eric Wilson. This repository consolidates all plugin work onto a single `main` branch for easier maintenance. Individual plugins can be branched off and PR'd to [rapid7/insightconnect-plugins](https://github.com/rapid7/insightconnect-plugins) as needed.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [chatgpt](plugins/chatgpt/) | 1.0.0 | Interact with OpenAI ChatGPT to assist SOC analysts with threat analysis, incident summarization, script explanation, and response recommendations |
| [fortinet_fortimanager](plugins/fortinet_fortimanager/) | 1.0.0 | Manage FortiGate address objects, address groups, and firewall policies through FortiManager's JSON-RPC API |
| [halo_itsm](plugins/halo_itsm/) | 1.1.0 | Create, update, delete, and list tickets in Halo ITSM for automated IT service workflows |
| [ip_api](plugins/ip_api/) | 1.0.0 | Geolocate IPv4/IPv6 addresses and domain names using ip-api.com |
| [microsoft_office365_email_security](plugins/microsoft_office365_email_security/) | 4.1.0 | Office 365 email security with Tenant Allow/Block List management, message trace, compliance search, and mass purge |
| [teamdynamix](plugins/teamdynamix/) | 1.0.0 | Create, read, update, and search tickets in TeamDynamix ITSM |
| [zscaler](plugins/zscaler/) | 2.0.0 | Zscaler SaaS security platform integration rewritten for OneAPI with OAuth 2.0, including ZCC VPN gateway bypass actions |

## Project Structure

```
plugins/<plugin_name>/
├── plugin.spec.yaml           # Source of truth for the plugin
├── icon_<plugin_name>/        # Main package
│   ├── actions/<name>/        # One directory per action
│   ├── connection/            # Auth and API connection
│   ├── triggers/              # Event triggers (if any)
│   ├── tasks/                 # Polling tasks (if any)
│   └── util/                  # Shared helpers (api.py, constants.py)
└── unit_test/                 # Tests with mocked HTTP responses
```

## Development Setup

This repo uses the `insight-plugin` CLI tool for code generation and validation:

```bash
# Create a new plugin from spec
insight-plugin create

# Regenerate after spec changes
insight-plugin refresh

# Validate before submission
insight-plugin validate
```

## Kiro Configuration

The `.kiro/` directory contains development environment configuration:

- **steering/** - Context rules for plugin development conventions, testing patterns, and code structure
- **skills/** - Reusable agent skills for creating plugins, actions, workflows, and releases
- **hooks/** - Automation hooks triggered by IDE events
- **settings/** - MCP server and permissions configuration

## Changelog

### 2026-07-14
- Reorganized repository: consolidated all plugins from feature branches onto `main`
- Moved `ip_api` and `teamdynamix` into `plugins/` directory for consistency
- Added `chatgpt` plugin (v1.0.0) - SOC analyst AI assistant actions
- Added `fortinet_fortimanager` plugin (v1.0.0) - FortiManager address/policy management
- Added `halo_itsm` plugin (v1.1.0) - Halo ITSM ticket management
- Added `microsoft_office365_email_security` updates (v4.1.0) - Tenant Allow/Block List actions
- Added `zscaler` plugin rewrite (v2.0.0) - OneAPI migration with OAuth 2.0 and VPN gateway bypass
- Added `.kiro/` directory with steering docs, skills, hooks, and settings
- Cleaned up feature branches (deleted locally and from origin)

### 2026-04-23
- Initial repo setup with `ip_api` and `teamdynamix` plugins
- Added Claude Code agent configuration
- Added `.gitignore` and project scaffolding
