#Requires -Version 5.1
<#
.SYNOPSIS
    Installs or updates the Baseball Addon packs into Minecraft Bedrock Edition.
.DESCRIPTION
    Copies Baseball_RP and Baseball_BP into the com.mojang packs directories.
    If a pack is already installed, it compares the version and updates in-place.
    Supports both the release and Preview editions of Minecraft.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Config ──────────────────────────────────────────────────────────────────

$ScriptRoot    = $PSScriptRoot
$RP_Source     = Join-Path $ScriptRoot 'Baseball_RP'
$BP_Source     = Join-Path $ScriptRoot 'Baseball_BP'

$RP_UUID       = '3038a3ba-3bf7-4049-9620-3d4fdbc702fd'
$BP_UUID       = '2f0a7fe1-4bdf-4190-979e-6fbb7ea95618'

$MCPackageName  = 'Microsoft.MinecraftUWP_8wekyb3d8bbwe'
$MCPreviewName  = 'Microsoft.MinecraftWindowsBeta_8wekyb3d8bbwe'
$MCRoamingShared = Join-Path $env:APPDATA 'Minecraft Bedrock\Users\Shared\games\com.mojang'

# ── Helpers ──────────────────────────────────────────────────────────────────

function Write-Step  { param($Msg) Write-Host "  > $Msg" -ForegroundColor Cyan }
function Write-Ok    { param($Msg) Write-Host "  [OK] $Msg" -ForegroundColor Green }
function Write-Warn  { param($Msg) Write-Host "  [!!] $Msg" -ForegroundColor Yellow }
function Write-Fail  { param($Msg) Write-Host "  [XX] $Msg" -ForegroundColor Red }

function Get-ComMojangPath {
    # New standalone Minecraft launcher (Roaming\Minecraft Bedrock\Users\Shared)
    if (Test-Path $MCRoamingShared) { return $MCRoamingShared }
    # Legacy: check if the roaming root com.mojang has pack directories (older launcher layout)
    $roamingRoot = Join-Path $env:APPDATA 'Minecraft Bedrock\games\com.mojang'
    if (Test-Path (Join-Path $roamingRoot 'resource_packs')) { return $roamingRoot }
    # Fallback: UWP Store package (original Bedrock for Windows)
    foreach ($pkg in @($MCPackageName, $MCPreviewName)) {
        $candidate = Join-Path $env:LOCALAPPDATA "Packages\$pkg\LocalState\games\com.mojang"
        if (Test-Path (Join-Path $candidate 'resource_packs')) { return $candidate }
    }
    return $null
}

function Get-PackVersion {
    param([string]$ManifestPath)
    $m = Get-Content $ManifestPath -Raw | ConvertFrom-Json
    return $m.header.version  # returns an array like [1, 3, 0]
}

function Compare-Version {
    param($A, $B)   # both are arrays [major, minor, patch]
    for ($i = 0; $i -lt 3; $i++) {
        if ($A[$i] -gt $B[$i]) { return  1 }
        if ($A[$i] -lt $B[$i]) { return -1 }
    }
    return 0
}

function Format-Version {
    param($V)
    return "$($V[0]).$($V[1]).$($V[2])"
}

function Find-InstalledPack {
    # Returns the installed pack folder path whose manifest header.uuid matches $UUID, or $null.
    param([string]$PacksDir, [string]$UUID)
    if (-not (Test-Path $PacksDir)) { return $null }
    foreach ($dir in Get-ChildItem $PacksDir -Directory) {
        $mf = Join-Path $dir.FullName 'manifest.json'
        if (-not (Test-Path $mf)) { continue }
        try {
            $data = Get-Content $mf -Raw | ConvertFrom-Json
            if ($data.header.uuid -eq $UUID) { return $dir.FullName }
        } catch { continue }
    }
    return $null
}

