# Microsoft Teams Plugin Setup Guide

This guide walks you through the complete Azure configuration required to use the InsightConnect Microsoft Teams plugin (v8.0.0+). By the end, you will have:

- An Azure App Registration with the correct permissions
- An Azure Bot registration for sending messages
- The credentials needed to configure the plugin connection

---

## Prerequisites

- An Azure account with **Global Administrator** or **Application Administrator** role (required to grant admin consent for application permissions)
- Access to the [Azure Portal](https://portal.azure.com)
- A Microsoft Teams environment where you can install apps

---

## Part 1: Create the Azure App Registration

### Step 1: Register a New Application

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** (formerly Azure Active Directory) → **App registrations**
3. Click **+ New registration**
4. Fill in the details:
   - **Name**: `InsightConnect Teams Bot` (or any descriptive name)
   - **Supported account types**: Select **Accounts in this organizational directory only (Single tenant)**
   - **Redirect URI**: Leave blank (not needed for this flow)
5. Click **Register**

### Step 2: Record Your Application (Client) ID

After registration, you'll land on the app's **Overview** page. Record these two values — you'll need them for the plugin connection:

| Field | Where to Find It | Plugin Connection Field |
|-------|-------------------|------------------------|
| **Application (client) ID** | Overview page, top section | `Application ID` |
| **Directory (tenant) ID** | Overview page, top section | `Directory ID` |

### Step 3: Create a Client Secret

1. In your app registration, go to **Certificates & secrets** → **Client secrets**
2. Click **+ New client secret**
3. Set a description (e.g., `InsightConnect Plugin`) and expiration (recommended: 24 months)
4. Click **Add**
5. **Immediately copy the Value** (not the Secret ID) — this is shown only once

| Field | Plugin Connection Field |
|-------|------------------------|
| **Client secret Value** | `Application Secret` |

> ⚠️ **Important**: The secret value is only displayed once. If you navigate away without copying it, you'll need to create a new one.

---

## Part 2: Configure API Permissions

### Step 4: Add Microsoft Graph Application Permissions

1. In your app registration, go to **API permissions**
2. Click **+ Add a permission** → **Microsoft Graph** → **Application permissions**
3. Add the permissions from the table below based on which actions you plan to use

### Permission Reference by Action

#### Minimum Permissions (Required for All Configurations)

These permissions are needed for the plugin to authenticate and perform basic operations:

| Permission | Type | Description |
|-----------|------|-------------|
| `Organization.Read.All` | Application | Used by connection test to verify authentication |

#### Permissions by Action

| Plugin Action | Required Permission(s) | Type |
|--------------|----------------------|------|
| **Get Teams** | `Group.Read.All` | Application |
| **Get Channels for Team** | `Channel.ReadBasic.All` | Application |
| **Send Message** | `Group.Read.All` + `Channel.ReadBasic.All` (to resolve names) | Application |
| **Send Message by GUID** | *(No Graph permissions — uses Bot Framework only)* | — |
| **Send HTML Message** | `Group.Read.All` + `Channel.ReadBasic.All` (to resolve names) | Application |
| **Add Member to Team** | `TeamMember.ReadWrite.All` + `User.Read.All` | Application |
| **Remove Member from Team** | `TeamMember.ReadWrite.All` + `User.Read.All` | Application |

> ⚠️ **Note**: Adding **guest users** to a team via application permissions is not supported by Microsoft. Guest users can only be added using delegated (user-signed-in) permissions. The `TeamMember.ReadWriteNonOwnerRole.All` permission is a least-privileged alternative if you only need to add members (not owners).
| **Add Channel to Team** | `Channel.Create` + `Group.Read.All` | Application |
| **Remove Channel from Team** | `Channel.Delete.All` + `Group.Read.All` + `Channel.ReadBasic.All` | Application |
| **Create Teams Enabled Group** | `Group.ReadWrite.All` + `User.Read.All` | Application |
| **Delete Team** | `Group.ReadWrite.All` | Application |
| **Add Group Owner** | `Group.ReadWrite.All` + `User.Read.All` | Application |
| **Add Member to Channel** | `ChannelMember.ReadWrite.All` + `Group.Read.All` + `Channel.ReadBasic.All` + `User.Read.All` | Application |
| **Get Message in Channel** | `ChannelMessage.Read.All` | Application |
| **Get Message in Chat** | `Chat.Read.All` | Application |
| **Get Reply List** | `ChannelMessage.Read.All` + `Group.Read.All` + `Channel.ReadBasic.All` | Application |
| **List Messages in Chat** | `Chat.Read.All` | Application |
| **Create Teams Chat** | `Chat.Create` + `TeamsAppInstallation.ReadWriteForChat.All` (if using installed_apps or auto-install) | Application |
| **New Message Received (Trigger)** | `ChannelMessage.Read.All` + `Group.Read.All` + `Channel.ReadBasic.All` | Application |

#### Recommended Permission Sets by Use Case

**Notifications Only** (send messages to channels, no management):
```
Organization.Read.All
Group.Read.All
Channel.ReadBasic.All
```

**Full Messaging** (send + read messages in channels and chats):
```
Organization.Read.All
Group.Read.All
Channel.ReadBasic.All
ChannelMessage.Read.All
Chat.Read.All
Chat.Create
```

**Full Management** (all actions including team/channel/member management):
```
Organization.Read.All
Group.Read.All
Group.ReadWrite.All
Channel.ReadBasic.All
Channel.Create
Channel.Delete.All
ChannelMessage.Read.All
ChannelMember.ReadWrite.All
TeamMember.ReadWrite.All
Chat.Read.All
Chat.Create
TeamsAppInstallation.ReadWriteForChat.All
User.Read.All
```

> **Note**: `TeamsAppInstallation.ReadWriteForChat.All` is only required if you configure the **App Catalog ID** in the connection (for automatic bot installation in chats). If you manage bot installation manually, this permission can be omitted.

### Step 5: Grant Admin Consent

After adding all required permissions:

1. Still on the **API permissions** page, click **Grant admin consent for [Your Organization]**
2. Click **Yes** to confirm
3. Verify all permissions show a green checkmark under the **Status** column with "Granted for [Your Organization]"

> ⚠️ **This step requires Global Administrator or Privileged Role Administrator**. If you don't have this role, you'll need to request consent from someone who does.

---

## Part 3: Create the Azure Bot Registration

The Bot Framework is used to send messages to Teams channels and chats without a user account. Messages will appear as coming from the bot identity.

### Step 6: Create a Bot Resource

1. In the Azure Portal, search for **Azure Bot** in the top search bar
2. Click **Create**
3. Fill in the details:
   - **Bot handle**: `InsightConnectBot` (must be globally unique)
   - **Subscription**: Select your Azure subscription
   - **Resource group**: Select an existing one or create new
   - **Data residency**: Select your preferred region (Global or regional)
   - **Pricing tier**: Select **Standard** (Free tier works for testing but has message limits)
   - **Type of App**: **Single Tenant**
   - **Creation type**: **Use existing app registration**
   - **App ID**: Paste the **Application (client) ID** from Step 2
   - **App tenant ID**: Paste the **Directory (tenant) ID** from Step 2
4. Click **Review + create** → **Create**

### Step 7: Configure the Bot Channel (Teams)

1. Once the bot resource is created, go to it in the Azure Portal
2. Navigate to **Channels** in the left menu
3. Click **Microsoft Teams** (the Teams icon)
4. Accept the Terms of Service
5. Under **Messaging**, ensure it's enabled
6. Click **Apply**

The bot is now configured to communicate with Microsoft Teams.

### Step 8: Install the Bot in Your Teams

For the bot to send messages to a specific team/channel, it must be installed in that team.

#### Option A: Install via Teams Admin Center (Recommended for Organization-Wide)

1. Go to the [Teams Admin Center](https://admin.teams.microsoft.com)
2. Navigate to **Teams apps** → **Manage apps**
3. Click **+ Upload new app** → **Upload an app to your org's app catalog**
4. You'll need to create a Teams app manifest (see below)
5. Once uploaded, go to **Setup policies** to push the app to users/teams

#### Option B: Create and Sideload a Teams App Manifest

Create a file called `manifest.json`:

```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.17/MicrosoftTeams.schema.json",
  "manifestVersion": "1.17",
  "version": "1.0.0",
  "id": "YOUR_APPLICATION_CLIENT_ID",
  "developer": {
    "name": "Your Organization",
    "websiteUrl": "https://www.rapid7.com",
    "privacyUrl": "https://www.rapid7.com/privacy-policy/",
    "termsOfUseUrl": "https://www.rapid7.com/legal/"
  },
  "name": {
    "short": "InsightConnect Bot",
    "full": "InsightConnect Automation Bot"
  },
  "description": {
    "short": "InsightConnect SOAR automation bot",
    "full": "This bot enables InsightConnect to send automated messages to Microsoft Teams channels and chats."
  },
  "icons": {
    "outline": "outline.png",
    "color": "color.png"
  },
  "accentColor": "#FF6600",
  "bots": [
    {
      "botId": "YOUR_APPLICATION_CLIENT_ID",
      "scopes": ["team", "personal", "groupChat"],
      "supportsFiles": false,
      "isNotificationOnly": true
    }
  ],
  "permissions": ["identity", "messageTeamMembers"],
  "validDomains": []
}
```

Replace `YOUR_APPLICATION_CLIENT_ID` with your actual Application (client) ID.

**To package and install:**

1. Create two icon files (32x32 `outline.png` and 192x192 `color.png`) — these can be simple placeholder images
2. Put `manifest.json`, `outline.png`, and `color.png` into a ZIP file (e.g., `insightconnect-bot.zip`)
3. In Microsoft Teams:
   - Go to **Apps** → **Manage your apps** → **Upload an app**
   - Select **Upload a custom app** (or **Upload an app to your org's app catalog** if you have admin access)
   - Upload the ZIP file
4. Add the bot to each team where you want it to send messages:
   - Go to the team → **Manage team** → **Apps** → **More apps**
   - Find "InsightConnect Bot" and click **Add**

#### Option C: Install via Microsoft Graph API (Programmatic)

```
POST https://graph.microsoft.com/v1.0/teams/{team-id}/installedApps
Content-Type: application/json

{
  "teamsApp@odata.bind": "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/{teams-app-id}"
}
```

This requires the `TeamsAppInstallation.ReadWriteForTeam.All` application permission.

---

## Part 4: Configure the Plugin Connection

With all the Azure setup complete, enter the following values in the InsightConnect Microsoft Teams plugin connection:

| Plugin Field | Value | Where You Got It |
|-------------|-------|------------------|
| **Application ID** | `63a0cad6-ac64-435c-a221-5d37c97b763e` (example) | App Registration → Overview → Application (client) ID |
| **Directory ID** | `9e538ff5-dcb2-46a9-9a28-f93b8250deb0` (example) | App Registration → Overview → Directory (tenant) ID |
| **Application Secret** | `aMeCAEYdOLlK+qRcD9AjdyxLkCaqZH1UPm7adjJQ5Og=` (example) | App Registration → Certificates & secrets → Client secret Value |
| **Endpoint** | `Normal` | Select based on your environment (Normal, GCC, GCC High, or DoD) |
| **App Catalog ID** | `05F59CEC-A742-4A50-A62E-202A57E478A4` (example) | Teams Admin Center → Manage Apps → Your bot app → App ID |

### Endpoint Selection Guide

| Environment | Endpoint Setting |
|-------------|-----------------|
| Commercial Microsoft 365 | `Normal` |
| US Government Community Cloud | `GCC` |
| US Government Community Cloud High | `GCC High` |
| US Department of Defense | `DoD` |

### App Catalog ID (Optional but Recommended)

The **App Catalog ID** enables automatic bot installation into chats. When configured:
- If the bot tries to send a message to a chat it hasn't been added to, it will **automatically install itself** and retry the message
- This eliminates the need for manual bot installation per chat or additional workflow steps

**How to find your App Catalog ID:**

1. Go to the [Teams Admin Center](https://admin.teams.microsoft.com)
2. Navigate to **Teams apps** → **Manage apps**
3. Search for your bot app by name (e.g., "InsightConnect Bot")
4. The **App ID** shown is your Teams App Catalog ID

Alternatively, query the Graph API:
```
GET https://graph.microsoft.com/v1.0/appCatalogs/teamsApps?$filter=externalId eq 'YOUR_APPLICATION_CLIENT_ID'
```

> **Note**: The App Catalog ID is NOT the same as the Azure App Registration client ID. It's the ID assigned when the app is published to your organization's Teams app catalog.

**Additional permission required when using App Catalog ID:**
- `TeamsAppInstallation.ReadWriteForChat.All` — allows the plugin to install the bot into chats automatically

---

## Part 5: Verify the Setup

### Test the Connection

1. Save the plugin connection in InsightConnect
2. The connection test will:
   - Authenticate using client_credentials flow
   - Call the Microsoft Graph API to verify permissions
3. If successful, you'll see a green "Connected" status

### Test Sending a Message

1. Create a workflow with the **Send Message by GUID** action
2. You'll need the team and channel GUIDs:
   - In Microsoft Teams, right-click the channel → **Get link to channel**
   - The link contains the IDs: `https://teams.microsoft.com/l/channel/{channel-id}/{channel-name}?groupId={team-id}`
   - **Team GUID** = the `groupId` parameter value
   - **Channel GUID** = the `channel-id` value (URL-decode it: replace `%3a` with `:` and `%40` with `@`)
3. Run the action with a test message

---

## Part 6: Common Action Examples

### Send HTML Message

Sends a formatted HTML message to a Teams channel.

**Inputs:**
| Field | Example Value |
|-------|---------------|
| Team Name | `Security Operations` |
| Channel Name | `Alerts` |
| Message Content | `<b>Alert:</b> Suspicious login detected from IP <code>192.168.1.100</code>` |
| Thread ID | *(leave empty for new message, or provide a message ID to reply in a thread)* |

**Supported HTML tags in Teams:**
- `<b>`, `<strong>` — Bold
- `<i>`, `<em>` — Italic
- `<s>`, `<strike>` — Strikethrough
- `<code>` — Inline code
- `<pre>` — Code block
- `<a href="url">text</a>` — Hyperlink
- `<br>` — Line break
- `<ul>`, `<ol>`, `<li>` — Lists
- `<h1>` through `<h3>` — Headings

**Example HTML message for an alert:**
```html
<h3>🚨 Security Alert</h3>
<p><b>Type:</b> Brute Force Attempt</p>
<p><b>Source IP:</b> <code>203.0.113.42</code></p>
<p><b>Target:</b> user@contoso.com</p>
<p><b>Attempts:</b> 47 failed logins in 5 minutes</p>
<br>
<p><a href="https://your-idr-instance.rapid7.com/investigation/abc123">View in InsightIDR</a></p>
```

### Send Message (Plain Text)

**Inputs:**
| Field | Example Value |
|-------|---------------|
| Team Name | `IT Operations` |
| Channel Name | `General` |
| Message | `Deployment to production completed successfully. Build #1234.` |

### Send Message to a Chat

**Inputs:**
| Field | Example Value |
|-------|---------------|
| Chat ID | `19:2da4c29f6d7041eca70b638b43d45437@thread.v2` |
| Message | `Your access request has been approved.` |

> **Note**: To send to a chat, the bot must be a participant. If the **App Catalog ID** is configured in the plugin connection, the bot will automatically install itself into the chat on the first message send — no manual steps needed. If App Catalog ID is not configured, you can use the **Create Teams Chat** action with the `Installed Apps` field to create a chat that includes the bot, or manually add the bot app to an existing chat via Teams.

### New Message Received (Trigger)

Polls a channel for new messages and triggers a workflow when a match is found.

**Inputs:**
| Field | Example Value | Notes |
|-------|---------------|-------|
| Team Name | `Security Operations` | Exact match |
| Channel Name | `Bot Commands` | Exact match |
| Message Content | `!investigate\s+(.+)` | Optional regex filter |

**What it returns:**
- The full message object (sender, content, timestamp)
- Extracted security indicators (IPs, URLs, hashes, emails, CVEs, MACs, UUIDs)
- Team and channel names for use in subsequent steps

### Create Teams Chat

Creates a new 1:1 or group chat, optionally with apps (bots) installed.

**Inputs:**
| Field | Example Value |
|-------|---------------|
| Members | `[{"user_info": "user1@contoso.com", "role": "owner"}, {"user_info": "user2@contoso.com", "role": "owner"}]` |
| Topic | `Incident Response - INC-2024-001` |
| Installed Apps | `["YOUR-TEAMS-APP-CATALOG-ID"]` |

> **Note**: 2 members = 1:1 chat (topic ignored). 3+ members = group chat (topic optional).

> **Tip**: If you have the **App Catalog ID** configured in the plugin connection, you don't need to use `Installed Apps` here — the bot will auto-install itself when it first sends a message to the chat. The `Installed Apps` field is useful when you want to pre-install the bot at creation time without sending a message, or when installing apps other than the configured bot.

---

## Troubleshooting

### "Bot is not authorized to send messages to this conversation"

**Cause**: The bot app is not installed in the target team or chat.

**Fix for channels**: Install the bot in the team (see Step 8 above). The bot must be added to each team where it needs to send messages to channels.

**Fix for chats**: Configure the **App Catalog ID** in the plugin connection. When set, the bot will automatically install itself into chats before sending messages. If you don't want to use auto-install, you can:
- Use the **Create Teams Chat** action with `installed_apps` to include the bot at chat creation time
- Manually add the bot app to the chat in the Teams client

### "Authentication to Microsoft Graph failed"

**Cause**: Invalid credentials or missing admin consent.

**Fix**:
1. Verify the Application ID, Directory ID, and Secret are correct
2. Ensure the client secret has not expired
3. Confirm admin consent was granted (green checkmarks on API permissions page)

### "Forbidden - The application does not have sufficient permissions"

**Cause**: Missing a required application permission or admin consent not granted.

**Fix**:
1. Go to App Registration → API permissions
2. Add the missing permission (refer to the permission table above)
3. Click "Grant admin consent" again after adding new permissions

### "Resource not found" when sending messages

**Cause**: Incorrect team/channel ID, or the bot is not installed in the team.

**Fix**:
1. Verify the team and channel names/GUIDs are correct
2. Ensure the bot is installed in the target team
3. For chat messages, ensure the bot is a participant in the chat

### "Rate limit exceeded"

**Cause**: Too many API calls in a short period. Microsoft Graph limits to approximately 10,000 requests per 10 minutes per app.

**Fix**: Add delays between actions in your workflow, or reduce trigger polling frequency.

### Messages appear as "Bot" instead of a user name

**Expected behavior**: This is by design. The plugin uses a bot identity to send messages, which eliminates the need for a user account. The bot's display name (set in the Azure Bot resource) will appear as the sender.

To customize the bot's display name:
1. Go to your Azure Bot resource
2. Navigate to **Configuration**
3. Update the **Display name** field

---

## Security Considerations

- **Least privilege**: Only grant the permissions needed for your specific use case. Refer to the permission sets above.
- **Secret rotation**: Set a calendar reminder to rotate the client secret before it expires.
- **Audit logging**: All bot activities are logged in the Azure AD sign-in logs under the application's service principal.
- **Conditional Access**: You can apply Conditional Access policies to the service principal to restrict which networks/locations can authenticate.
- **No user account**: This configuration does not require a licensed user account, eliminating MFA bypass concerns and reducing licensing costs.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│           Plugin Connection Configuration               │
├─────────────────────────────────────────────────────────┤
│  Application ID:     [App Registration Client ID]       │
│  Directory ID:       [App Registration Tenant ID]       │
│  Application Secret: [Client Secret Value]              │
│  Endpoint:           Normal | GCC | GCC High | DoD      │
│  App Catalog ID:     [Teams App Catalog ID] (optional)  │
└─────────────────────────────────────────────────────────┘

Azure Resources Created:
  1. App Registration (Microsoft Entra ID)
     └── API Permissions (Microsoft Graph, Application type)
     └── Client Secret
  2. Azure Bot Resource
     └── Teams Channel enabled
     └── Installed in target teams (for channel messaging)
     └── Auto-installs in chats (when App Catalog ID configured)
```
