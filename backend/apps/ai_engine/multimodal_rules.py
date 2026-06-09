import re


def clean_ocr_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in keywords)


def detect_issue_type(text: str, file_type: str = "IMAGE") -> str:
    text = text.lower()

    if contains_any(text, ["blue screen", "bsod", "stop code", "your pc ran into a problem"]):
        return "Blue Screen / System Crash"

    if contains_any(text, ["password", "incorrect password", "account locked", "sign in", "login failed"]):
        return "Login / Password Issue"

    if contains_any(text, ["vpn", "network", "connection failed", "no internet", "dns", "proxy"]):
        return "VPN / Network Issue"

    if contains_any(text, ["outlook", "mail", "sync", "send/receive", "exchange"]):
        return "Outlook / Email Issue"

    if contains_any(text, ["teams", "microsoft teams", "camera", "microphone", "meeting"]):
        return "Microsoft Teams Issue"

    if contains_any(text, ["printer", "print", "paper jam", "offline", "toner"]):
        return "Printer Issue"

    if contains_any(text, ["disk full", "low disk", "storage", "not enough space"]):
        return "Storage / Disk Space Issue"

    if contains_any(text, ["battery", "plugged in", "charging", "charger", "power"]):
        return "Battery / Power Issue"

    if contains_any(text, ["update", "windows update", "installing updates", "failed to install"]):
        return "Windows Update Issue"

    if contains_any(text, ["error", "failed", "crashed", "not responding", "exception"]):
        return "Application Error"

    if file_type == "VIDEO":
        return "Video-Based System Issue"

    return "General Technical Issue"


def suggest_solution(issue_type: str, extracted_text: str = "") -> str:
    issue_type = issue_type.lower()
    extracted_text = extracted_text.lower()

    if "blue screen" in issue_type:
        return (
            "Ask the user to restart the laptop, note the stop code, disconnect external devices, "
            "and upload a clear screenshot. Escalate to IT endpoint support if the issue repeats."
        )

    if "login" in issue_type or "password" in issue_type:
        return (
            "Ask the user to verify credentials, try password reset, clear browser cache, "
            "and share the exact login error. Escalate if the account is locked."
        )

    if "vpn" in issue_type or "network" in issue_type:
        return (
            "Ask the user to check internet connectivity, restart VPN client, verify credentials, "
            "and retry. If the error continues, escalate to network support."
        )

    if "outlook" in issue_type or "email" in issue_type:
        return (
            "Ask the user to restart Outlook, check internet connection, verify account login, "
            "and clear Outlook cache if needed."
        )

    if "teams" in issue_type:
        return (
            "Ask the user to restart Teams, check camera/microphone permissions, clear Teams cache, "
            "and re-login."
        )

    if "printer" in issue_type:
        return (
            "Ask the user to check printer power, network connection, paper tray, and printer queue. "
            "Escalate if printer is offline or shows hardware error."
        )

    if "battery" in issue_type or "power" in issue_type:
        return (
            "Ask the user to connect the charger, check the power indicator, hold the power button "
            "for 15 seconds, and try another power socket."
        )

    if "update" in issue_type:
        return (
            "Ask the user to restart the system, check internet connection, retry Windows Update, "
            "and share the update error code if it fails again."
        )

    if "application" in issue_type:
        return (
            "Ask the user to restart the application, reboot the system, check for updates, "
            "and share the exact error message."
        )

    return (
        "Ask the user to provide more details, device information, and a clearer screenshot/video "
        "if required. Start with basic restart and connectivity checks."
    )


def build_analysis_summary(
    file_type: str,
    issue_type: str,
    extracted_text: str,
    frame_count: int = 0,
) -> str:
    extracted_text = clean_ocr_text(extracted_text)

    if extracted_text:
        visible_text = extracted_text[:700]
    else:
        visible_text = "No readable text was detected."

    solution = suggest_solution(issue_type, extracted_text)

    if file_type == "VIDEO":
        return (
            f"Video Analysis Summary\n"
            f"Issue Type: {issue_type}\n"
            f"Frames Analyzed: {frame_count}\n"
            f"Detected Text: {visible_text}\n"
            f"Suggested Action: {solution}"
        )

    return (
        f"Image Analysis Summary\n"
        f"Issue Type: {issue_type}\n"
        f"Detected Text: {visible_text}\n"
        f"Suggested Action: {solution}"
    )