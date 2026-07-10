"""
Pipeline entry point simply for orchestration
"""

import argparse
import sys

from pubmed import fetch_paper_details, search_pubmed
from summarizer import summarize_paper
from utils import display_results


def run_pipeline(question: str, max_returns: int) -> int:
    """
    Run retrieval pipeline end-to-end.
    """

    question = question.strip()
    if not question:
        print("Error: question must be a non-empty string.", file=sys.stderr)
        return 1

    print(f"Searching PubMed for: {question!r}")
    try:
        pubmed_ids = search_pubmed(question, max_returns=max_returns)
    except (ValueError, RuntimeError) as exc:
        print(f"Search failed: {exc}", file=sys.stderr)
        return 1

    if not pubmed_ids:
        print("No papers found for that question. Try a broader query.")
        return 0

    print(f"Found {len(pubmed_ids)} paper IDs. Fetching details...")
    try:
        papers = fetch_paper_details(pubmed_ids)
    except (ValueError, RuntimeError) as exc:
        print(f"Fetch failed: {exc}", file=sys.stderr)
        return 1

    if not papers:
        print("PubMed returned IDs but no article records. Nothing to summarize.")
        return 0

    print(f"Summarizing {len(papers)} papers")
    summaries: list[str] = []
    for index, paper in enumerate(papers, start=1):
        print(f"[{index}/{len(papers)}] {paper.title}")
        try:
            summary = summarize_paper(paper.title, paper.abstract)
        except (ValueError, RuntimeError) as exc:
            summary = f"(Summary failed: {exc})"
        summaries.append(summary)

    display_results(question, papers, summaries)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Week 1 biomedical retrieval pipeline (PubMed -> LLM summaries).",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Biomedical research question. If omitted, you will be prompted.",
    )
    parser.add_argument(
        "--max-returns",
        type=int,
        default=10,
        help="Max PubMed papers to retrieve (default: 10). Use 2 for a quick test.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    question = args.question
    if not question:
        question = input("Enter a biomedical research question: ").strip()

    return run_pipeline(question, max_returns=args.max_returns)


if __name__ == "__main__":
    raise SystemExit(main())