function Test-FolderContentMatches {
    # Returns $true only if both folders contain the same files (relative path + SHA256).
    param([string]$A, [string]$B)
    if (-not (Test-Path $A)) { return $false }
    if (-not (Test-Path $B)) { return $false }
    $aBase = (Resolve-Path $A).Path
    $bBase = (Resolve-Path $B).Path
    $aFiles = @(Get-ChildItem $aBase -Recurse -File)
    $bFiles = @(Get-ChildItem $bBase -Recurse -File)
    if ($aFiles.Count -ne $bFiles.Count) { return $false }
    $bMap = @{}
    foreach ($f in $bFiles) {
        $rel = $f.FullName.Substring($bBase.Length).TrimStart('\')
        $bMap[$rel] = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
    }
    foreach ($f in $aFiles) {
        $rel = $f.FullName.Substring($aBase.Length).TrimStart('\')
        if (-not $bMap.ContainsKey($rel)) { return $false }
        if ((Get-FileHash $f.FullName -Algorithm SHA256).Hash -ne $bMap[$rel]) { return $false }
    }
    return $true
}

function Copy-PackContent {
    # Mirror SourceDir into DestDir (full replace; DestDir keeps its own folder name).
    param([string]$SourceDir, [string]$DestDir)
    if (Test-Path $DestDir) { Remove-Item -Path $DestDir -Recurse -Force }
    Copy-Item -Path $SourceDir -Destination $DestDir -Recurse -Force
}

function Sync-Pack {
    param(
        [string]$Label,
        [string]$SourceDir,
        [string]$PacksDir,
        [string]$UUID
    )

    $srcManifest = Join-Path $SourceDir 'manifest.json'
    $srcVersion  = Get-PackVersion $srcManifest
    $srcVerStr   = Format-Version $srcVersion

    $installed = Find-InstalledPack -PacksDir $PacksDir -UUID $UUID

    if ($null -eq $installed) {
        # ── Fresh install ────────────────────────────────────────────────────
        $destName = Split-Path $SourceDir -Leaf
        $destDir  = Join-Path $PacksDir $destName

        # If a folder with the same name exists but different UUID, append _baseball
        if (Test-Path $destDir) { $destDir = $destDir + '_baseball' }

        Write-Step "Installing $Label v$srcVerStr → $destDir"
        Copy-Item -Path $SourceDir -Destination $destDir -Recurse -Force
        Write-Ok   "$Label installed successfully (v$srcVerStr)"
    } else {
        # ── Check for update ─────────────────────────────────────────────────
        $instManifest = Join-Path $installed 'manifest.json'
        $instVersion  = Get-PackVersion $instManifest
        $instVerStr   = Format-Version $instVersion

        $cmp = Compare-Version $srcVersion $instVersion

        if ($cmp -eq 0) {
            # Same version number: the content can still differ if files were edited
            # without a version bump. Compare contents and re-sync if needed.
            if (Test-FolderContentMatches $SourceDir $installed) {
                Write-Ok "$Label is already up to date (v$instVerStr) -- no changes made"
            } else {
                Write-Step "Re-syncing $Label v$instVerStr (same version, content changed)"
                Remove-Item -Path $installed -Recurse -Force
                Copy-Item -Path $SourceDir -Destination $installed -Recurse -Force
                Write-Ok   "$Label content re-synced (v$instVerStr)"
            }
            return
        }

        if ($cmp -lt 0) {
            Write-Warn "$Label installed v$instVerStr is NEWER than source v$srcVerStr -- skipping"
            return
        }

        # Source is newer → update
        Write-Step "Updating $Label v$instVerStr → v$srcVerStr"
        Write-Step "  Removing old files from $installed"
        Remove-Item -Path $installed -Recurse -Force
        Write-Step "  Copying new files"
        Copy-Item -Path $SourceDir -Destination $installed -Recurse -Force
        Write-Ok   "$Label updated successfully (v$instVerStr → v$srcVerStr)"
    }
}

# ── World-save updater ───────────────────────────────────────────────────────

function Get-EmbeddedPackFolder {
    # Find a pack folder embedded inside a world (<world>\<kind>\*) whose manifest
    # header.uuid matches $UUID. Returns the folder path, or $null.
    param([string]$EmbedRoot, [string]$UUID)
    if (-not (Test-Path $EmbedRoot)) { return $null }
    foreach ($d in Get-ChildItem $EmbedRoot -Directory) {
        $mf = Join-Path $d.FullName 'manifest.json'
        if (-not (Test-Path $mf)) { continue }
        try {
            $m = Get-Content $mf -Raw | ConvertFrom-Json
            if ($m.header.uuid -ieq $UUID) { return $d.FullName }
        } catch { continue }
    }
    return $null
}

function Update-WorldPacks {
    # For each world that uses the addon, refresh its embedded pack copy (the content
    # Minecraft actually loads) AND align the world_*_packs.json version reference.
    param(
        [string]$WorldsDir,
        [array]$PackSpecs   # objects: Kind, RefFile, UUID, Source, Version, VerStr
    )

    if (-not (Test-Path $WorldsDir)) {
        Write-Warn "minecraftWorlds not found at $WorldsDir -- skipping"
        return
    }

    $checked = 0
    $updated = 0

    foreach ($world in Get-ChildItem $WorldsDir -Directory) {
        $namePath = Join-Path $world.FullName 'levelname.txt'
        $label    = if (Test-Path $namePath) { (Get-Content $namePath -Raw -Encoding UTF8).Trim() } else { $world.Name }
        $usesAddon    = $false
        $worldChanged = $false

        foreach ($spec in $PackSpecs) {
            $refFile = Join-Path $world.FullName $spec.RefFile
            if (-not (Test-Path $refFile)) { continue }

            try {
                # @() keeps a single-entry array as an array through the JSON round-trip
                $refData    = @((Get-Content $refFile -Raw -Encoding UTF8 | ConvertFrom-Json))
                $references = @($refData | Where-Object { $_.pack_id -ieq $spec.UUID })
                if ($references.Count -eq 0) { continue }
                $usesAddon = $true

                # 1. Refresh the embedded pack content (this is what the world renders)
                $embRoot   = Join-Path $world.FullName $spec.Kind
                $embFolder = Get-EmbeddedPackFolder -EmbedRoot $embRoot -UUID $spec.UUID
                if ($embFolder) {
                    if (-not (Test-FolderContentMatches $spec.Source $embFolder)) {
                        Copy-PackContent -SourceDir $spec.Source -DestDir $embFolder
                        Write-Step "  '$label': refreshed embedded $($spec.Kind) -> v$($spec.VerStr)"
                        $worldChanged = $true
                    }
                }

                # 2. Align the version reference with the source version
                $dirty = $false
                foreach ($entry in $references) {
                    $oldStr = "$($entry.version[0]).$($entry.version[1]).$($entry.version[2])"
                    if ($oldStr -ne $spec.VerStr) {
                        $entry.version = $spec.Version
                        $dirty = $true
                        Write-Step "  '$label': $($spec.RefFile) ref $oldStr -> $($spec.VerStr)"
                    }
                }
                if ($dirty) {
                    $json = ConvertTo-Json -InputObject $refData -Depth 5
                    # UTF-8 without BOM so Minecraft parses it cleanly
                    [System.IO.File]::WriteAllText($refFile, $json, [System.Text.UTF8Encoding]::new($false))
                    $worldChanged = $true
                }
            } catch {
                Write-Warn "  '$label': could not update $($spec.RefFile): $_"
            }
        }

        if ($usesAddon) {
            $checked++
            if ($worldChanged) { $updated++ }
            else { Write-Ok "  '$label': already current" }
        }
    }

    Write-Ok "$checked world(s) use the addon; $updated updated"
}

# ── Main ──────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "======================================" -ForegroundColor White
Write-Host "  Baseball Addon Installer / Updater" -ForegroundColor White
Write-Host "======================================" -ForegroundColor White
Write-Host ""

# Validate source packs exist
foreach ($dir in @($RP_Source, $BP_Source)) {
    if (-not (Test-Path $dir)) {
        Write-Fail "Source directory not found: $dir"
        Write-Host "  Run this script from the same folder as Baseball_RP and Baseball_BP." -ForegroundColor Red
        exit 1
    }
}

# Find Minecraft
$comMojang = Get-ComMojangPath
if ($null -eq $comMojang) {
    Write-Fail "Minecraft Bedrock Edition not found."
    Write-Host "  Expected path: $env:LOCALAPPDATA\Packages\<MinecraftPackage>\LocalState\games\com.mojang" -ForegroundColor Red
    Write-Host "  Make sure Minecraft (or Minecraft Preview) is installed from the Microsoft Store." -ForegroundColor Red
    exit 1
}

Write-Step "Found Minecraft data at: $comMojang"
Write-Host ""

$rpDir = Join-Path $comMojang 'resource_packs'
$bpDir = Join-Path $comMojang 'behavior_packs'

# Ensure target directories exist
foreach ($d in @($rpDir, $bpDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

Sync-Pack -Label 'Baseball_RP (Resource Pack)' -SourceDir $RP_Source -PacksDir $rpDir -UUID $RP_UUID
Write-Host ""
Sync-Pack -Label 'Baseball_BP (Behavior Pack)' -SourceDir $BP_Source -PacksDir $bpDir -UUID $BP_UUID

# ── Update existing world saves ───────────────────────────────────────────────

Write-Host ""
Write-Host "-- Updating existing world saves ----------------------------------" -ForegroundColor White
Write-Host ""

$rpSrcVer = Get-PackVersion (Join-Path $RP_Source 'manifest.json')
$bpSrcVer = Get-PackVersion (Join-Path $BP_Source 'manifest.json')

$packSpecs = @(
    [pscustomobject]@{ Kind = 'resource_packs'; RefFile = 'world_resource_packs.json'; UUID = $RP_UUID; Source = $RP_Source; Version = $rpSrcVer; VerStr = (Format-Version $rpSrcVer) },
    [pscustomobject]@{ Kind = 'behavior_packs'; RefFile = 'world_behavior_packs.json'; UUID = $BP_UUID; Source = $BP_Source; Version = $bpSrcVer; VerStr = (Format-Version $bpSrcVer) }
)

# Collect every minecraftWorlds directory under all user profiles, including Shared
$mcUsersRoot = Join-Path $env:APPDATA 'Minecraft Bedrock\Users'
$worldsDirs  = @()
if (Test-Path $mcUsersRoot) {
    $worldsDirs = Get-ChildItem $mcUsersRoot -Directory |
        ForEach-Object { Join-Path $_.FullName 'games\com.mojang\minecraftWorlds' } |
        Where-Object    { Test-Path $_ }
}
# Fallback: the com.mojang that the packs were installed into (covers non-standard layouts)
$sharedWorlds = Join-Path $comMojang 'minecraftWorlds'
if ((Test-Path $sharedWorlds) -and ($worldsDirs -notcontains $sharedWorlds)) {
    $worldsDirs += $sharedWorlds
}

# Normalize to an array and drop any empty entries so the .Count check below is
# safe under Set-StrictMode (a null/scalar result would otherwise throw here).
$worldsDirs = @($worldsDirs | Where-Object { $_ })

if ($worldsDirs.Count -eq 0) {
    Write-Warn "No minecraftWorlds directories found -- skipping world updates"
} else {
    foreach ($wd in $worldsDirs) {
        Write-Step "Scanning $wd"
        Update-WorldPacks -WorldsDir $wd -PackSpecs $packSpecs
    }
}

# ── Build .mcaddon for iPad / iPhone (and other manual-install platforms) ─────

Write-Host ""
Write-Host "-- Building .mcaddon package ----------------------------------------" -ForegroundColor White
Write-Host ""

$mcaddonScript = Join-Path $ScriptRoot 'build_mcaddon.py'
if (Test-Path $mcaddonScript) {
    python $mcaddonScript
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "Baseball_Addon.mcaddon rebuilt"
    } else {
        Write-Warn "build_mcaddon.py failed (exit $LASTEXITCODE) -- .mcaddon may be stale"
    }
} else {
    Write-Warn "build_mcaddon.py not found -- skipping .mcaddon build"
}

Write-Host ""
Write-Host "Done." -ForegroundColor White
Write-Host ""
