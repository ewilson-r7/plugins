# Microsoft Entra ID Admin Plugin - Connection Setup

## Prerequisites

- An Azure subscription with Microsoft Entra ID (formerly Azure AD)
- Permissions to register applications and assign roles in your tenant

---

## Step 1: Register an Application

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** → **App registrations**
3. Click **New registration**
4. Enter a name for the application (e.g., "InsightConnect Entra ID Admin")
5. Leave the default supported account type (single tenant)
6. Click **Register**
7. Note down the **Application (client) ID** — you'll need this for the connection
8. Note down the **Directory (tenant) ID** from the Overview page

---

## Step 2: Create a Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "InsightConnect") and choose an expiration period
4. Click **Add**
5. **Copy the secret value immediately** — it won't be shown again. This is your Application Secret for the connection.

---

## Step 3: Assign API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Application permissions**
3. Add the following permissions:
   - `Directory.ReadWrite.All` (under Directory category)
   - `User.ReadWrite.All` (under User category)
   - `Device.ReadWrite.All` (under Device category)
   - `IdentityRiskEvent.Read.All` (under IdentityRiskEvent category — required for the Risk Detection trigger)
4. Click **Grant admin consent for [your tenant]** (requires Global Admin)
5. Verify all permissions show a green checkmark under "Status"

> **Note:** The plugin uses client credentials (app-only) authentication. You only need Application permissions, not Delegated permissions.

---

## Step 4: Assign a Directory Role (Required for User/Device Management)

The app needs a directory role to perform write operations on users and devices. Choose the least-privileged role that fits your use case:

| Role | Covers |
|------|--------|
| **User Administrator** | Disable/enable, create, delete non-admin users. Reset passwords for non-admins. |
| **Cloud Device Administrator** | Enable, disable, delete devices. |
| **Privileged Authentication Administrator** | All of User Administrator's capabilities plus can disable/enable admin accounts (except Global Admins). |
| **Global Administrator** | Required only if you need to disable/enable other Global Admin accounts. |

**Recommended minimum:** Assign **User Administrator** (for user operations) and **Cloud Device Administrator** (for device operations). Only escalate to Privileged Authentication Administrator or Global Administrator if you need to manage accounts that hold admin roles.

### To assign the role:

1. In the Azure Portal, navigate to **Microsoft Entra ID** → **Roles and administrators**
2. Search for and click the desired role (e.g., "User Administrator")
3. Click **Add assignments**
4. Search for your application name (from Step 1)
5. Select it and click **Add**
6. Repeat for any additional roles needed (e.g., Cloud Device Administrator)

> **Note:** If you don't see the option to add assignments directly, navigate to **Microsoft Entra ID** → **App registrations** → select your app → **Roles and Administrators**. Above the Roles table, click the "here" link that says the resource can only be assigned at directory level. This opens the All Roles view where you can find and assign the role.

---

## Step 5: Configure the Plugin Connection in InsightConnect

Use the following values from the steps above:

| Connection Field | Value |
|-----------------|-------|
| **Tenant ID** | Directory (tenant) ID from Step 1 |
| **Application ID** | Application (client) ID from Step 1 |
| **Application Secret** | Client secret value from Step 2 |

---

## Troubleshooting

- **401 Unauthorized** — Verify your Tenant ID, Application ID, and Application Secret are correct
- **403 Forbidden** — The app may be missing required permissions or admin consent hasn't been granted
- **403 when disabling/enabling a user** — The target user likely holds an admin role. Your app needs a higher-privileged role (e.g., Privileged Authentication Administrator to manage admins, or Global Administrator to manage other Global Admins)
- **Risk Detection trigger not working** — Ensure `IdentityRiskEvent.Read.All` is set as an Application permission (not Delegated)
- **Unable to manage devices** — Confirm the Cloud Device Administrator role is assigned to the application
