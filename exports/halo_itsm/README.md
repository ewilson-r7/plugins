# Halo ITSM Plugin (v1.0.0)

Create, get, update, delete, and list tickets in Halo ITSM with action notes and file attachments.

## Actions
- **Create Ticket** - Create a new ticket with summary, details, priority, and type
- **Get Ticket** - Retrieve a ticket by ID
- **Update Ticket** - Update ticket fields (status, priority, assignment, etc.)
- **Delete Ticket** - Delete a ticket by ID
- **List Tickets** - List tickets with optional filtering
- **Add Action to Ticket** - Add an action/note to a ticket
- **Attach File to Ticket** - Attach a file to a ticket

## Connection
- **Base URL** - Halo ITSM instance URL (e.g., `https://yourorg.halopsa.com`)
- **Client ID** - OAuth2 Client ID from your Halo API application
- **Client Secret** - OAuth2 Client Secret

## Import
Upload `rapid7_halo_itsm_1.0.0.tar.gz` via InsightConnect Settings > Plugins > Import.

## Full Documentation
See `halo_itsm_plugin_docs.html` for detailed action schemas and examples.
