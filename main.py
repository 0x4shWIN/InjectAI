from banner import display_banner
import argparse 
import requests
import validators
from attack import inject

display_banner()

def validate_url(url):
    '''Validate the URL format'''
    return validators.url(url)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="InjectAI : Automated Prompt Injection")
    parser.add_argument("method", choices=["http-post", "http-get"], help="Specify HTTP method: 'http-post' or 'http-get'")
    parser.add_argument("-u", "--url", required=True, help="Chatbot API URL with 'PRMPT' as the injection point")
    parser.add_argument("-S", "--static", action="store_true", help="Static Prompt Injection with predefined jailbreak prompts")
    parser.add_argument("-D", "--dynamic", action="store_true", help="Dynamic Prompt Injection purely based on LLM")
    parser.add_argument("-H", "--header", nargs="*", help="URL headers")
    parser.add_argument("-d", "--data", help="Parameters/values being passed")
    parser.add_argument("-O", "--outfile", type=str, default="default_log.txt", help="Save logs to output file (default: default_log.txt)")
    args = parser.parse_args()

    if not validate_url(args.url):
        print("🔴 Invalid URL provided")
        exit(1)

    if args.static:
        print("🛠️ Running Static Prompt Injection...")
        inject(args.url, args.header, args.data, args.method, mode="static", outfile=args.outfile)

    elif args.dynamic:
        print("🤖 Running Dynamic Prompt Injection...")
        inject(args.url, args.header, args.data, args.method, mode="dynamic", outfile=args.outfile)
        
    else:
        print("⚠️ No injection mode selected. Use -S or -D. Exiting.")
        exit()
