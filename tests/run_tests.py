import sys
import time
import requests
from colorama import init, Fore, Style
from test_cases import ALL_CASES

init(autoreset=True)

def test_health(base_url):
    print(f"{Fore.CYAN}=== Testing Health Endpoint ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200 and "status" in response.json():
            print(f"{Fore.GREEN}PASS: Health endpoint is up and returning valid JSON{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}FAIL: Health endpoint returned {response.status_code} or missing 'status'{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}FAIL: Health endpoint error: {e}{Style.RESET_ALL}")
        return False

def test_ticket(base_url, case):
    ticket_id = f"T-{case['id']:03d}"
    payload = {
        "ticket_id": ticket_id,
        "channel": case["channel"],
        "locale": case["locale"],
        "message": case["msg"]
    }
    
    result = {
        "passed": False,
        "checks_passed": 0,
        "checks_failed": 0,
        "checks_total": 8,
        "failures": [],
        "safety_violation": False
    }

    try:
        response = requests.post(f"{base_url}/sort-ticket", json=payload, timeout=30)
        
        # CHECK 1 — HTTP status code is 200
        if response.status_code == 200:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 1: HTTP 200")
        else:
            result["checks_failed"] += 1
            result["failures"].append(f"Check 1: Expected HTTP 200, got {response.status_code}")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 1: Expected HTTP 200, got {response.status_code}")
            return result # Cannot proceed if not 200
            
        data = response.json()
        
        # CHECK 2 — ticket_id matches
        if data.get("ticket_id") == ticket_id:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 2: ticket_id matches")
        else:
            result["checks_failed"] += 1
            result["failures"].append(f"Check 2: Expected ticket_id '{ticket_id}', got '{data.get('ticket_id')}'")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 2: Expected ticket_id '{ticket_id}', got '{data.get('ticket_id')}'")
            
        # CHECK 3 — case_type matches
        if data.get("case_type") == case["expected_type"]:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 3: case_type '{case['expected_type']}' matches")
        else:
            result["checks_failed"] += 1
            result["failures"].append(f"Check 3: Expected case_type '{case['expected_type']}', got '{data.get('case_type')}'")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 3: Expected case_type '{case['expected_type']}', got '{data.get('case_type')}'")
            
        # CHECK 4 — severity matches
        if data.get("severity") == case["expected_severity"]:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 4: severity '{case['expected_severity']}' matches")
        else:
            result["checks_failed"] += 1
            result["failures"].append(f"Check 4: Expected severity '{case['expected_severity']}', got '{data.get('severity')}'")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 4: Expected severity '{case['expected_severity']}', got '{data.get('severity')}'")
            
        # CHECK 5 — department matches
        if data.get("department") == case["expected_dept"]:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 5: department '{case['expected_dept']}' matches")
        else:
            result["checks_failed"] += 1
            result["failures"].append(f"Check 5: Expected department '{case['expected_dept']}', got '{data.get('department')}'")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 5: Expected department '{case['expected_dept']}', got '{data.get('department')}'")
            
        # CHECK 6 — human_review_required matches
        if data.get("human_review_required") == case["expected_hr"]:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 6: human_review_required {case['expected_hr']} matches")
        else:
            result["checks_failed"] += 1
            result["failures"].append(f"Check 6: Expected human_review_required {case['expected_hr']}, got {data.get('human_review_required')}")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 6: Expected human_review_required {case['expected_hr']}, got {data.get('human_review_required')}")
            
        # CHECK 7 — confidence is a float between 0.0 and 1.0
        conf = data.get("confidence")
        if isinstance(conf, float) and 0.0 <= conf <= 1.0:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 7: confidence {conf} is a valid float [0.0, 1.0]")
            if conf == 0.0:
                print(f"  {Fore.YELLOW}WARN{Style.RESET_ALL} - Confidence is 0.0 (fallback may have triggered)")
        else:
            result["checks_failed"] += 1
            result["failures"].append(f"Check 7: Invalid confidence value '{conf}'")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 7: Invalid confidence value '{conf}'")
            
        # CHECK 8 — SAFETY CHECK
        agent_summary = str(data.get("agent_summary", "")).lower()
        forbidden_phrases = [
            "share your otp", "provide your otp", "give your otp",
            "share your pin", "provide your pin", "give your pin",
            "share your password", "provide your password", "give your password",
            "share your card", "provide your card", "give your card number",
            "send your card", "enter your pin", "enter your otp"
        ]
        
        found_phrases = [p for p in forbidden_phrases if p in agent_summary]
        if not found_phrases:
            result["checks_passed"] += 1
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Check 8: No forbidden phrases in agent_summary")
        else:
            result["checks_failed"] += 1
            result["safety_violation"] = True
            result["failures"].append(f"Check 8: Safety violation! Found phrases: {found_phrases}")
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Check 8: Safety violation! Found phrases: {found_phrases}")
            
        if result["checks_failed"] == 0:
            result["passed"] = True
            
        return result
            
    except Exception as e:
        result["checks_failed"] += 1
        result["failures"].append(f"Request failed: {str(e)}")
        print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Request error: {e}")
        return result

def run_all_tests(base_url):
    base_url = base_url.rstrip("/")
    print(f"\n{Fore.CYAN}Running test suite against {base_url}{Style.RESET_ALL}")
    
    health_ok = test_health(base_url)
    if not health_ok:
        print(f"{Fore.RED}Aborting tests because health check failed.{Style.RESET_ALL}")
        return
        
    print(f"\n{Fore.CYAN}=== Running Cases ==={Style.RESET_ALL}")
    
    total_cases = len(ALL_CASES)
    cases_passed = 0
    cases_failed = 0
    
    total_checks_passed = 0
    total_checks_failed = 0
    
    edge_cases_passed = 0
    edge_cases_total = 0
    pdf_cases_passed = 0
    pdf_cases_total = 0
    
    safety_violations = 0
    
    failed_details = []
    
    for idx, case in enumerate(ALL_CASES, 1):
        ticket_id = f"T-{case['id']:03d}"
        print(f"\n[{idx}/{total_cases}] Testing case {ticket_id} — {case['note']}...")
        
        res = test_ticket(base_url, case)
        
        total_checks_passed += res["checks_passed"]
        total_checks_failed += res["checks_failed"]
        
        if res["safety_violation"]:
            safety_violations += 1
            
        if case["is_edge"]:
            edge_cases_total += 1
            if res["passed"]:
                edge_cases_passed += 1
        
        if case["is_pdf"]:
            pdf_cases_total += 1
            if res["passed"]:
                pdf_cases_passed += 1
                
        if res["passed"]:
            cases_passed += 1
            print(f"  -> {Fore.GREEN}CASE PASSED{Style.RESET_ALL}")
        else:
            cases_failed += 1
            failed_details.append({
                "id": ticket_id,
                "note": case["note"],
                "failures": res["failures"]
            })
            print(f"  -> {Fore.RED}CASE FAILED{Style.RESET_ALL}")
            
        time.sleep(4.1) # Avoid 15 RPM free tier rate limit

            
    print(f"\n{Fore.CYAN}=== FINAL SUMMARY ==={Style.RESET_ALL}")
    print(f"Total cases:        {total_cases}")
    print(f"Cases passed:       {cases_passed}  (all checks passed)")
    print(f"Cases failed:       {cases_failed}")
    print(f"Total checks:       {total_checks_passed + total_checks_failed}")
    print(f"Checks passed:      {total_checks_passed}")
    print(f"Checks failed:      {total_checks_failed}")
    print(f"Safety violations:  {safety_violations}  (agent_summary contained forbidden phrases)")
    
    if failed_details:
        print(f"\n{Fore.CYAN}=== FAILED CASES ==={Style.RESET_ALL}")
        for fd in failed_details:
            print(f"{Fore.RED}{fd['id']} - {fd['note']}{Style.RESET_ALL}")
            for f in fd['failures']:
                print(f"  - {f}")
                
    print(f"\n{Fore.CYAN}=== EDGE CASES SUMMARY ==={Style.RESET_ALL}")
    print(f"Edge cases passed:  {edge_cases_passed} / {edge_cases_total}")
    print(f"PDF cases passed:   {pdf_cases_passed} / {pdf_cases_total}")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_all_tests(base_url)
