# Generate Plugin HTML Documentation

Generate a standalone, shareable HTML documentation page for an InsightConnect plugin. The output is a single self-contained HTML file with a sidebar navigation, styled tables, and code examples — suitable for sharing with SEs, customers, or internal stakeholders.

## Input

- A plugin directory containing a `plugin.spec.yaml` and `help.md` file
- Output path for the HTML file (default: `/Users/ewilson/Documents/Kiro Work Files/<plugin_name>_plugin_docs.html`)

## Steps

### 1. Read the plugin.spec.yaml

Extract the following from the spec:
- Plugin `title`, `version`, `description`
- `connection` fields (name, type, required, description)
- `actions` (each with title, description, inputs, outputs)
- `triggers` (if any)
- `tasks` (if any)
- `types` (custom type definitions with field names, types, descriptions, examples)
- `key_features`, `requirements`
- `version_history`
- `links`, `references`
- `supported_versions`
- `troubleshooting` (if present)

### 2. Research Vendor Setup Details

Before generating the HTML, use web search to gather:
- Step-by-step instructions for creating API credentials on the vendor platform
- Permission/role/scope models and how to configure least-privilege access
- Any relevant network requirements or prerequisites

This ensures the Setup section contains enough detail for a customer to configure the vendor side without needing separate documentation.

### 3. Build the HTML structure

Use this template structure. The file must be **fully self-contained** (inline CSS, no external dependencies).

#### Document Layout
- Fixed left sidebar (260px wide, dark background `#1a1a2e`)
- Main content area (scrollable, max-width ~960px)

#### Sidebar Contents
- Brand section: plugin title + version
- "Overview" section links: Description, Key Features, Requirements, Setup, Permissions
- "Actions" section links: one link per action (use kebab-case IDs)
  - If the plugin spans multiple product lines (e.g., ZIA/ZPA/ZCC), group actions by product in the sidebar with separate section labels
- "Triggers" section links (if any)
- "Tasks" section links (if any)
- "Reference" section links: Custom Types, Version History, Links

#### Main Content Sections
For each section, use `id` attributes matching the sidebar links.

#### CSS Classes to Use
```
.badge-required  → red pill badge for required fields
.badge-optional  → blue pill badge for optional fields
.info-box        → blue left-bordered callout for setup tips
.warning-box     → amber left-bordered callout for security warnings and cautions
pre/code         → dark background code blocks for JSON examples and CLI commands
.product-badge   → small colored pill for product-line tagging on actions (e.g., ZIA, ZPA)
.perm-table      → table with bold first column for permission breakdowns
```

### 4. Render Setup & Configuration (EXPANDED)

This section must be comprehensive enough for a customer to configure the integration end-to-end without additional documentation. Include:

#### Vendor Side Setup
- **Step-by-step instructions** for creating API credentials (API keys, tokens, OAuth clients, etc.)
- **Screenshots-equivalent detail** — mention exact navigation paths in the vendor UI (e.g., "Navigate to System Settings > Admin > Administrators")
- **Key generation commands** if applicable (e.g., `openssl genrsa` for private keys)
- **Security callouts** using `.warning-box` for sensitive operations (key storage, credential handling)

#### InsightConnect Side Setup
- **Connection field table** with columns: Field, Type, Required (badge), Description
- **Info boxes** explaining how authentication works under the hood

#### Network Requirements
- Endpoints that need to be reachable (hostnames, ports)
- Proxy considerations if applicable
- Any firewall rules needed

### 5. Render Permissions & Least Privilege (REQUIRED SECTION)

Always include a dedicated Permissions section (`id="permissions"`) with:

- **Multiple permission profiles** organized by use case (e.g., Read-Only, Object Management, Full Automation)
- **Permission tables** with columns: Permission/Scope, Access Level, Rationale/Actions Enabled
- **Least-privilege guidance** — explain which profile to use for which workflows
- **Separation of concerns** — recommend using separate API credentials for different privilege levels when possible
- **Scope/RBAC mapping** — map vendor permissions to specific plugin actions so customers can audit what each credential can do

Use the `.perm-table` class for these tables (bold first column).

### 6. Render Actions

For each action:
- `<h2 id="kebab-case-name">Action Title</h2>`
- **Product badge** if the plugin spans multiple services (use `.product-badge` with product-specific colors)
- Brief description paragraph
- **Input table** with columns: Name, Type, Required (badge), Description
- **Output** section with a brief description of what's returned
- **Example output** as a formatted JSON code block (use the `example` value from the spec output, pretty-printed)
- **Warning boxes** for destructive or high-impact actions (policy installs, deletions, etc.)

### 7. Render Custom Types

For each type in `types`:
- `<h3>type_name</h3>`
- Table with columns: Field, Type, Description, Example
- Skip overly verbose internal types (e.g., nested report structures) — include the key operational types that users interact with

### 8. Render Version History

Table with columns: Version, Changes

### 9. Render Links & References

Bulleted list of external links (open in new tab). Include:
- Vendor product page
- API documentation
- Relevant setup guides from the vendor
- Permission/role documentation

### 10. Footer

Light footer with: `Rapid7 InsightConnect · {Plugin Title} Plugin v{version} · Supported Versions: {supported_versions}`

## Style Reference

```css
/* Key styles — embed these inline in the HTML <style> block */
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
.sidebar { position: fixed; width: 260px; height: 100vh; background: #1a1a2e; }
.sidebar a { color: #b0b0d0; padding: 8px 20px; }
.sidebar a:hover { background: #2d2d4e; color: #fff; }
.sidebar .section-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #6c6c8c; }
.main { margin-left: 260px; padding: 40px 60px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #f4f4f8; padding: 10px 12px; border: 1px solid #e0e0e8; }
td { padding: 8px 12px; border: 1px solid #e0e0e8; }
pre { background: #1e1e2e; color: #e0e0e0; padding: 16px 20px; border-radius: 8px; font-size: 13px; }
code { font-family: 'SF Mono', Menlo, Monaco, monospace; font-size: 12px; }
td code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.badge-required { background: #fee2e2; color: #b91c1c; }
.badge-optional { background: #e0f2fe; color: #0369a1; }
.info-box { background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 0 6px 6px 0; margin: 12px 0 20px; font-size: 13px; }
.warning-box { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 0 6px 6px 0; margin: 12px 0 20px; font-size: 13px; }
.perm-table td:first-child { font-weight: 600; white-space: nowrap; }
.product-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 4px; }
.footer { margin-top: 60px; padding: 20px 0; border-top: 1px solid #e0e0e8; font-size: 12px; color: #6c6c8c; text-align: center; }
```

## Output Rules

- Write the HTML file to the specified output path
- The file must open correctly in any browser with no external resources
- Keep JSON examples concise — show key fields, not every single field (trim output examples if they're excessively long)
- Use real example values from the spec, not placeholder text
- For `bytes` type inputs, note they accept Base64-encoded content
- For `credential_secret_key` type connection fields, show the type name but don't include secret values in examples
- Always include the expanded Setup and Permissions sections — these are not optional
- Use warning boxes for destructive actions and security-sensitive operations
- Group actions by product line in the sidebar when the plugin covers multiple services

## Example Usage

When the user says something like:
- "Generate HTML docs for the servicenow plugin"
- "Create an HTML doc page for this plugin I can share"
- "Make me a shareable HTML version of the plugin docs"

Read their `plugin.spec.yaml`, research vendor setup details, extract all metadata, and generate the HTML file following this template.
