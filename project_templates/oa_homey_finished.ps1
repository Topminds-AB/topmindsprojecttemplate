#Requires -Version 5.1
<#
.SYNOPSIS
    Sends a text message to an Athom Homey webhook.

.DESCRIPTION
    This script sends a GET request to a Homey webhook endpoint so that
    a Homey Flow can catch the event and use the tag value as message data.

    The message text is automatically set to the name of the repository
    directory where this script is located.

.NOTES
    The webhook URL format used is:
    https://webhook.homey.app/<homey-id>/<event>?tag=<message>

    Create a Homey Flow with:
    Logic -> "Webhook event [Event] has been received"

    Then use the tag value inside the Flow to push a notification.

.EXAMPLE
    powershell.exe -ExecutionPolicy Bypass -File .\homey_finished.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$WarningPreference = 'SilentlyContinue'
$VerbosePreference = 'SilentlyContinue'
$InformationPreference = 'SilentlyContinue'
$ProgressPreference = 'SilentlyContinue'

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------

[string]$HomeyId = '65c3730767641fa181da9786'
[string]$EventName = 'pc_message'
[string]$SecretToken = 'PUT_YOUR_SECRET_HERE'
[bool]$UseSecretInTag = $false
[int]$TimeoutSeconds = 15

# -------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------

function Get-RepositoryName {
    <#
    .SYNOPSIS
        Gets the repository directory name for the current script.

    .DESCRIPTION
        Returns the leaf folder name of the directory where the current script
        is located. This value is used as the webhook message text.

    .PARAMETER ScriptRootPath
        The directory path where the script is located.

    .OUTPUTS
        System.String
        The repository directory name.
    #>
    param (
        [Parameter(Mandatory = $true)]
        [string]$ScriptRootPath
    )

    [string]$repositoryName = Split-Path -Path $ScriptRootPath -Leaf

    if ([string]::IsNullOrWhiteSpace($repositoryName)) {
        throw 'Could not determine the repository directory name from the script location.'
    }

    return $repositoryName
}

function Get-EncodedValue {
    <#
    .SYNOPSIS
        URL-encodes a string value.

    .DESCRIPTION
        Converts a plain text string into a URL-safe encoded value that can
        be included in a query string or path segment.

    .PARAMETER Value
        The plain text value to encode.

    .OUTPUTS
        System.String
        A URL-encoded string.
    #>
    param (
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    return [System.Uri]::EscapeDataString($Value)
}

function Get-WebhookUrl {
    <#
    .SYNOPSIS
        Builds the Homey webhook URL.

    .DESCRIPTION
        Creates the full webhook URL for Homey, including the event name and
        the tag payload that carries the message text.

    .PARAMETER HomeyIdentifier
        The Homey ID used in the webhook URL.

    .PARAMETER WebhookEventName
        The webhook event name that Homey Flow listens for.

    .PARAMETER TextMessage
        The text message to send to Homey.

    .PARAMETER Token
        A secret token that can optionally be appended to the tag payload.

    .PARAMETER IncludeSecretInTag
        Controls whether the secret token is included in the tag payload.

    .OUTPUTS
        System.String
        The full webhook URL.
    #>
    param (
        [Parameter(Mandatory = $true)]
        [string]$HomeyIdentifier,

        [Parameter(Mandatory = $true)]
        [string]$WebhookEventName,

        [Parameter(Mandatory = $true)]
        [string]$TextMessage,

        [Parameter(Mandatory = $true)]
        [string]$Token,

        [Parameter(Mandatory = $true)]
        [bool]$IncludeSecretInTag
    )

    [string]$tagPayload = $TextMessage

    if ($IncludeSecretInTag) {
        $tagPayload = "token=$Token|message=$TextMessage"
    }

    [string]$encodedEventName = Get-EncodedValue -Value $WebhookEventName
    [string]$encodedTagPayload = Get-EncodedValue -Value $tagPayload

    return "https://webhook.homey.app/$HomeyIdentifier/$($encodedEventName)?tag=$($encodedTagPayload)"
}

function Send-HomeyWebhook {
    <#
    .SYNOPSIS
        Sends the webhook request to Homey.

    .DESCRIPTION
        Performs an HTTP GET request against the generated Homey webhook URL.

    .PARAMETER Url
        The webhook URL to call.

    .PARAMETER RequestTimeoutSeconds
        Timeout in seconds for the HTTP request.

    .OUTPUTS
        System.Void
    #>
    param (
        [Parameter(Mandatory = $true)]
        [string]$Url,

        [Parameter(Mandatory = $true)]
        [int]$RequestTimeoutSeconds
    )

    $null = Invoke-WebRequest `
        -Uri $Url `
        -Method Get `
        -TimeoutSec $RequestTimeoutSeconds `
        -UseBasicParsing
}

# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

try {
    [string]$RepositoryName = Get-RepositoryName -ScriptRootPath $PSScriptRoot
    [string]$MessageText = "OA-Agenten har nu slutfört sitt arbete i repo $RepositoryName"

    if ([string]::IsNullOrWhiteSpace($HomeyId)) {
        throw 'HomeyId is empty.'
    }

    if ([string]::IsNullOrWhiteSpace($EventName)) {
        throw 'EventName is empty.'
    }

    if ([string]::IsNullOrWhiteSpace($MessageText)) {
        throw 'MessageText is empty.'
    }

    if ($UseSecretInTag -and [string]::IsNullOrWhiteSpace($SecretToken)) {
        throw 'SecretToken is empty while UseSecretInTag is enabled.'
    }

    [string]$webhookUrl = Get-WebhookUrl `
        -HomeyIdentifier $HomeyId `
        -WebhookEventName $EventName `
        -TextMessage $MessageText `
        -Token $SecretToken `
        -IncludeSecretInTag $UseSecretInTag

    Send-HomeyWebhook `
        -Url $webhookUrl `
        -RequestTimeoutSeconds $TimeoutSeconds

    exit 0
}
catch {
    exit 1
}