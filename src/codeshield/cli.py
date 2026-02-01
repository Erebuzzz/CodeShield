"""
CLI entry point for CodeShield
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="CodeShield - The Complete AI Coding Safety Net"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--port", type=int, default=8080, help="Server port")
    serve_parser.add_argument("--host", default="localhost", help="Server host")

    # verify command
    verify_parser = subparsers.add_parser("verify", help="Verify code")
    verify_parser.add_argument("file", help="File to verify")

    # style command
    style_parser = subparsers.add_parser("style", help="Check code style against codebase")
    style_parser.add_argument("file", help="File to check")
    style_parser.add_argument("--codebase", default=".", help="Codebase path")

    args = parser.parse_args()

    if args.command == "serve":
        from codeshield.mcp.server import run_server
        run_server(host=args.host, port=args.port)
    elif args.command == "verify":
        from codeshield.trustgate.checker import verify_file
        result = verify_file(args.file)
        print(result)
    elif args.command == "style":
        from codeshield.styleforge.corrector import check_style
        result = check_style(args.file, args.codebase)
        print(result)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
