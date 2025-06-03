import requests
import time
import json
import os # Import the os module to access environment variables
import warnings
warnings.filterwarnings("ignore")

# --- Configuration ---
BASE_URL = "https://api.pingera.ru"
EXECUTE_ENDPOINT = "/v1/checks/execute"
JOB_STATUS_ENDPOINT = "/v1/checks/jobs/{job_id}"

# --- Get API Token from Environment Variable ---
# It's highly recommended to set this environment variable before running the script.
# For example, on Linux/macOS: export PINGERA_API_TOKEN="YOUR_ACTUAL_TOKEN_HERE"
# On Windows (cmd): set PINGERA_API_TOKEN="YOUR_ACTUAL_TOKEN_HERE"
# On Windows (PowerShell): $env:PINGERA_API_TOKEN="YOUR_ACTUAL_TOKEN_HERE"
PINGERA_API_TOKEN = os.getenv("PINGERA_API_TOKEN")

if not PINGERA_API_TOKEN:
    print("Error: PINGERA_API_TOKEN environment variable is not set.")
    print("Please set it before running the script. Example:")
    print("  export PINGERA_API_TOKEN=\"YOUR_ACTUAL_TOKEN_HERE\"")
    exit(1) # Exit if the token is not found

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"{PINGERA_API_TOKEN}" # Add the Authorization header
}

POST_BODY = {
    "name": "Pingera web check",
    "type": "web",
    "url": "https://app.pingera.ru",
    "timeout": 10,
}

POLLING_INTERVAL_SECONDS = 3
MAX_POLLING_ATTEMPTS = 20

# --- Colors for pretty printing ---
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_MAGENTA = "\033[95m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_UNDERLINE = "\033[4m"

def print_colored(message, color):
    """Prints a message with the specified color."""
    print(f"{color}{message}{COLOR_RESET}")

def print_status_update(job_id, status, attempt_num):
    """Prints a formatted status update during polling."""
    status_colors = {
        "pending": COLOR_YELLOW,
        "running": COLOR_CYAN,
        "completed": COLOR_GREEN,
        "failed": COLOR_RED,
        "timeout": COLOR_RED,
        "cancelled": COLOR_MAGENTA,
    }
    color = status_colors.get(status, COLOR_BLUE)
    print_colored(f"  [{attempt_num}] Job ID: {COLOR_BOLD}{job_id}{COLOR_RESET}{color} - Status: {status.upper()}", color)

def main():
    print_colored(f"{COLOR_BOLD}{COLOR_BLUE}--- Pingera API Endpoint Demo ---{COLOR_RESET}", COLOR_BLUE)
    print_colored(f"Using API Token from environment variable: PINGERA_API_TOKEN", COLOR_BLUE)

    # 1. Send POST request to execute a check
    print_colored(f"\n{COLOR_BOLD}1. Sending POST request to execute check...{COLOR_RESET}", COLOR_CYAN)
    print_colored(f"   URL: {BASE_URL}{EXECUTE_ENDPOINT}", COLOR_CYAN)
    print_colored(f"   Body: {json.dumps(POST_BODY, indent=2)}", COLOR_CYAN)

    try:
        response = requests.post(f"{BASE_URL}{EXECUTE_ENDPOINT}", json=POST_BODY, headers=HEADERS)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        initial_response_data = response.json()

        print_colored(f"\n{COLOR_BOLD}--- Initial Response ---{COLOR_RESET}", COLOR_GREEN)
        print_colored(json.dumps(initial_response_data, indent=2), COLOR_GREEN)

        job_id = initial_response_data.get("job_id")
        if not job_id:
            print_colored(f"{COLOR_RED}Error: 'job_id' not found in the initial response.{COLOR_RESET}", COLOR_RED)
            return

        print_colored(f"\n{COLOR_BOLD}Extracted Job ID: {COLOR_UNDERLINE}{job_id}{COLOR_RESET}", COLOR_MAGENTA)

    except requests.exceptions.RequestException as e:
        print_colored(f"{COLOR_RED}Error sending POST request: {e}{COLOR_RESET}", COLOR_RED)
        if hasattr(e, 'response') and e.response is not None:
            print_colored(f"{COLOR_RED}Response Status Code: {e.response.status_code}{COLOR_RESET}", COLOR_RED)
            print_colored(f"{COLOR_RED}Response content: {e.response.text}{COLOR_RESET}", COLOR_RED)
        return

    # 2. Periodically probe job status
    print_colored(f"\n{COLOR_BOLD}2. Periodically probing job status for job ID: {job_id}{COLOR_RESET}", COLOR_CYAN)
    print_colored(f"   Polling every {POLLING_INTERVAL_SECONDS} seconds, max attempts: {MAX_POLLING_ATTEMPTS}", COLOR_CYAN)

    job_status = None
    attempts = 0
    while job_status != "completed" and attempts < MAX_POLLING_ATTEMPTS:
        attempts += 1
        probe_url = f"{BASE_URL}{JOB_STATUS_ENDPOINT.format(job_id=job_id)}"
        
        try:
            probe_response = requests.get(probe_url, headers=HEADERS)
            probe_response.raise_for_status()
            probe_data = probe_response.json()
            
            job_status = probe_data.get("status")
            print_status_update(job_id, job_status, attempts)

            if job_status == "completed":
                print_colored(f"\n{COLOR_BOLD}{COLOR_GREEN}--- Job Completed! Final Result ---{COLOR_RESET}", COLOR_GREEN)
                print_colored(json.dumps(probe_data, indent=2), COLOR_GREEN)
                
                check_result = probe_data.get("result")
                if check_result:
                    print_colored(f"\n{COLOR_BOLD}--- Key Check Result Details ---{COLOR_RESET}", COLOR_YELLOW)
                    print_colored(f"  Status: {check_result.get('status')}", COLOR_YELLOW)
                    print_colored(f"  Response Time: {check_result.get('response_time')} ms", COLOR_YELLOW)
                    metadata = check_result.get("check_metadata", {})
                    print_colored(f"  HTTP Status Code: {metadata.get('status_code')}", COLOR_YELLOW)
                break
            elif job_status in ["failed", "timeout", "cancelled"]:
                print_colored(f"\n{COLOR_BOLD}{COLOR_RED}--- Job {job_status.upper()}! ---{COLOR_RESET}", COLOR_RED)
                print_colored(json.dumps(probe_data, indent=2), COLOR_RED)
                break
            
            time.sleep(POLLING_INTERVAL_SECONDS)

        except requests.exceptions.RequestException as e:
            print_colored(f"{COLOR_RED}Error probing job status: {e}{COLOR_RED}", COLOR_RED)
            if hasattr(e, 'response') and e.response is not None:
                print_colored(f"{COLOR_RED}Response Status Code: {e.response.status_code}{COLOR_RED}", COLOR_RED)
                print_colored(f"{COLOR_RED}Response content: {e.response.text}{COLOR_RED}", COLOR_RED)
            break
        
    else:
        if job_status != "completed":
            print_colored(f"\n{COLOR_BOLD}{COLOR_RED}Max polling attempts reached. Job did not complete within the expected time.{COLOR_RESET}", COLOR_RED)
            if job_status:
                print_colored(f"{COLOR_RED}Last known status: {job_status}{COLOR_RESET}", COLOR_RED)

    print_colored(f"\n{COLOR_BOLD}{COLOR_BLUE}--- Demo Finished ---{COLOR_RESET}", COLOR_BLUE)

if __name__ == "__main__":
    main()
