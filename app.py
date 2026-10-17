import os
import io
import html
import base64

import streamlit as st
from PIL import Image
from search_engine import ImageSearchEngine

st.set_page_config(
    page_title="Lightbox · Image Search",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Design: a photographer's light table. Results are slides on a navy mat that
# "develop" (blur -> sharp) once, like a cyanotype print. Amber marks the best match.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Figtree:wght@400;500;600;700&display=swap');

:root {
  --paper: #F4F7FB;
  --sheet: #FFFFFF;
  --ink: #14213D;
  --muted: #5B6B86;
  --cyan: #1F4E9C;
  --rule: #D3DCEA;
  --amber: #E8A33D;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--paper) !important;
  color: var(--ink) !important;
  font-family: 'Figtree', system-ui, sans-serif !important;
}
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1180px; padding-top: 3.2rem !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--sheet) !important; border-right: 1px solid var(--rule) !important; }
[data-testid="stSidebar"] * { color: var(--ink) !important; font-family: 'Figtree', sans-serif !important; }
.side-fact { display:flex; justify-content:space-between; padding:.55rem 0; border-bottom:1px solid var(--rule); font-size:.88rem; }
.side-fact span:first-child { color: var(--muted) !important; }

/* Masthead */
.mast h1 {
  font-family: 'Instrument Serif', serif !important;
  font-weight: 400 !important;
  font-size: clamp(2.6rem, 6vw, 4.6rem) !important;
  line-height: 1.02 !important;
  letter-spacing: -0.015em;
  color: var(--ink) !important;
  margin: 0 0 .8rem !important;
  padding: 0 !important;
}
.mast p { color: var(--muted); font-size: 1.05rem; max-width: 52ch; margin: 0 0 1.6rem; }

/* Search field + button */
.stTextInput input {
  background: var(--sheet) !important;
  color: var(--ink) !important;
  border: 2px solid var(--ink) !important;
  border-radius: 999px !important;
  padding: 1.05rem 1.5rem !important;
  font-size: 1.1rem !important;
  font-family: 'Figtree', sans-serif !important;
}
.stTextInput input:focus { border-color: var(--cyan) !important; box-shadow: 0 0 0 4px rgba(31,78,156,.15) !important; }
.stTextInput input::placeholder { color: #8A97AE !important; }
div.stButton > button {
  font-family: 'Figtree', sans-serif !important;
  border-radius: 999px !important;
  font-weight: 600 !important;
  transition: background .15s, color .15s, border-color .15s;
}
div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"] {
  background: var(--ink) !important; color: #fff !important; border: 2px solid var(--ink) !important;
  padding: .95rem 1rem !important; font-size: 1.02rem !important;
}
div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="stBaseButton-primary"]:hover {
  background: var(--cyan) !important; border-color: var(--cyan) !important; color:#fff !important;
}
div.stButton > button[kind="secondary"], div.stButton > button[data-testid="stBaseButton-secondary"] {
  background: transparent !important; color: var(--cyan) !important;
  border: 1.5px solid var(--rule) !important; font-size: .88rem !important; padding: .35rem .9rem !important;
}
div.stButton > button[kind="secondary"]:hover, div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
  border-color: var(--cyan) !important; background: #fff !important; color: var(--cyan) !important;
}
.try-label { color: var(--muted); font-size: .9rem; margin: 1.1rem 0 .2rem; }

/* Results header */
.summary { margin: 2.4rem 0 1.1rem; padding-bottom: .9rem; border-bottom: 2px solid var(--ink); display:flex; justify-content:space-between; align-items:baseline; gap:1rem; flex-wrap:wrap; }
.summary .q { font-family:'Instrument Serif', serif; font-style: italic; font-size: 1.9rem; line-height:1.15; }
.summary .n { color: var(--muted); font-size: .92rem; }

