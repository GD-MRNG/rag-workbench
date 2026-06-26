"""
Generate benchmark Q&A pairs for the RAG workbench.

Reads all knowledge base documents, then calls an LLM once per question category
to produce structured test questions. Output is written to data/tests.jsonl.

Usage:
    uv run python data/generate_tests.py
"""

import json
from pathlib import Path
from pydantic import BaseModel, Field
from litellm import completion
from tenacity import retry, wait_exponential
from dotenv import load_dotenv

load_dotenv(override=True)

MODEL = "gpt-4.1-nano"
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "knowledge-base"
OUTPUT_PATH = Path(__file__).parent / "tests.jsonl"

# Target counts per category — adjust to change benchmark size or balance
CATEGORY_COUNTS = {
    "direct_fact": 70,
    "temporal": 20,
    "spanning": 20,
    "comparative": 10,
    "numerical": 10,
    "relationship": 10,
    "holistic": 10,
}

CATEGORY_DEFINITIONS = {
    "direct_fact": (
        "A single isolated fact answerable from one sentence in one document. "
        "Examples: who founded the company, what is an employee's job title, "
        "what is a product's monthly price, where is the headquarters."
    ),
    "temporal": (
        "Involves a specific date, year, quarter, or time period. "
        "Examples: when was the company founded, when did a product launch, "
        "when does a contract expire, what year did an employee join."
    ),
    "comparative": (
        "Involves a percentage, rate of change, improvement, or metric that compares "
        "one thing against another. Examples: by what percentage did X improve, "
        "what is the conversion rate increase, what growth rate was achieved."
    ),
    "numerical": (
        "Involves a raw count or quantity. "
        "Examples: how many employees work at the company, how many states does a product cover, "
        "how many active policies does a client have, how many contracts does a product have."
    ),
    "relationship": (
        "Connects two named entities — a person to a product, a company to a product, "
        "an employee to a team or responsibility. "
        "Examples: which product does an employee work on, which product does a client use, "
        "who is the technical lead for a product."
    ),
    "spanning": (
        "Requires combining facts from at least two different documents or sections to answer. "
        "The answer cannot be found in any single sentence or paragraph. "
        "Examples: what product does the IIOTY award winner work on "
        "(requires linking the award winner to their role to their product), "
        "what is the monthly price of the product that employee X leads."
    ),
    "holistic": (
        "Requires aggregating or synthesising across many records to produce the answer. "
        "Examples: total contract value across all contracts for a product, "
        "how many products have more than 3 active contracts, "
        "which product has the highest combined contract value."
    ),
}

wait = wait_exponential(multiplier=1, min=10, max=120)


class TestQuestion(BaseModel):
    question: str = Field(description="The question to ask the RAG system")
    keywords: list[str] = Field(
        description="2-4 atomic facts from the answer: proper names, numbers, or key terms. Never prose phrases."
    )
    reference_answer: str = Field(
        description="The correct answer in 1-3 complete sentences, directly and specifically addressing the question"
    )
    category: str = Field(description="The question category")


class TestQuestions(BaseModel):
    questions: list[TestQuestion]


def load_knowledge_base() -> str:
    sections = []
    for folder in sorted(KNOWLEDGE_BASE_PATH.iterdir()):
        if not folder.is_dir():
            continue
        folder_lines = [f"\n{'=' * 60}", f"SECTION: {folder.name.upper()}", f"{'=' * 60}\n"]
        for md_file in sorted(folder.rglob("*.md")):
            folder_lines.append(f"--- FILE: {md_file.name} ---")
            folder_lines.append(md_file.read_text(encoding="utf-8"))
            folder_lines.append("")
        sections.append("\n".join(folder_lines))
    return "\n".join(sections)


@retry(wait=wait)
def generate_questions(kb_text: str, category: str, n: int) -> list[TestQuestion]:
    definition = CATEGORY_DEFINITIONS[category]

    system_prompt = f"""You are an expert knowledge base curator creating a benchmark evaluation set for a RAG (Retrieval-Augmented Generation) system.

You will be given the full contents of a company knowledge base. Your task is to generate high-quality test questions of a specific type that will be used to evaluate how well a RAG system retrieves and answers questions about this company.

KNOWLEDGE BASE:
{kb_text}

QUESTION CATEGORY: {category}
CATEGORY DEFINITION: {definition}

RULES FOR QUESTIONS:
- Questions must be answerable only by someone who has read the knowledge base — not from general knowledge
- Questions must be specific and unambiguous — there should be exactly one correct answer
- Questions must match the category definition precisely
- Do not generate generic questions; ground every question in specific facts from the knowledge base

RULES FOR KEYWORDS:
- Extract 2-4 atomic facts from the reference answer
- Keywords should be proper names, numbers, product names, dates, or key terms
- Keywords must appear verbatim (or near-verbatim) in any document that correctly answers the question
- Never use prose phrases as keywords — keep them short and specific
- Example: for "Maxine Thompson won the IIOTY award in 2023", keywords are ["Maxine", "Thompson", "IIOTY", "2023"]

RULES FOR REFERENCE ANSWERS:
- 1-3 complete sentences
- Directly and specifically answer the question
- Factually grounded in the knowledge base — do not infer or extrapolate
- Concise: no preamble, no caveats, just the answer

Generate exactly {n} questions of category '{category}'. Make them varied — cover different employees, products, contracts, and topics across the knowledge base. Do not repeat the same fact in multiple questions."""

    user_prompt = f"Generate {n} benchmark questions of category '{category}'. Ensure they are varied and cover different parts of the knowledge base."

    response = completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=TestQuestions,
    )

    result = TestQuestions.model_validate_json(response.choices[0].message.content)
    # Ensure category field is set correctly
    for q in result.questions:
        q.category = category
    return result.questions


def main():
    print("Loading knowledge base...")
    kb_text = load_knowledge_base()
    print(f"Knowledge base loaded: {len(kb_text):,} characters")

    all_questions = []

    for category, count in CATEGORY_COUNTS.items():
        print(f"Generating {count} '{category}' questions...", end=" ", flush=True)
        questions = generate_questions(kb_text, category, count)
        all_questions.extend(questions)
        print(f"done ({len(questions)} generated)")

    print(f"\nWriting {len(all_questions)} questions to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for q in all_questions:
            f.write(json.dumps(q.model_dump(), ensure_ascii=False) + "\n")

    print(f"Done. {OUTPUT_PATH} contains {len(all_questions)} entries.")

    # Print category summary
    from collections import Counter
    counts = Counter(q.category for q in all_questions)
    print("\nCategory breakdown:")
    for cat, n in counts.most_common():
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
