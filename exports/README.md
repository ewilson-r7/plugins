# Plugin Exports for InsightConnect

Pre-built plugin images ready to import into Rapid7 InsightConnect as custom plugins.

## How to Import

1. Download the `.tar.gz` file for the plugin you need
2. In InsightConnect, go to **Settings > Plugins > Import**
3. Upload the `.tar.gz` file
4. The plugin will appear in your plugin library and be available for workflows

## Available Plugins

| Plugin | Version | File |
|--------|---------|------|
| Active Directory LDAP | 11.0.0 | `active_directory_ldap/rapid7_active_directory_ldap_11.0.0.tar.gz` |
| ChatGPT | 1.0.0 | `chatgpt/rapid7_chatgpt_1.0.0.tar.gz` |
| Fortinet FortiManager | 1.0.0 | `fortinet_fortimanager/rapid7_fortinet_fortimanager_1.0.0.tar.gz` |
| Halo ITSM | 1.0.0 | `halo_itsm/rapid7_halo_itsm_1.0.0.tar.gz` |
| IP API | 1.0.0 | `ip_api/rapid7_ip_api_1.0.0.tar.gz` |
| Microsoft Office365 Email Security | 4.1.0 | `microsoft_office365_email_security/rapid7_microsoft_office365_email_security_4.1.0.tar.gz` |
| Microsoft Teams | 8.0.0 | `microsoft_teams/rapid7_microsoft_teams_8.0.0.tar.gz` |
| TeamDynamix | 1.0.0 | `teamdynamix/rapid7_teamdynamix_1.0.0.tar.gz` |
| Zscaler | 2.0.0 | `zscaler/rapid7_zscaler_2.0.0.tar.gz` |

## Documentation

Each plugin folder contains setup guides and/or reference documentation. Check the `README.md` or `.html` files in each folder for connection configuration, required permissions, and usage details.

## Notes

- These are custom/pre-release builds not yet available in the official InsightConnect Extension Library
- Built with `insight-plugin export` using SDK 6.6.0 on Python 3.13
- For source code, see the `plugins/` directory in this repository
