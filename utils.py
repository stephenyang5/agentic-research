"""
Shared helpers that are not PubMed-specific and not LLM-specific.

Week 1: pretty-printing for terminal.
"""

from models import Paper


def display_results(
    question: str,
    papers: list[Paper],
    summaries: list[str],
) -> None:
    """
    Print structured paper summaries in a readable terminal format.
    """

    print()
    print("=" * 64)
    print(f"Question: {question}")
    print(f"Papers summarized: {len(papers)}")
    print("=" * 64)

    for index, (paper, summary) in enumerate(zip(papers, summaries), start=1):
        print("\n" + "=" * 64)
        print(f"Paper {index}\n")
        print(f"Title: {paper.title}")
        print(f"Journal: {paper.journal}")
        print(f"Year: {paper.year}")
        print(f"PMID: {paper.pubmed_id}\n")
        print("Summary")
        print(summary)
        print("=" * 64)

    print()
