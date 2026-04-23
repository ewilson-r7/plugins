# TeamDynamix

## About

[TeamDynamix](https://www.teamdynamix.com/) is an IT Service Management (ITSM) and Project Portfolio Management platform widely used in higher education and enterprise environments. This plugin integrates TeamDynamix with Rapid7 InsightConnect, enabling automated ticketing workflows—including creating remediation tickets triggered by Remediation Hub findings.

## Actions

### Create Ticket

Creates a new ticket in TeamDynamix. This is the primary action for Remediation Hub integration.

**Input:**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| title | string | Yes | Short title of the ticket | Remediate CVE-2024-1234 |
| description | string | No | Full ticket description | Critical vulnerability on host 192.168.1.10 |
| type_id | integer | Yes | TeamDynamix ticket Type ID | 123 |
| form_id | integer | No | TeamDynamix Form ID | 456 |
| account_id | integer | No | Account/Department ID | 789 |
| priority_id | integer | No | Priority ID | 20 |
| requestor_uid | string | No | Requestor user GUID | xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx |
| responsible_group_id | integer | No | Responsible group ID | 100 |
| additional_fields | object | No | Additional JSON fields | {"StatusID": 602} |

**Output:**

| Name | Type | Description |
|------|------|-------------|
| ticket_id | integer | ID of the created ticket |
| ticket_url | string | Direct URL to the ticket |
| success | boolean | Whether creation succeeded |

### Get Ticket

Retrieves a ticket by its numeric ID.

**Input:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ticket_id | integer | Yes | TeamDynamix Ticket ID |

**Output:**

| Name | Type | Description |
|------|------|-------------|
| ticket | object | Full ticket object |
| title | string | Ticket title |
| status | string | Current status name |
| ticket_id | integer | Ticket ID |

### Update Ticket

Updates fields on an existing ticket (status, title, description, priority).

**Input:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ticket_id | integer | Yes | ID of ticket to update |
| title | string | No | New title |
| description | string | No | New description |
| status_id | integer | No | New status ID |
| priority_id | integer | No | New priority ID |
| additional_fields | object | No | Additional fields |

**Output:**

| Name | Type | Description |
|------|------|-------------|
| success | boolean | Whether update succeeded |

### Search Tickets

Searches for tickets using TeamDynamix's ticket search API.

**Input:**

| Name | Type | Required | Description | Default |
|------|------|----------|-------------|---------|
| search_text | string | No | Text to search | — |
| status_id | integer | No | Filter by status ID | — |
| max_results | integer | No | Max results to return | 25 |

**Output:**

| Name | Type | Description |
|------|------|-------------|
| tickets | []object | List of matching tickets |
| count | integer | Number of results |

---

## Connection

| Name | Type | Required | Description |
|------|------|----------|-------------|
| base_url | string | Yes | TeamDynamix instance URL, e.g. https://yourorg.teamdynamix.com |
| beid | string | Yes | BEID from TeamDynamix Admin > Integration > Web API |
| web_services_key | credential_secret_key | Yes | Web Services Key from TeamDynamix Admin |
| app_id | integer | Yes | Numeric Application ID of your ticketing app |

### How to Obtain Credentials

1. Log in to TeamDynamix as an administrator.
2. Navigate to **Admin > Integration > Web API**.
3. Copy the **BEID** and create/copy a **Web Services Key**.
4. Find your **Application ID** under **Admin > Applications** — it is the numeric ID shown next to your ticketing application.

---

## Remediation Hub Workflow

To mirror the ServiceNow Remediation Hub workflow:

1. Add a **TeamDynamix – Create Ticket** step after a Remediation Hub trigger.
2. Map Remediation Hub fields to ticket inputs:
   - `{{finding.title}}` → **Title**
   - `{{finding.description}}` → **Description**
   - Set your organization's **Type ID** and **Priority ID**
3. Optionally add a **Get Ticket** step to monitor ticket status.
4. Use **Update Ticket** to close the ticket when the finding is remediated.

---

## Troubleshooting

- **Authentication failures:** Verify the BEID and Web Services Key have not expired. Regenerate from TeamDynamix Admin if needed.
- **404 on ticket actions:** Confirm the `app_id` matches the target application.
- **Missing fields on create:** Use `additional_fields` to pass any required custom attributes specific to your TeamDynamix configuration.
- **API URL format:** The plugin appends `/TDWebApi/api/{app_id}/tickets` to the base URL. Do not include `/TDWebApi` in your `base_url` connection setting.

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-04-21 | Initial release — Create, Get, Update, Search Ticket actions |

