import html
import random
import re

import requests
import streamlit as st

API = "http://localhost:8000"

st.set_page_config(page_title="Eco-Court AI", page_icon="⚖️", layout="wide")

# ---------------- Theme toggle ----------------
with st.sidebar:
    st.markdown("### Settings")
    dark = st.toggle("Dark mode", value=True, key="dark_mode")

if dark:
    T = dict(bg="#070b16", bg2="#0d1426", text="#e6eaf5", muted="#8f9bb8",
             card="rgba(255,255,255,0.045)", border="rgba(255,255,255,0.10)",
             a1="#3b82f6", a2="#14b8a6", orb=0.22, shadow="rgba(0,0,0,0.45)",
             nav="rgba(7,11,22,0.75)", field="#121a2e")
else:
    T = dict(bg="#f6f8fc", bg2="#eaf0fb", text="#0f1b3d", muted="#5a6785",
             card="rgba(255,255,255,0.85)", border="rgba(15,27,61,0.10)",
             a1="#2563eb", a2="#0d9488", orb=0.14, shadow="rgba(30,50,120,0.12)",
             nav="rgba(246,248,252,0.85)", field="#ffffff")

# ---------------- Soft floating particles ----------------
random.seed(7)
particles = "".join(
    f'<span class="p" style="left:{random.randint(0,100)}%;'
    f'width:{s}px;height:{s}px;'
    f'animation-duration:{random.randint(18,36)}s;'
    f'animation-delay:-{random.randint(0,30)}s"></span>'
    for s in [random.choice([2, 2, 3, 4]) for _ in range(22)]
)

# ---------------- CSS ----------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

:root {{
  --bg:{T['bg']}; --bg2:{T['bg2']}; --text:{T['text']}; --muted:{T['muted']};
  --card:{T['card']}; --border:{T['border']}; --a1:{T['a1']}; --a2:{T['a2']};
  --field:{T['field']};
  --body: 'Inter', 'Segoe UI', system-ui, sans-serif;
  --head: 'Plus Jakarta Sans', 'Inter', 'Segoe UI', sans-serif;
}}

/* ---- fonts (icons are left alone so arrows keep working) ---- */
.stApp, .stApp p, .stApp label, .stApp li, .stApp button, .stApp input,
.stApp textarea, .stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stMetricLabel"] p {{
  font-family: var(--body);
}}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, [data-testid="stMetricValue"] {{
  font-family: var(--head) !important; letter-spacing: -0.02em; font-weight: 700;
}}

/* ---- background ---- */
.stApp {{
  background: linear-gradient(135deg, var(--bg), var(--bg2), var(--bg));
  background-size: 300% 300%; animation: bgShift 30s ease infinite; color: var(--text);
}}
@keyframes bgShift {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] {{ background: var(--card); backdrop-filter: blur(16px); border-right:1px solid var(--border); }}
.block-container {{ position:relative; z-index:2; max-width:1080px; padding-top:1rem; }}

.stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] p {{ color: var(--text); }}
[data-testid="stCaptionContainer"] p {{ color: var(--muted) !important; }}

/* ---- ambient glow + particles ---- */
.orb {{ position:fixed; border-radius:50%; filter:blur(100px); opacity:{T['orb']}; z-index:0; pointer-events:none; }}
.o1 {{ width:460px;height:460px;background:var(--a1);top:-140px;left:-120px;animation:f1 24s ease-in-out infinite; }}
.o2 {{ width:400px;height:400px;background:var(--a2);bottom:-150px;right:-100px;animation:f2 28s ease-in-out infinite; }}
@keyframes f1 {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(120px,90px)}} }}
@keyframes f2 {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(-130px,-80px)}} }}
.p {{ position:fixed; bottom:-10px; border-radius:50%; background:var(--a1); opacity:0; z-index:1;
      pointer-events:none; animation-name:rise; animation-iteration-count:infinite; animation-timing-function:linear; }}
@keyframes rise {{ 0%{{transform:translateY(0);opacity:0}} 10%{{opacity:.55}} 90%{{opacity:.35}}
                   100%{{transform:translateY(-105vh) translateX(30px);opacity:0}} }}

/* ---- top navigation bar ---- */
.nav {{
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 22px; margin-bottom:2.2rem; border-radius:16px;
  background:{T['nav']}; border:1px solid var(--border); backdrop-filter:blur(16px);
  box-shadow:0 8px 28px {T['shadow']}; animation:fadeUp .6s ease both;
}}
.brand {{ display:flex; align-items:center; gap:12px; }}
.logo {{ width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center;
         font-size:20px; background:linear-gradient(135deg,var(--a1),var(--a2)); box-shadow:0 4px 14px var(--a1); }}
.brand-name {{ font-family:var(--head); font-weight:800; font-size:1.15rem; color:var(--text); line-height:1.1; }}
.brand-sub {{ font-size:.72rem; color:var(--muted); letter-spacing:.06em; text-transform:uppercase; }}
.nav-pill {{ font-size:.75rem; font-weight:600; padding:5px 14px; border-radius:999px;
             color:var(--a2); border:1px solid var(--a2); }}

