"""Canonical CJP Command Line Interface."""

import argparse
import os
import sys

from cobol_migrate import Pipeline


def main():
    parser = argparse.ArgumentParser(
        prog="cjp",
        description="COBOL to Native Java Modernization Platform (CJP)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: run (full pipeline)
    run_parser = subparsers.add_parser("run", help="Execute complete modernization pipeline")
    run_parser.add_argument("--repo", "-r", required=True, help="Path to COBOL repository")
    run_parser.add_argument("--out", "-o", help="Target output directory")
    run_parser.add_argument("--config", "-c", help="Configuration file path")

    # Command: ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest and fingerprint COBOL source files")
    ingest_parser.add_argument("--repo", "-r", required=True, help="Path to COBOL repository")

    # Command: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze COBOL architecture and call graph")
    analyze_parser.add_argument("--repo", "-r", required=True, help="Path to COBOL repository")

    # Command: generate
    generate_parser = subparsers.add_parser("generate", help="Generate Native Java Spring Boot application")
    generate_parser.add_argument("--repo", "-r", required=True, help="Path to COBOL repository")
    generate_parser.add_argument("--out", "-o", help="Target output directory")

    # Command: verify
    verify_parser = subparsers.add_parser("verify", help="Run differential verification gates")
    verify_parser.add_argument("--repo", "-r", required=True, help="Path to COBOL repository")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    repo = os.path.abspath(args.repo)
    out = os.path.abspath(args.out) if getattr(args, "out", None) else None
    cfg = args.config if getattr(args, "config", None) else None

    pipeline = Pipeline(repo=repo, out=out, config_path=cfg)

    if args.command == "run":
        verdict = pipeline.run()
        print(f"Pipeline Execution Complete. Final Verdict: {verdict}")
        sys.exit(0 if verdict in ("MVP_CERTIFIED", "PROD_READY") else 1)
    elif args.command == "ingest":
        pipeline.run_until("ingest")
    elif args.command == "analyze":
        pipeline.run_until("analyze")
    elif args.command == "generate":
        pipeline.run_until("generate")
    elif args.command == "verify":
        pipeline.run_until("validate")


if __name__ == "__main__":
    main()
