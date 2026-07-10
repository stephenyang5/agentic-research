"""
PubMed / Entrez access

- Given a query, return paper IDs
- Given paper IDs, return titles / abstracts / metadata
"""

from Bio import Entrez

import config
from models import Paper


def search_pubmed(query: str, max_returns: int | None = None) -> list[str]:
    """Search PubMed and return paper IDs (no titles or abstracts)."""
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")

    if not config.NCBI_EMAIL:
        raise ValueError("NCBI email is missing - set it in .env file.")

    Entrez.email = config.NCBI_EMAIL
    if config.NCBI_API_KEY:
        Entrez.api_key = config.NCBI_API_KEY

    max_returns = config.DEFAULT_MAX_RETURNS if max_returns is None else max_returns
    try:
        # pubmed selects pubmed database among many NCBI databases
        # term= is the search query. max_returns caps how many IDs we ask for.
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_returns)
        # read() parses the XML response into a Python dict.
        results = Entrez.read(handle)
        handle.close()
    except Exception as exc:
        raise RuntimeError(f"PubMed search failed: {exc}") from exc

    # IdList is always present on a successful esearch, but may be empty.
    id_list = results.get("IdList", [])
    return list(id_list)


def _join_abstract(abstract_text) -> str:
    """
    Normalize AbstractText into one string.
    """
    if abstract_text is None:
        return ""
    if isinstance(abstract_text, list):
        return " ".join(str(section) for section in abstract_text)
    return str(abstract_text)


def _extract_year(pub_date: dict) -> str:
    """Pull a year out of PubDate, which may only have MedlineDate."""
    if not pub_date:
        return ""
    if "Year" in pub_date:
        return str(pub_date["Year"])
    # some records only have MedlineDate for some reason
    medline_date = pub_date.get("MedlineDate", "")
    return str(medline_date)[:4] if medline_date else ""


def _extract_authors(article: dict) -> list[str] | None:
    """Return author names if present, else None."""
    author_list = article.get("AuthorList", [])
    if not author_list:
        return None

    names: list[str] = []
    for author in author_list:
        # CollectiveName covers group authors like WHO
        if "CollectiveName" in author:
            names.append(str(author["CollectiveName"]))
            continue
        last = author.get("LastName", "")
        initials = author.get("Initials", "")
        if last:
            names.append(f"{last} {initials}".strip())
    return names or None


def _parse_article(pubmed_article: dict) -> Paper:
    """Convert one PubmedArticle dict into Paper class."""
    citation = pubmed_article["MedlineCitation"]
    article = citation["Article"]
    journal_info = article.get("Journal", {})
    pub_date = journal_info.get("JournalIssue", {}).get("PubDate", {})

    pubmed_id = str(citation.get("PMID", ""))
    title = str(article.get("ArticleTitle", "")).strip() or "(No title)"
    journal = str(journal_info.get("Title", "")).strip() or "(No journal)"
    year = _extract_year(pub_date)

    abstract_block = article.get("Abstract", {})
    abstract = _join_abstract(abstract_block.get("AbstractText"))

    authors = _extract_authors(article)

    return Paper(
        pubmed_id=pubmed_id,
        title=title,
        journal=journal,
        year=year,
        abstract=abstract,
        authors=authors,
    )


def fetch_paper_details(pubmed_ids: list[str]) -> list[Paper]:
    """
    Fetch title, journal, year, abstract (and optional authors) for PMIDs.
    """

    if not pubmed_ids:
        raise ValueError("pubmed_ids must be a non-empty list")

    if not config.NCBI_EMAIL:
        raise ValueError("NCBI email is missing - set it in .env file.")

    Entrez.email = config.NCBI_EMAIL
    if config.NCBI_API_KEY:
        Entrez.api_key = config.NCBI_API_KEY


    # efetch accepts a comma-separated ID string for a batch fetch.
    id_string = ",".join(pubmed_ids)

    try:
        # rettype/retmode=xml gives structured records Entrez.read can parse.
        handle = Entrez.efetch(
            db="pubmed",
            id=id_string,
            rettype="abstract",
            retmode="xml",
        )
        records = Entrez.read(handle)
        handle.close()
    except Exception as exc:
        raise RuntimeError(f"PubMed fetch failed: {exc}") from exc

    # Successful XML responses usually nest articles under "PubmedArticle".
    articles = records.get("PubmedArticle", [])
    return [_parse_article(article) for article in articles]


if __name__ == "__main__":
    # basic test
    test_query = "Mental health and AI interactions"
    ids = search_pubmed(test_query, max_returns=2)
    print(f"query: {test_query}")
    print(f"found {len(ids)} IDs")

    if not ids:
        print("No papers found, nothing to fetch.")
    else:
        papers = fetch_paper_details(ids)
        print(f"fetched {len(papers)} papers:\n")
        for paper in papers:
            abstract_preview = paper.abstract
            print(f"\nPMID: {paper.pubmed_id}")
            print(f"Title: {paper.title}")
            print(f"Journal: {paper.journal} ({paper.year})")
            print(f"Abstract: {abstract_preview or '(No abstract)'}\n")
            print("=" * 100)