/* ---- hero ---- */
.hero {{ text-align:center; padding:.5rem 0 2rem; animation:fadeUp .8s ease both; }}
.hero h1 {{ font-size:2.9rem; line-height:1.12; margin:0 0 .7rem; font-weight:800; }}
.hero h1 span {{ background:linear-gradient(90deg,var(--a1),var(--a2)); -webkit-background-clip:text;
                 background-clip:text; -webkit-text-fill-color:transparent; }}
.hero p {{ color:var(--muted) !important; font-size:1.08rem; max-width:640px; margin:0 auto 1.2rem; line-height:1.6; }}
.chips {{ display:flex; gap:10px; justify-content:center; flex-wrap:wrap; }}
.chip {{ font-size:.8rem; font-weight:500; padding:6px 14px; border-radius:999px; color:var(--muted);
         background:var(--card); border:1px solid var(--border); transition:all .25s ease; }}
.chip:hover {{ color:var(--text); border-color:var(--a1); transform:translateY(-2px); }}
@keyframes fadeUp {{ from{{opacity:0;transform:translateY(18px)}} to{{opacity:1;transform:translateY(0)}} }}

/* ---- section labels ---- */
.stApp h3 {{ font-size:1.25rem; margin-top:1.6rem; }}

/* ---- glass cards ---- */
[data-testid="stMetric"], [data-testid="stExpander"], [data-testid="stAlert"], .hit, .answer {{
  background:var(--card); border:1px solid var(--border); border-radius:14px;
  backdrop-filter:blur(14px); box-shadow:0 8px 26px {T['shadow']}; animation:fadeUp .6s ease both;
}}
[data-testid="stMetric"] {{ padding:16px 20px; transition:transform .25s ease, box-shadow .25s ease; }}
[data-testid="stMetric"]:hover {{ transform:translateY(-5px); box-shadow:0 14px 36px {T['shadow']}; }}
[data-testid="stMetricValue"] {{ color:var(--a1) !important; }}
.hit {{ padding:16px 20px; margin-bottom:14px; line-height:1.6; transition:transform .25s ease, border-color .25s ease; }}
.hit:hover {{ transform:translateY(-3px); border-color:var(--a1); }}
.hit .meta {{ color:var(--a2); font-weight:600; font-size:.82rem; margin-bottom:8px;
              text-transform:uppercase; letter-spacing:.05em; }}

/* ---- AI answer card ---- */
.answer {{ padding:20px 24px; margin:14px 0 8px; line-height:1.75; border-left:4px solid var(--a1); }}
.answer .label {{ color:var(--a1); font-weight:700; font-size:.78rem; margin-bottom:10px;
                  text-transform:uppercase; letter-spacing:.08em; }}
.disclaimer {{ color:var(--muted); font-size:.8rem; margin:4px 0 14px; }}

