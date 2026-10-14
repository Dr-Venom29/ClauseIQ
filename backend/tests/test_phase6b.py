"""
ClauseIQ Phase 6B — Comprehensive Security & Isolation Test Suite
=================================================================
All external API calls (Gemini LLM + Google Embeddings) are mocked so the
suite runs fully offline and completes in seconds.

Tests:
  1. Ownership Enforcement     — Cross-user 403 on all analysis endpoints
  2. My Documents Isolation    — /documents/my returns only the caller's docs
  3. Chat / RAG Isolation      — FAISS search never leaks cross-user vectors
  4. FAISS Metadata Structure  — Every stored record has user_id, document_id, page
  5. Activity Logs             — All action types written with correct user_id
  6. Repository Audit          — DB ops (.query/.add/.commit/.delete) live
                                 only in repositories/, never in services/ or routes/
"""

import sys
import os
import io
import math
import pickle
import re
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ── Path & env setup — MUST come before any `app` import ───────────────────────
sys.path.insert(0, r"D:\P1\clauseiq\backend")

TEST_DB          = r"D:\P1\clauseiq\backend\test_phase6b.db"
TEST_FAISS_INDEX = r"D:\P1\clauseiq\backend\test_p6b_faiss.bin"
TEST_FAISS_META  = r"D:\P1\clauseiq\backend\test_p6b_faiss.pkl"

os.environ["DATABASE_URL"]                = f"sqlite:///{TEST_DB}"
os.environ["JWT_SECRET_KEY"]              = "testphase6bsecret_testphase6bsecret_42!"
os.environ["JWT_ALGORITHM"]               = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"


# ── Deterministic fake embeddings ──────────────────────────────────────────────
EMBEDDING_DIM = 768

def _fake_embedding(text: str = "") -> list:
    """Deterministic unit-norm vector so FAISS L2 works correctly."""
    import hashlib, random
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**31)
    rng  = random.Random(seed)
    vec  = [rng.gauss(0, 1) for _ in range(EMBEDDING_DIM)]
    norm = math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x / norm for x in vec]


# ── Fake AI responses ──────────────────────────────────────────────────────────
FAKE_SUMMARY_JSON = {
    "executive_summary": "Test NDA summary",
    "purpose": "Testing",
    "key_obligations": ["Maintain confidentiality"],
    "important_clauses": ["Termination clause: 12 months notice"],
    "penalties": ["None specified"],
    "exceptions": ["Public domain information"],
    "takeaways": ["Standard NDA terms apply"]
}
FAKE_RISK_JSON = {
    "high_risks": [],
    "medium_risks": [],
    "low_risks": [
        {"risk": "Low confidentiality exposure", "severity": "low",
         "reason": "Standard NDA terms", "citation": "Section 1"}
    ],
    "assumptions": ["Parties act in good faith"]
}
FAKE_CHECKLIST_JSON = [
    {"title": "Parties identified", "status": "present",
     "explanation": "Both parties are named.", "citation": "Section 1"},
    {"title": "Termination clause", "status": "present",
     "explanation": "12 months notice required.", "citation": "Section 5"}
]
FAKE_CHAT_TEXT = "The termination clause requires 12 months notice. [Citation 1]"


def _ai_json_router(prompt: str, user_id=None, model_name=None):
    """Route fake AI responses by distinctive keywords in each service's prompt."""
    p = prompt.lower()
    # risk_service prompt: "risk management ai" / "high, medium, and low risks"
    if "risk management" in p or "high_risks" in p or "low risks" in p:
        return FAKE_RISK_JSON
    # checklist_service prompt: "compliance officer" / "json array"
    if "compliance officer" in p or "json array" in p:
        return FAKE_CHECKLIST_JSON
    # clause_extraction: "extract clauses"
    if "extract" in p and "clause" in p:
        return []
    # Default: summary_service
    return FAKE_SUMMARY_JSON



