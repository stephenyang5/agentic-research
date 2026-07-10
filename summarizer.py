"""
LLM summarization

- Given a title + abstract, what is a structured summary?"
"""

import ollama

import config

# Prompt engineering: ask for a fixed skeleton so 10 papers look comparable.
_SYSTEM_PROMPT = """You are a biomedical research assistant.
Summarize scientific papers using ONLY the title and abstract provided.
Do not invent methods, results, or citations that are not supported by the abstract.
If a section cannot be determined from the abstract, write "Not stated in abstract".
Keep each bullet to 1-3 sentences.
Do not include chain-of-thought or preamble — output only the structured summary.
"""

_USER_PROMPT_TEMPLATE = """Title: {title}

Abstract: {abstract}

Return exactly this structure:

- Objective: ...
- Methods: ...
- Findings: ...
- Limitations: ...
- Relevance: ...
"""


def summarize_paper(title: str, abstract: str) -> str:
    """
    Summarize one paper from its title and abstract via a local Ollama model.
    """

    title = (title or "").strip()
    abstract = (abstract or "").strip()

    if not title:
        raise ValueError("title is empty string")

    if not abstract:
        return (
            "(No abstract was available for this paper.)"
            "- Objective: Not stated in abstract\n"
            "- Methods: Not stated in abstract\n"
            "- Findings: Not stated in abstract\n"
            "- Limitations: Not stated in abstract\n"
            "- Relevance: Not stated in abstract\n"
        )

    user_prompt = _USER_PROMPT_TEMPLATE.format(title=title, abstract=abstract)

    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        response = client.chat(
            model=config.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            # Low temperature - less variability.
            options={"temperature": 0.2},
        )
    except Exception as exc:
        raise RuntimeError(
            f"Ollama summarization failed. No server connecti on {config.OLLAMA_MODEL}' is unavailable"
        ) from exc

    # ollama-python returns a ChatResponse; .message.content is the text.
    content = (response.message.content or "").strip()
    if not content:
        raise RuntimeError("Ollama returned an empty summary")

    return content


if __name__ == "__main__":
    # Basic test without any pubmed retrieved stuff summarizer should work on any title/abstract.
    sample_title = (
        "Scalable biomarkers of Parkinson's disease: insights from mobile EEG in Peru"
    )
    sample_abstract = (
        "Mobile electroencephalography (EEG) may offer a scalable, cost-effective "
        "way to capture neural signatures of Parkinson's disease. We recorded "
        "resting-state EEG in patients and controls and evaluated candidate "
        "spectral biomarkers. Results suggest that mobile EEG features can "
        "discriminate groups, though sample size and site effects limit generality."
    )

    print(f"Model: {config.OLLAMA_MODEL}")
    print(f"Host:  {config.OLLAMA_HOST}")
    print("=" * 100)
    print(summarize_paper(sample_title, sample_abstract))
