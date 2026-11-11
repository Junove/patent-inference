"""Per-section prompt templates (FR-G4). Guidance lines are written against the
linter's rules (app/linter/rules.yaml and engine.py) so a well-behaved answer
passes FR-G6 with no findings."""
from app.linter.engine import load_rules

SYSTEM = ("You are a patent attorney drafting one section of a utility patent application in "
          "precise, formal language. Reply with only the section body text: no heading, no markdown, "
          "no commentary.")

SECTION_GUIDANCE = {
    "Title": "A concise patent title for the invention, one line, at most 15 words.",
    "Abstract": "A single paragraph abstract summarizing the invention. Keep it under {abstract_max_words} words.",
    "Background": "Explain the problem the invention solves and the shortcomings of prior approaches.",
    "Summary": "A brief summary of the invention and its advantages over the background.",
    "Drawings Description": ('A short description of each implied figure, one line per figure starting '
                              '"FIG. n is ...". If no drawings are implied by the source material, say so.'),
    "Detailed Description": "A thorough technical description of the invention's structure and operation.",
    "Claims": ('Patent claims only, one claim per line, numbered consecutively starting at 1, each a single '
               'sentence ending with a period. A dependent claim may only reference an earlier claim number '
               '(for example "The device of claim 1"). Do not reference a claim number equal to or after its own.'),
}


def _guidance(section: str) -> str:
    return SECTION_GUIDANCE[section].format(abstract_max_words=load_rules().get("abstract_max_words", 150))


def build_messages(section: str, context_text: str, images: list[str], instructions: str,
                    prior_art: str = "") -> list[dict]:
    parts: list[str] = []
    if context_text:
        parts.append(f"Source material:\n{context_text}")
    if prior_art:
        parts.append(f"Related prior art found by patent search (for context, do not copy verbatim):\n{prior_art}")
    if instructions:
        parts.append(f"Additional instructions: {instructions}")
    parts.append(f'Write the "{section}" section. {_guidance(section)}')

    content: list[dict] = [{"type": "text", "text": "\n\n".join(parts)}]
    for url in images:
        content.append({"type": "image_url", "image_url": {"url": url}})
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": content}]