/* Light table */
.sheet { display:grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.slide { background: var(--sheet); border: 1px solid var(--rule); border-radius: 6px; overflow: hidden; display:flex; flex-direction:column; }
.slide.best { grid-column: span 2; grid-row: span 2; border: 2px solid var(--amber); }
.mat { background: var(--ink); padding: 10px 10px 0; position: relative; flex: 1; min-height: 0; display:flex; }
.mat img { width:100%; height:100%; aspect-ratio: 4/3; object-fit: cover; display:block; border-radius: 2px; animation: develop 1.1s ease-out both; }
.slide.best .mat img { aspect-ratio: auto; min-height: 340px; }
.rank { position:absolute; top:18px; left:18px; background: rgba(20,33,61,.88); color:#fff; font-weight:700; font-size:.82rem; padding:.2rem .6rem; border-radius:999px; }
.best .rank { background: var(--amber); color: var(--ink); }
.meta { padding: .8rem 1rem 1rem; }
.meter { height: 6px; background: #E5ECF6; border-radius: 99px; overflow:hidden; }
.meter i { display:block; height:100%; background: var(--cyan); border-radius: 99px; }
.best .meter i { background: var(--amber); }
.row { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:.45rem; font-size:.85rem; }
.row b { font-size: 1.05rem; font-variant-numeric: tabular-nums; }
.row span { color: var(--muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width: 60%; }
.cap { margin: .75rem 0 0; font-size:.88rem; line-height:1.5; color:#2B3A57; max-width: 62ch; }
.slide:not(.best) .cap { display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
.missing { padding: 2rem 1rem; color:#9B2C2C; font-size:.9rem; background:#FFF5F5; }

/* Empty state */
.empty { border: 2px dashed var(--rule); border-radius: 10px; padding: 3rem 1.5rem; text-align:center; color: var(--muted); margin-top: 2rem; }
.empty strong { display:block; font-family:'Instrument Serif', serif; font-weight:400; font-size:1.7rem; color: var(--ink); margin-bottom:.3rem; }

@keyframes develop {
  from { filter: blur(14px) grayscale(1) contrast(.6) brightness(1.25); transform: scale(1.03); }
  to   { filter: none; transform: none; }
}
@media (prefers-reduced-motion: reduce) { .mat img { animation: none; } }
@media (max-width: 900px) {
  .sheet { grid-template-columns: repeat(2, 1fr); }
  .slide.best .mat img { min-height: 220px; }
}
@media (max-width: 520px) {
  .sheet { grid-template-columns: 1fr; }
  .slide.best { grid-column: auto; grid-row: auto; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
@st.cache_resource
def load_engine():
    return ImageSearchEngine()


@st.cache_data(show_spinner=False)
def thumb_b64(path: str, max_side: int = 900) -> str:
    """Resize once and embed as base64 so the HTML grid stays fast and fully styleable."""
    img = Image.open(path).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def read_caption(filename: str) -> str:
    p = os.path.join("captions", os.path.splitext(filename)[0] + ".txt")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def slide_html(rank: int, res: dict, top_score: float) -> str:
    fname = res["filename"]
    path = os.path.join("images", fname)
    best = rank == 1
    cls = "slide best" if best else "slide"

    if not os.path.exists(path):
        return f'<div class="{cls}"><div class="missing">Missing file: {html.escape(fname)}. Check the images folder.</div></div>'

    score = float(res["score"])
    pct = max(4, min(100, (score / top_score) * 100)) if top_score > 0 else 4
    cap = html.escape(read_caption(fname))
    cap_html = f'<p class="cap">{cap}</p>' if cap else ""
    img = thumb_b64(path, 1100 if best else 600)

    return (
        f'<div class="{cls}">'
        f'<div class="mat"><img src="data:image/jpeg;base64,{img}" alt="{html.escape(fname)}"/>'
        f'<div class="rank">{"Best match" if best else f"#{rank}"}</div></div>'
        f'<div class="meta">'
        f'<div class="row"><b>{score:.3f}</b><span title="{html.escape(fname)}">{html.escape(fname)}</span></div>'
        f'<div class="meter"><i style="width:{pct:.1f}%"></i></div>'
        f'{cap_html}</div></div>'
    )


engine = load_engine()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")
    top_k = st.slider("Number of results", min_value=1, max_value=12, value=5, step=1)
    st.markdown("### About this index")
    st.markdown(
        f'<div class="side-fact"><span>Images</span><span>{len(engine.filenames)}</span></div>'
        '<div class="side-fact"><span>Model</span><span>CLIP ViT-B/32</span></div>'
        '<div class="side-fact"><span>Ranking</span><span>Cosine similarity</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("IIT Bhubaneswar internship project")

# ---------------------------------------------------------------------------
# Masthead + search
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="mast"><h1>Describe a scene. Find the frame.</h1>'
    '<p>Type what you remember in plain words. The search matches meaning, not file names or tags.</p></div>',
    unsafe_allow_html=True,
)

EXAMPLES = ["a dog running on a beach", "city street at night", "people eating together", "snow covered mountain"]

if "q" not in st.session_state:
    st.session_state.q = ""


def use_example(text: str):
    st.session_state.q = text


col_input, col_btn = st.columns([6, 1], vertical_alignment="center")
with col_input:
    query = st.text_input(
        "Search", key="q", placeholder="a child laughing in the rain…", label_visibility="collapsed"
    )
with col_btn:
    st.button("Find images", type="primary", use_container_width=True)

st.markdown('<div class="try-label">Try one of these</div>', unsafe_allow_html=True)
chip_cols = st.columns(len(EXAMPLES) + 2)
for c, ex in zip(chip_cols, EXAMPLES):
    with c:
        st.button(ex, key=f"ex_{ex}", on_click=use_example, args=(ex,), use_container_width=True)

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
q = query.strip()
if not q:
    st.markdown(
        '<div class="empty"><strong>Nothing on the table yet</strong>'
        "Enter a description above, or pick an example, to see the closest matches.</div>",
        unsafe_allow_html=True,
    )
else:
    with st.spinner("Searching the index…"):
        results = engine.search(query_text=q, top_k=top_k)

    if not results:
        st.markdown(
            '<div class="empty"><strong>No matches found</strong>'
            "Try fewer words or describe the main subject, for example “a red car”.</div>",
            unsafe_allow_html=True,
        )
    else:
        top_score = max(float(r["score"]) for r in results)
        st.markdown(
            f'<div class="summary"><div class="q">“{html.escape(q)}”</div>'
            f'<div class="n">{len(results)} closest matches · bars are relative to the best score</div></div>',
            unsafe_allow_html=True,
        )
        slides = "".join(slide_html(i, r, top_score) for i, r in enumerate(results, start=1))
        st.markdown(f'<div class="sheet">{slides}</div>', unsafe_allow_html=True)