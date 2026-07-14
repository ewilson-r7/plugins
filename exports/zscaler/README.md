# Zscaler Plugin (v2.0.0)

Zscaler SaaS security platform integration using OneAPI with OAuth 2.0 Private Key authentication. Includes ZIA, ZPA, and ZCC management capabilities.

## Actions
- **Blacklist URL** - Add a URL to the blocklist
- **Get Blacklist URL** - Retrieve the current blocklist
- **Lookup URL** - Check URL categorization
- **Get Sandbox Report for Hash** - Get sandbox analysis for a file hash
- **Create/Delete/Get Users** - Manage ZIA users
- **Get URL Category by Name** - Retrieve a URL category
- **Update URLs of URL Category** - Add/remove URLs from categories
- **Create/Get/Update/List Firewall Rules** - Manage ZIA firewall rules
- **Get Firewall/Web Logs** - Retrieve security logs
- **Get DLP Incidents** - Retrieve DLP incident data
- **Submit Threat Feed** - Submit IoCs to threat feed
- **List Application Segments / Get Server Group** - ZPA management
- **Get/Remove VPN Gateway Bypasses** - ZCC VPN gateway bypass management

## Connection
- **Client ID** - OAuth2 Client ID
- **Private Key** - RSA Private Key for JWT signing
- **Vanity Domain** - Your Zscaler vanity domain (e.g., `yourcompany`)
- **Cloud** - Zscaler cloud (e.g., `zscaler`, `zscalerone`, `zscloud`)

## Import
Upload `rapid7_zscaler_2.0.0.tar.gz` via InsightConnect Settings > Plugins > Import.

## Full Documentation
See `zscaler_plugin_docs.html` for detailed action schemas and examples.