/* ---- buttons ---- */
.stButton > button {{
  background:linear-gradient(90deg,var(--a1),var(--a2)); color:#fff; border:0; border-radius:10px;
  padding:.6rem 1.5rem; font-weight:600; letter-spacing:.01em;
  transition:transform .2s ease, box-shadow .2s ease;
}}
.stButton > button:hover {{ transform:translateY(-2px); box-shadow:0 10px 24px {T['shadow']}, 0 0 0 3px var(--a1); color:#fff; }}

/* ---- file uploader ---- */
[data-testid="stFileUploaderDropzone"] {{ background:var(--card); border:2px dashed var(--border);
  border-radius:14px; backdrop-filter:blur(10px); transition:all .3s ease; }}
[data-testid="stFileUploaderDropzone"]:hover {{ border-color:var(--a1); box-shadow:0 0 24px {T['shadow']}; }}

/* ---- text inputs (fix for white boxes in dark mode) ---- */
[data-baseweb="textarea"], [data-baseweb="textarea"] > div,
[data-baseweb="input"], [data-baseweb="input"] > div,
[data-baseweb="base-input"] {{
  background: var(--field) !important;
  border-color: var(--border) !important;
  border-radius: 10px !important;
}}
textarea, input {{
  background: var(--field) !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  border-radius: 10px !important;
}}
textarea::placeholder, input::placeholder {{
  color: var(--muted) !important;
  -webkit-text-fill-color: var(--muted) !important;
  opacity: .8;
}}
[data-baseweb="textarea"]:focus-within, [data-baseweb="input"]:focus-within {{
  border-color: var(--a1) !important;
  box-shadow: 0 0 0 3px {T['shadow']} !important;
}}

/* ---- footer ---- */
.foot {{ text-align:center; color:var(--muted); font-size:.78rem; margin:3rem 0 1rem;
         padding-top:1.2rem; border-top:1px solid var(--border); }}
</style>

<div class="orb o1"></div><div class="orb o2"></div>
{particles}
""", unsafe_allow_html=True)

# ---------------- Navigation bar + hero ----------------
st.markdown("""
<div class="nav">
  <div class="brand">
    <div class="logo">⚖️</div>
    <div>
      <div class="brand-name">Eco-Court AI</div>
      <div class="brand-sub">Environmental Legal Intelligence</div>
    </div>
  </div>
  <div class="nav-pill">● MVP · v0.3</div>
</div>

<div class="hero">
  <h1>Legal research for environmental law,<br><span>source-grounded and searchable.</span></h1>
  <p>Upload court judgments, ask questions in plain language, and get answers traced back to the exact page.</p>
  <div class="chips">
    <div class="chip">PDF Extraction</div>
    <div class="chip">Semantic Search</div>
    <div class="chip">Grounded Q&amp;A</div>
    <div class="chip">Page Citations</div>
  </div>
</div>
""", unsafe_allow_html=True)


def render_text(text: str) -> str:
    """Escape HTML, keep **bold** and line breaks from the model's answer."""
    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    return safe.replace("\n", "<br>")


# ---------------- Upload ----------------
st.markdown("### Upload document")
uploaded = st.file_uploader("Environmental judgment (PDF)", type="pdf")

if uploaded and st.button("Process document"):
    with st.spinner("Extracting, chunking and embedding... (first run downloads the model)"):
        try:
            r = requests.post(
                f"{API}/upload-pdf/",
                files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
                timeout=600,
            )
        except requests.exceptions.ConnectionError:
            st.error("Backend not running. Start it with: py -m uvicorn backend.app:app --reload")
            st.stop()
    if r.status_code == 200:
        st.session_state["doc"] = r.json()
        st.session_state.pop("qa", None)
    else:
        st.error(r.json().get("detail", "Upload failed."))

# ---------------- Results ----------------
doc = st.session_state.get("doc")
if doc:
    st.success(f"Processed **{doc['filename']}**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pages", doc["num_pages"])
    c2.metric("Chunks", doc["num_chunks"])
    c3.metric("Document ID", doc["doc_id"])
    if doc["possibly_scanned"]:
        st.warning("Very little text found - this looks like a scanned PDF. OCR is a later milestone.")

    # ---------- Ask a question (Milestone 3) ----------
    st.markdown("### Ask a question")
    question = st.text_input(
        "Your question about this document",
        placeholder="e.g. What did the tribunal decide about the public hearing?",
        key="question_box",
    )
    if st.button("Ask") and question.strip():
        with st.spinner("Searching the document and writing an answer..."):
            try:
                resp = requests.post(
                    f"{API}/ask",
                    json={"question": question, "doc_id": doc["doc_id"]},
                    timeout=120,
                )
                if resp.status_code == 200:
                    st.session_state["qa"] = {"q": question, **resp.json()}
                else:
                    st.session_state.pop("qa", None)
                    st.error(resp.json().get("detail", "Something went wrong."))
            except requests.exceptions.ConnectionError:
                st.error("Backend not running. Start it with: py -m uvicorn backend.app:app --reload")

    qa = st.session_state.get("qa")
    if qa:
        if qa["grounded"]:
            st.markdown(
                f'<div class="answer"><div class="label">Answer</div>{render_text(qa["answer"])}</div>'
                '<div class="disclaimer">AI-generated from the retrieved passages below. '
                'Verify against the original document. Not legal advice.</div>',
                unsafe_allow_html=True,
            )
            st.markdown("**Supporting sources**")
            for s in qa["sources"]:
                st.markdown(
                    f'<div class="hit"><div class="meta">[{s["id"]}] {html.escape(s["filename"])} '
                    f'· Page {s["page"]} · relevance {s["score"]}</div>'
                    f'{html.escape(s["text"])}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.warning(qa["answer"])

    st.markdown("### Extracted text preview")
    st.text_area("First pages", doc["preview"], height=250, label_visibility="collapsed")

    with st.expander("Sample chunks (with page numbers)"):
        for c in doc["sample_chunks"]:
            st.markdown(f"**Chunk {c['chunk_index']} · page {c['page']}**")
            st.text(c["text"])

    st.markdown("### Semantic search")
    q = st.text_input("Search this document", placeholder="e.g. environmental clearance")
    if q:
        r = requests.get(f"{API}/search", params={"q": q, "k": 5, "doc_id": doc["doc_id"]})
        for hit in r.json()["results"]:
            st.markdown(
                f'<div class="hit"><div class="meta">Page {hit["page"]} · relevance {hit["score"]}</div>'
                f'{html.escape(hit["text"])}</div>',
                unsafe_allow_html=True,
            )

# ---------------- Footer ----------------
st.markdown(
    '<div class="foot">Eco-Court AI is an AI-assisted research tool, not legal advice. '
    'Always verify results against the original court documents.</div>',
    unsafe_allow_html=True,
)