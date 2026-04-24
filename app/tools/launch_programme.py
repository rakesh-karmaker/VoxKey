import os
from pathlib import Path
import subprocess
import json
from fuzzywuzzy import process


def _is_unnecessary(name: str) -> bool:
    """Determine if a program is unnecessary based on its name."""
    unnecessary_keywords = [
        "uninstall",
        "install",
        "setup",
        "update",
        "help",
        "support",
        "readme",
        "manual",
        "config",
        "settings",
    ]
    return any(keyword in name.lower() for keyword in unnecessary_keywords)


def _get_uwp_apps() -> dict[str, dict]:
    """Get all installed UWP/Microsoft Store apps via PowerShell."""
    ps_command = """
    Get-AppxPackage | ForEach-Object {
        $manifest = $null
        $exePath  = $null
        $appId    = $null

        try {
            $manifestPath = Join-Path $_.InstallLocation "AppxManifest.xml"
            if (Test-Path $manifestPath) {
                [xml]$manifest = Get-Content $manifestPath -ErrorAction Stop
                $app = $manifest.Package.Applications.Application | Select-Object -First 1
                if ($app) {
                    $exePath = Join-Path $_.InstallLocation $app.Executable
                    $appId   = $app.Id
                }
            }
        } catch {}

        [PSCustomObject]@{
            Name            = $_.Name
            FullName        = $_.PackageFullName
            FamilyName      = $_.PackageFamilyName
            DisplayName     = if ($manifest) { try { $manifest.Package.Properties.DisplayName } catch { $_.Name } } else { $_.Name }
            InstallLocation = $_.InstallLocation
            ExePath         = if ($exePath -and (Test-Path $exePath)) { $exePath } else { "" }
            AppId           = if ($appId) { $appId } else { "App" }
        }
    } | ConvertTo-Json -Depth 2
    """

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"PowerShell error: {result.stderr}")
        return {}

    try:
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
    except json.JSONDecodeError:
        return {}

    skip_keywords = [
        "Microsoft.NET",
        "Microsoft.UI",
        "Microsoft.VCLibs",
        "Microsoft.DirectX",
        "Microsoft.Services",
        "Windows.CBSPreview",
        "Microsoft.WindowsAppRuntime",
        "Microsoft.Xbox.TCUI",
    ]

    programs = {}
    for app in data:
        full_name = app.get("FullName", "")
        if any(skip in full_name for skip in skip_keywords):
            continue

        display_name = app.get("DisplayName", "").strip()
        if display_name.startswith("ms-resource") or not display_name:
            display_name = app.get("Name", "").strip()

        if _is_unnecessary(display_name):
            continue

        programs[display_name] = {
            "exe": app.get("ExePath", "").strip() or None,
            "location": app.get("InstallLocation", "").strip(),
            "type": "UWP",
            "family_name": app.get(
                "FamilyName", ""
            ).strip(),  # ← needed for shell launch
            "app_id": app.get("AppId", "App").strip(),  # ← needed for shell launch
        }

    return programs


def _get_start_menu_programs() -> dict[str, dict]:
    """Get all programs from Start Menu (system-wide + current user)."""
    start_menu_paths = [
        Path(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"),
        Path(os.environ["APPDATA"]) / r"Microsoft\Windows\Start Menu\Programs",
    ]

    programs = {}
    for start_menu in start_menu_paths:
        if not start_menu.exists():
            continue
        for lnk_file in start_menu.rglob("*.lnk"):
            name = lnk_file.stem
            if not _is_unnecessary(name):
                programs[name] = {
                    "exe": None,
                    "location": str(lnk_file),  # .lnk works fine with os.startfile
                    "type": "Desktop",
                }

    return programs


def _get_programs(get_uwp_programs: bool) -> dict[str, dict]:
    """Get all programs, optionally including UWP apps. UWP apps are fetched separately to avoid long delays when loading the program list."""
    programs = {}

    if get_uwp_programs:
        for name, info in _get_uwp_apps().items():
            if name not in programs:
                programs[name] = info
    else:
        programs = _get_start_menu_programs()

    return programs


def _launch(info: dict) -> str:
    """Launch any program — Desktop (.lnk) or UWP."""
    if info["type"] == "Desktop":
        try:
            os.startfile(info["location"])
            return "--launched--"
        except Exception as _:
            return "--failed-to-launch--"

    elif info["type"] == "UWP":
        # 1. Try direct exe if available
        exe = info.get("exe")
        if exe and os.path.isfile(exe):
            subprocess.Popen([exe])
            return "--launched--"

        # 2. Launch via shell:AppsFolder using stored family_name + app_id
        family = info.get("family_name", "")
        app_id = info.get("app_id", "App")
        if family:
            try:
                os.startfile(f"shell:AppsFolder\\{family}!{app_id}")
                return "--launched--"
            except Exception:
                pass

        return "--failed-to-launch--"


def _search_programs(query: str, programs: dict, top_n=5) -> list[dict]:
    matches = process.extract(query, programs.keys(), limit=top_n)
    return [programs[match[0]] for match in matches if match[1] > 60]  # threshold of 60


def _find_and_launch(query: str, programs: dict) -> str:
    matches = _search_programs(query, programs)
    if not matches:
        uwp_programmes = _get_programs(get_uwp_programs=True)
        uwp_matches = _search_programs(query, uwp_programmes)
        if not uwp_matches:
            return "--no-match--"
        matches = uwp_matches

    info = matches[0]
    return _launch(info)


def launch_programme(query: str):
    programs = _get_programs(get_uwp_programs=False)
    tag = _find_and_launch(query, programs)
    match tag:
        case "--launched--":
            print("Program launched successfully.")
        case "--no-match--":
            print("No matching program found.")
        case "--failed-to-launch--":
            print("Failed to launch the program.")