# ── PDF generation ─────────────────────────────────────────────────────────────
def _make_pdf_bytes(text: str) -> bytes:
    """Create a proper PDF using reportlab (already installed)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(text, styles["Normal"])])
    return buf.getvalue()


def _cleanup(*paths):
    for p in paths:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


# ── Patch builder ──────────────────────────────────────────────────────────────
def _build_patches():
    """
    All patches that replace external network calls with fast stubs.
    We patch at the import locations inside the app modules.
    """
    # Mock embeddings object returned by GoogleGenerativeAIEmbeddings(...)
    mock_embeddings_instance = MagicMock()
    mock_embeddings_instance.aembed_query     = AsyncMock(side_effect=lambda t: _fake_embedding(t))
    mock_embeddings_instance.aembed_documents = AsyncMock(
        side_effect=lambda texts: [_fake_embedding(t) for t in texts]
    )

    # Mock AIService instance methods
    mock_ai_instance = MagicMock()
    mock_ai_instance.generate_json = AsyncMock(side_effect=_ai_json_router)
    mock_ai_instance.generate_text = AsyncMock(return_value=FAKE_CHAT_TEXT)

    return [
        # Patch the Embeddings class so every instantiation returns our mock
        patch(
            "app.services.embedding_service.GoogleGenerativeAIEmbeddings",
            return_value=mock_embeddings_instance
        ),
        # Patch genai.Client so AIService.__new__ doesn't fail on missing API key
        patch("app.services.ai_service.genai.Client", return_value=MagicMock()),
        # Patch the AIService class-level singleton so every AIService() call
        # returns our mock instance
        patch("app.services.llm_providers.gemini_provider.AIService", return_value=mock_ai_instance),
        patch("app.services.ai_service.AIService",        return_value=mock_ai_instance),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPhase6B(unittest.TestCase):

    _patches: list = []

    @classmethod
    def setUpClass(cls):
        _cleanup(TEST_DB, TEST_FAISS_INDEX, TEST_FAISS_META)

        # Reset FAISS singleton
        try:
            from app.vector_store.faiss import FAISSVectorStore
            if FAISSVectorStore._instance is not None:
                FAISSVectorStore._instance.index    = None
                FAISSVectorStore._instance.metadata = []
                FAISSVectorStore._instance._initialized = False
                FAISSVectorStore._instance = None
        except Exception:
            pass

        # Reset AIService and LLMRouter singletons
        try:
            import app.services.ai_service as _ai_mod
            _ai_mod.AIService._instance = None
        except Exception:
            pass
        try:
            import app.services.llm_router as _router_mod
            _router_mod._router_instance = None
        except Exception:
            pass

        # Start all patches before any app module is imported with real creds
        cls._patches = _build_patches()
        for p in cls._patches:
            p.start()

        # Now build the test client — all external deps already patched
        import app.db.session as _session_mod
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        _session_mod.engine.dispose()
        _session_mod.engine = create_engine(f"sqlite:///{TEST_DB}", connect_args={"check_same_thread": False})
        _session_mod.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_session_mod.engine)
        from app.models.document import Base
        Base.metadata.create_all(bind=_session_mod.engine)

        from fastapi.testclient import TestClient
        from app.main import app
        cls.client = TestClient(app)

        # Redirect FAISS singleton to test-specific files
        from app.vector_store.faiss import FAISSVectorStore
        vs = FAISSVectorStore()
        vs.index_path    = TEST_FAISS_INDEX
        vs.metadata_path = TEST_FAISS_META
        vs.index         = None
        vs.metadata      = []

        # ── Register users ─────────────────────────────────────────────────────
        res = cls.client.post("/api/v1/auth/register",
                              json={"email": "user_a_p6b@example.com", "password": "SecurePassA1!"})
        assert res.status_code == 201, f"Register A failed: {res.text}"
        cls.token_a   = res.json()["access_token"]
        cls.headers_a = {"Authorization": f"Bearer {cls.token_a}"}
        cls.user_a_id = cls.client.get("/api/v1/auth/me", headers=cls.headers_a).json()["id"]

        res = cls.client.post("/api/v1/auth/register",
                              json={"email": "user_b_p6b@example.com", "password": "SecurePassB1!"})
        assert res.status_code == 201, f"Register B failed: {res.text}"
        cls.token_b   = res.json()["access_token"]
        cls.headers_b = {"Authorization": f"Bearer {cls.token_b}"}
        cls.user_b_id = cls.client.get("/api/v1/auth/me", headers=cls.headers_b).json()["id"]

        # ── Upload documents ───────────────────────────────────────────────────
        nda_bytes = _make_pdf_bytes(
            "Mutual Non-Disclosure Agreement. The termination clause requires "
            "12 months written notice. Parties shall keep all information confidential."
        )
        msa_bytes = _make_pdf_bytes(
            "Master Services Agreement. Payment terms net-30. SLA 99.9% uptime."
        )
        emp_bytes = _make_pdf_bytes(
            "Employment Agreement. Notice period: 3 months. Non-compete: 1 year."
        )

        res = cls.client.post(
            "/api/v1/documents/upload",
            files={"file": ("nda.pdf", io.BytesIO(nda_bytes), "application/pdf")},
            headers=cls.headers_a
        )
        assert res.status_code == 200, f"A upload nda failed: {res.text}"
        cls.doc_nda_id = res.json()["id"]

        res = cls.client.post(
            "/api/v1/documents/upload",
            files={"file": ("msa.pdf", io.BytesIO(msa_bytes), "application/pdf")},
            headers=cls.headers_a
        )
        assert res.status_code == 200, f"A upload msa failed: {res.text}"
        cls.doc_msa_id = res.json()["id"]

        res = cls.client.post(
            "/api/v1/documents/upload",
            files={"file": ("employment.pdf", io.BytesIO(emp_bytes), "application/pdf")},
            headers=cls.headers_b
        )
        assert res.status_code == 200, f"B upload employment failed: {res.text}"
        cls.doc_emp_id = res.json()["id"]

        print("\nSetup complete")
        print("  User A: %s...   User B: %s..." % (cls.user_a_id[:8], cls.user_b_id[:8]))
        print("  NDA: %s  MSA: %s  EMP: %s" % (cls.doc_nda_id[:8], cls.doc_msa_id[:8], cls.doc_emp_id[:8]))

    @classmethod
    def tearDownClass(cls):
        for p in cls._patches:
            try:
                p.stop()
            except Exception:
                pass
        try:
            import app.db.session as _session_mod
            _session_mod.engine.dispose()
        except Exception:
            pass
        try:
            import app.services.llm_router as _router_mod
            _router_mod._router_instance = None
        except Exception:
            pass
        _cleanup(TEST_DB, TEST_FAISS_INDEX, TEST_FAISS_META)


    # ══════════════════════════════════════════════════════════════════════════
    #  TEST 1 — Ownership Enforcement
    # ══════════════════════════════════════════════════════════════════════════
    def test_01_ownership_enforcement(self):
        """
        User B must receive 403 or 404 on EVERY endpoint that touches User A's NDA.
        A 200 response is a security failure.
        """
        doc_id = self.doc_nda_id
        endpoints = [
            f"/api/v1/documents/{doc_id}",
            f"/api/v1/documents/{doc_id}/summary",
            f"/api/v1/documents/{doc_id}/risks",
            f"/api/v1/documents/{doc_id}/checklist",
            f"/api/v1/documents/{doc_id}/clauses",
        ]

        print("\n[TEST 1] Ownership Enforcement:")
        for url in endpoints:
            res = self.client.get(url, headers=self.headers_b)
            passed = res.status_code in (403, 404)
            icon   = "[PASS]" if passed else "[FAIL]"
            short  = url.split("/", 4)[-1]
            print("  %s GET %s -> HTTP %d" % (icon, short, res.status_code))
            self.assertIn(
                res.status_code, (403, 404),
                "\n  SECURITY FAIL - GET %s\n"
                "  Expected 403/404, got %d\n"
                "  Body: %s" % (url, res.status_code, res.text[:300])
            )

        print("  -> All cross-user requests correctly blocked.")


    # ══════════════════════════════════════════════════════════════════════════
    #  TEST 2 — My Documents Isolation
    # ══════════════════════════════════════════════════════════════════════════
    def test_02_my_documents_isolation(self):
        """
        GET /documents/my returns only the caller's documents.
        """
        # User A
        res_a = self.client.get("/api/v1/documents/my", headers=self.headers_a)
        self.assertEqual(res_a.status_code, 200, f"A /my failed: {res_a.text}")
        ids_a  = {d["id"] for d in res_a.json()}
        names_a = [d.get("filename", "?") for d in res_a.json()]

        self.assertIn(self.doc_nda_id, ids_a,    "nda.pdf missing from User A")
        self.assertIn(self.doc_msa_id, ids_a,    "msa.pdf missing from User A")
        self.assertNotIn(self.doc_emp_id, ids_a, "employment.pdf LEAKED into User A's list")

        # User B
        res_b = self.client.get("/api/v1/documents/my", headers=self.headers_b)
        self.assertEqual(res_b.status_code, 200, f"B /my failed: {res_b.text}")
        ids_b  = {d["id"] for d in res_b.json()}
        names_b = [d.get("filename", "?") for d in res_b.json()]

        self.assertIn(self.doc_emp_id, ids_b,    "employment.pdf missing from User B")
        self.assertNotIn(self.doc_nda_id, ids_b, "nda.pdf LEAKED into User B's list")
        self.assertNotIn(self.doc_msa_id, ids_b, "msa.pdf LEAKED into User B's list")

        print(
            "\n[TEST 2] [PASS] My Documents Isolation\n"
            "  User A sees %d doc(s): %s\n"
            "  User B sees %d doc(s): %s" % (len(ids_a), names_a, len(ids_b), names_b)
        )


    # ══════════════════════════════════════════════════════════════════════════
    #  TEST 3 — Chat / RAG Isolation
    # ══════════════════════════════════════════════════════════════════════════
    def test_03_chat_rag_isolation(self):
        """
        FAISS user_id filter must prevent User A's vectors from appearing in
        User B's search results.
        """
        query = "What is the termination clause?"

        res_a = self.client.post("/api/v1/search",
                                 json={"query": query, "top_k": 5},
                                 headers=self.headers_a)
        self.assertEqual(res_a.status_code, 200)
        results_a = res_a.json().get("results", [])

        res_b = self.client.post("/api/v1/search",
                                 json={"query": query, "top_k": 5},
                                 headers=self.headers_b)
        self.assertEqual(res_b.status_code, 200)
        results_b = res_b.json().get("results", [])

        # Core: no User A doc_ids in B's results
        leaked = [
            r for r in results_b
            if str(r.get("metadata", {}).get("document_id", "")) == str(self.doc_nda_id)
        ]
        self.assertEqual(
            len(leaked), 0,
            f"VECTOR LEAK — {len(leaked)} User A NDA vector(s) in User B's results:\n"
            + "\n".join(str(r.get("metadata", {})) for r in leaked)
        )

        print(
            "\n[TEST 3] [PASS] Chat / RAG Isolation\n"
            "  Query: '%s'\n"
            "  User A results: %d\n"
            "  User B results: %d (0 NDA leaks)" % (query, len(results_a), len(results_b))
        )


    # ══════════════════════════════════════════════════════════════════════════
    #  TEST 4 — FAISS Metadata Structure
    # ══════════════════════════════════════════════════════════════════════════
    def test_04_faiss_metadata_structure(self):
        """
        Every record in faiss_metadata.pkl must contain: user_id, document_id, page.
        """
        self.assertTrue(
            os.path.exists(TEST_FAISS_META),
            f"FAISS metadata file not found: {TEST_FAISS_META}\n"
            f"  Ensure at least one document was uploaded."
        )

        with open(TEST_FAISS_META, "rb") as f:
            metadata = pickle.load(f)

        self.assertIsInstance(metadata, list, "Metadata must be a list")
        self.assertGreater(len(metadata), 0,  "Metadata is empty — no embeddings stored")

        missing_uid = [i for i, r in enumerate(metadata) if not r.get("user_id")]
        missing_did = [i for i, r in enumerate(metadata) if not r.get("document_id")]
        missing_pg  = [i for i, r in enumerate(metadata) if "page" not in r]

        issues = []
        if missing_uid:
            issues.append(f"  {len(missing_uid)} record(s) missing 'user_id'    (indices: {missing_uid[:5]})")
        if missing_did:
            issues.append(f"  {len(missing_did)} record(s) missing 'document_id' (indices: {missing_did[:5]})")
        if missing_pg:
            issues.append(f"  {len(missing_pg)} record(s) missing 'page'        (indices: {missing_pg[:5]})")

        self.assertFalse(
            issues,
            "\n[TEST 4] [FAIL] FAISS metadata structure violations:\n" + "\n".join(issues)
        )

        s = metadata[0]
        print(
            "\n[TEST 4] [PASS] FAISS Metadata Structure\n"
            "  Total vectors   : %d\n"
            "  Record keys     : %s\n"
            "  Sample user_id  : %s\n"
            "  Sample doc_id   : %s\n"
            "  Sample page     : %s" % (
                len(metadata),
                sorted(s.keys()),
                str(s.get('user_id', 'MISSING'))[:36],
                str(s.get('document_id', 'MISSING'))[:36],
                s.get('page', 'MISSING'),
            )
        )


    # ══════════════════════════════════════════════════════════════════════════
    #  TEST 5 — Activity Logs
    # ══════════════════════════════════════════════════════════════════════════
    def test_05_activity_logs(self):
        """
        After triggering upload + summary + risk + checklist + chat for User A,
        activity_logs must contain all five action types with correct user_id.
        """
        doc_id = self.doc_nda_id

        # Trigger all action types
        self.client.get(f"/api/v1/documents/{doc_id}/summary",   headers=self.headers_a)
        self.client.get(f"/api/v1/documents/{doc_id}/risks",     headers=self.headers_a)
        self.client.get(f"/api/v1/documents/{doc_id}/checklist", headers=self.headers_a)
        self.client.post(
            "/api/v1/chat",
            json={"query": "What is the termination clause?", "document_id": doc_id},
            headers=self.headers_a
        )

        from app.db.session import SessionLocal
        from app.models.activity_log import ActivityLog

        db = SessionLocal()
        try:
            logs_a   = db.query(ActivityLog).filter(ActivityLog.user_id == self.user_a_id).all()
            actions  = {log.action for log in logs_a}
            required = {"upload", "summary", "risk_analysis", "checklist", "chat"}
            missing  = required - actions

            self.assertFalse(
                missing,
                f"\n  Missing log actions: {missing}\n"
                f"  Actions found: {sorted(actions)}"
            )

            for log in logs_a:
                self.assertEqual(
                    str(log.user_id), str(self.user_a_id),
                    f"Log entry {log.id} has wrong user_id: {log.user_id}"
                )

            print(
                "\n[TEST 5] [PASS] Activity Logs\n"
                "  User A total entries : %d\n"
                "  Actions logged       : %s" % (len(logs_a), sorted(actions))
            )
        finally:
            db.close()


    # ══════════════════════════════════════════════════════════════════════════
    #  TEST 6 — Repository Audit (static analysis)
    # ══════════════════════════════════════════════════════════════════════════
    def test_06_repository_audit(self):
        """
        Raw SQLAlchemy operations must ONLY live inside app/repositories/.
        Any .query/.add/.commit/.delete/.flush/.refresh in services/ or routes/
        is a repository-pattern violation.
        """
        backend_root = Path(r"D:\P1\clauseiq\backend\app")

        DB_OPS = re.compile(
            r"(?:self\.db|(?<!\w)db)\s*\.\s*"
            r"(?:query|add|delete|flush|commit|refresh|execute)\s*\(",
            re.VERBOSE,
        )

        REPO_DIR  = backend_root / "repositories"
        SVC_DIR   = backend_root / "services"
        ROUTE_DIR = backend_root / "api" / "routes"

        violations: list[str] = []

        def scan(directory: Path, label: str, allow: bool):
            for py in sorted(directory.rglob("*.py")):
                if "__pycache__" in py.parts:
                    continue
                try:
                    src = py.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for lineno, line in enumerate(src.splitlines(), 1):
                    if line.lstrip().startswith("#"):
                        continue
                    if DB_OPS.search(line) and not allow:
                        rel = py.relative_to(backend_root.parent)
                        violations.append(f"  [{label}] {rel}:{lineno}  →  {line.strip()}")

        scan(REPO_DIR,  "REPO",    allow=True)
        scan(SVC_DIR,   "SERVICE", allow=False)
        scan(ROUTE_DIR, "ROUTE",   allow=False)

        svc_files   = sum(1 for _ in SVC_DIR.rglob("*.py") if "__pycache__" not in str(_))
        route_files = sum(1 for _ in ROUTE_DIR.rglob("*.py") if "__pycache__" not in str(_))

        if violations:
            self.fail(
                f"\n[TEST 6] [FAIL] {len(violations)} repository-pattern violation(s):\n"
                + "\n".join(violations)
                + "\n\n  DB operations must only live inside app/repositories/**"
            )

        print(
            "\n[TEST 6] [PASS] Repository Audit - Clean\n"
            "  Scanned %d service file(s)   - 0 violations\n"
            "  Scanned %d route file(s)     - 0 violations\n"
            "  All DB ops correctly isolated in repositories/" % (svc_files, route_files)
        )


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    unittest.main(verbosity=2)
