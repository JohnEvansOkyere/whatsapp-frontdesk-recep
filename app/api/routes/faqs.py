"""FAQ endpoints. Businesses can add FAQs one-by-one or upload a doc (CSV/TXT) in bulk."""
import csv
import io
import re
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.db import FAQ
from app.services import faq_service
from sqlalchemy import select

router = APIRouter(tags=["faqs"])


class FAQCreate(BaseModel):
    question: str
    answer: str
    keywords: list[str] = []


class FAQItem(BaseModel):
    question: str
    answer: str
    keywords: list[str] = []


class FAQBulkCreate(BaseModel):
    faqs: list[FAQItem]


class FAQResponse(BaseModel):
    id: str
    question: str
    answer: str
    keywords: list[str]


def _parse_faq_txt(content: str) -> list[dict]:
    """Parse plain text with Q: / A: blocks. Optional K: for keywords."""
    faqs = []
    # Split by blocks that start with Q: (allow blank lines between)
    blocks = re.split(r"(?m)^\s*Q:\s*", content, flags=re.IGNORECASE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        question_parts: list[str] = []
        answer_parts: list[str] = []
        keywords: list[str] = []
        state = "question"
        for line in block.split("\n"):
            line_stripped = line.strip()
            if re.match(r"^A:\s*", line_stripped, re.IGNORECASE):
                state = "answer"
                answer_parts.append(re.sub(r"^A:\s*", "", line_stripped, flags=re.IGNORECASE).strip())
            elif re.match(r"^K:\s*", line_stripped, re.IGNORECASE):
                kw = re.sub(r"^K:\s*", "", line_stripped, flags=re.IGNORECASE).strip()
                if kw:
                    keywords.extend(k.strip() for k in re.split(r"[;,]", kw) if k.strip())
            elif state == "question":
                question_parts.append(line_stripped)
            elif state == "answer":
                answer_parts.append(line_stripped)
        question = " ".join(question_parts).strip()
        answer = "\n".join(answer_parts).strip()
        if question and answer:
            faqs.append({"question": question[:512], "answer": answer, "keywords": keywords})
    # Fallback: split by double newline, first line = question, rest = answer
    if not faqs and content.strip():
        for block in re.split(r"\n\s*\n+", content):
            lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
            if len(lines) >= 2:
                faqs.append({
                    "question": lines[0][:512],
                    "answer": "\n".join(lines[1:]),
                    "keywords": [],
                })
    return faqs


def _parse_faq_csv(content: str) -> list[dict]:
    """Parse CSV with columns question, answer, keywords (optional). Keywords column can be 'a;b;c' or 'a,b,c'."""
    reader = csv.DictReader(io.StringIO(content))
    faqs = []
    for row in reader:
        q = (row.get("question") or "").strip()
        a = (row.get("answer") or "").strip()
        if not q or not a:
            continue
        kw_str = (row.get("keywords") or "").strip()
        if kw_str:
            keywords = [k.strip() for k in re.split(r"[;,]", kw_str) if k.strip()]
        else:
            keywords = []
        faqs.append({"question": q[:512], "answer": a, "keywords": keywords})
    return faqs


@router.post("/api/businesses/{business_id}/faqs", response_model=FAQResponse)
async def add_faq(
    business_id: UUID,
    body: FAQCreate,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Add a single FAQ for the business."""
    created = await faq_service.add_faq(
        session,
        business_id=business_id,
        question=body.question,
        answer=body.answer,
        keywords=body.keywords or [],
    )
    return created


@router.get("/api/businesses/{business_id}/faqs", response_model=list[FAQResponse])
async def list_faqs(
    business_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    """List all FAQs for the business."""
    items = await faq_service.get_faqs_for_business(session, business_id)
    # Need to include id; get_faqs_for_business doesn't return id. Query directly for list response.
    result = await session.execute(
        select(FAQ).where(FAQ.business_id == business_id).order_by(FAQ.question)
    )
    faqs = result.scalars().all()
    return [
        {"id": str(f.id), "question": f.question, "answer": f.answer, "keywords": list(f.keywords) if f.keywords else []}
        for f in faqs
    ]


@router.delete("/api/faqs/{faq_id}")
async def delete_faq(
    faq_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Delete one FAQ by id."""
    deleted = await faq_service.delete_faq(session, faq_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": "FAQ deleted"}


@router.post("/api/businesses/{business_id}/faqs/import", response_model=list[FAQResponse])
async def import_faqs(
    business_id: UUID,
    session: AsyncSession = Depends(get_db),
    body: FAQBulkCreate | None = None,
    file: UploadFile | None = File(None),
) -> list[dict]:
    """
    Bulk import FAQs for the business.

    - **JSON**: send body `{"faqs": [{"question": "...", "answer": "...", "keywords": ["..."]}]}`.
    - **File**: upload a CSV (columns: question, answer, keywords) or a TXT with Q: / A: blocks.

    TXT format example:
    ```
    Q: What are your opening hours?
    A: We are open 9am to 9pm every day.
    K: hours, opening, time

    Q: Do you take reservations?
    A: Yes, you can book via this bot or call us.
    ```
    """
    items: list[dict] = []
    if body is not None and body.faqs:
        items = [{"question": f.question, "answer": f.answer, "keywords": getattr(f, "keywords", []) or []} for f in body.faqs]
    elif file and file.filename:
        raw = await file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 text or CSV")
        if file.filename.lower().endswith(".csv"):
            items = _parse_faq_csv(text)
        else:
            items = _parse_faq_txt(text)
    if not items:
        raise HTTPException(
            status_code=400,
            detail="Provide JSON body with 'faqs' array or upload a CSV/TXT file (Q: / A: blocks)",
        )
    created = await faq_service.add_faqs_bulk(session, business_id, items)
    return created
