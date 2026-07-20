#!/usr/bin/env python3
"""
main.py

Entry point for AIRS.

Usage:
    python main.py --entity "AAPL"
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description="AIRS - Autonomous Investment Research System")
    parser.add_argument("--entity", type=str, required=True, help="Entity to analyze")
    args = parser.parse_args()
    
    print(f"Analyzing: {args.entity}")
    # TODO: Implement full workflow
    return 0


if __name__ == "__main__":
    exit(main())
