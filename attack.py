import os
from static_prompts import STATIC_PROMPTS
import requests
from analysis import response_analysis


def get_dynamic_prompt(content):
    try:
        response = requests.post("http://localhost:8000/generate", json={"content": content})
        if response.status_code == 200:
            payload = response.json().get("prompt", "")
            return payload
        else:
            print("❌ Error from prompt server: ", response.status_code)
            exit()
    except Exception as e:
        print(f"❌ Failed to connect to prompt server: {e}")
        exit()



def handle_static_injection(url, headers, data, method, outfile=None):
    headers_dict = {h.split(":")[0].strip(): h.split(":")[1].strip() for h in headers} if headers else {}

    if outfile:
        log_dir = "log"
        os.makedirs(log_dir, exist_ok=True)
        outfile_path = os.path.join(log_dir, outfile)

    payloads = STATIC_PROMPTS

    for payload in payloads:
        if not payload:
            print("⚠️ Skipping empty or invalid static payload.")
            continue

        print(f"🔹 Testing Static Payload: {payload}")

        # Handle GET method
        if method == "http-get":
            if "PRMT" in url:
                injected_url = url.replace("PRMT", payload)
                print(f"🔹 GET Request Sent: {injected_url}")
                response = requests.get(injected_url, headers=headers_dict)
            else:
                print("⚠️ No 'PRMT' placeholder found in the URL.")
                return

        # Handle POST method
        elif method == "http-post":
            if data and "PRMT" in data:
                injected_data = data.replace("PRMT", payload)
                print(f"🔹 Injected Static Data: {injected_data}")

                if "Content-Type" in headers_dict and headers_dict["Content-Type"] == "application/json":
                    response = requests.post(url, headers=headers_dict, json={"prompt": injected_data})
                else:
                    response = requests.post(url, headers=headers_dict, data={"prompt": injected_data})

                print(f"🔹 POST Request Sent to {url} with injected static data: {injected_data}")
            else:
                print("⚠️ No 'PRMT' placeholder found in POST data.")
                return

        else:
            print("❌ Invalid HTTP method. Use 'http-get' or 'http-post'.")
            return

        print(f"🟢 Response ({response.status_code}): {response.text}...\n")
        analysis_result = response_analysis(response.text)

        print("🔍 Response Analysis:")
        for key, value in analysis_result.items():
            print(f"  {key}: {value}")

        if outfile:
            with open(outfile_path, "a") as f:
                f.write(f"\n[Payload]: {payload}\n")
                f.write(f"[Request URL]: {url}\n")
                f.write(f"[Request Data]: {data}\n")
                f.write(f"[Response Code]: {response.status_code}\n")
                f.write(f"[Response Text]: {response.text}\n")
                f.write("[Analysis]:\n")
                for key, value in analysis_result.items():
                    f.write(f"  {key}: {value}\n")
                f.write("-" * 50 + "\n")


def handle_dynamic_injection(url, headers, data, method, outfile=None):
    headers_dict = {h.split(":")[0].strip(): h.split(":")[1].strip() for h in headers} if headers else {}

    if outfile:
        log_dir = "log"
        os.makedirs(log_dir, exist_ok=True)
        outfile_path = os.path.join(log_dir, outfile)

    user_input = input("📝 Enter the injection goal: ").strip()

    while True:
        for i in range(5):
            print(f"\n🚀 Generating dynamic payload {i+1}/5...")
            payload = get_dynamic_prompt(user_input)

            if not payload:
                print("❌ No payload received from prompt generator.")
                continue

            print(f"🔹 Testing Dynamic Payload: {payload}")

            # Handle GET method
            if method == "http-get":
                if "PRMT" in url:
                    injected_url = url.replace("PRMT", payload)
                    print(f"🔹 GET Request Sent: {injected_url}")
                    response = requests.get(injected_url, headers=headers_dict)
                else:
                    print("⚠️ No 'PRMT' placeholder found in the URL.")
                    return

            # Handle POST method
            elif method == "http-post":
                if data and "PRMT" in data:
                    injected_data = data.replace("PRMT", payload)
                    print(f"🔹 Injected Dynamic Data: {injected_data}")

                    if "Content-Type" in headers_dict and headers_dict["Content-Type"] == "application/json":
                        response = requests.post(url, headers=headers_dict, json={"prompt": injected_data})
                    else:
                        response = requests.post(url, headers=headers_dict, data={"prompt": injected_data})

                    print(f"🔹 POST Request Sent to {url} with injected dynamic data: {injected_data}")
                else:
                    print("⚠️ No 'PRMT' placeholder found in POST data.")
                    return

            else:
                print("❌ Invalid HTTP method. Use 'http-get' or 'http-post'.")
                return

            print(f"🟢 Response ({response.status_code}): {response.text[:]}...\n")
            analysis_result = response_analysis(response.text)

            print("🔍 Response Analysis:")
            for key, value in analysis_result.items():
                print(f"  {key}: {value}")

            if analysis_result['suggested_action'] == 'escalate':
                print("⚠️ Escalate: Potential security issue detected.")
            elif analysis_result['suggested_action'] == 'obfuscate':
                print("⚠️ Obfuscate: Refusal or obfuscated response detected.")
            elif analysis_result['suggested_action'] == 'decode_and_continue':
                print("⚠️ Decode response and continue.")
            else:
                print("✅ Continue: No immediate issues detected.")

            if outfile:
                with open(outfile_path, "a") as f:
                    f.write(f"\n[Payload]: {payload}\n")
                    f.write(f"[Request URL]: {url}\n")
                    f.write(f"[Request Data]: {data}\n")
                    f.write(f"[Response Code]: {response.status_code}\n")
                    f.write(f"[Response Text]: {response.text}\n")
                    f.write("[Analysis]:\n")
                    for key, value in analysis_result.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("-" * 50 + "\n")

        # Ask if user wants to continue
        cont = input("🔁 Do you want to generate and test 5 more dynamic payloads? (y/n): ").strip().lower()
        if cont != 'y':
            print("👋 Exiting dynamic injection loop.")
            break

def inject(url, headers, data, method, mode, outfile=None):
    if mode == "static":
        handle_static_injection(url, headers, data, method, outfile)
    elif mode == "dynamic":
        handle_dynamic_injection(url, headers, data, method, outfile)
    else:
        print("❌ Invalid mode. Please choose either 'static' or 'dynamic'.")