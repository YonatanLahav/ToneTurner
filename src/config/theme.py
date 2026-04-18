from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    bg: str
    sidebar_bg: str
    input_bg: str
    text: str
    text_muted: str
    border: str
    btn_bg: str
    btn_hover_bg: str
    btn_hover_border: str
    alert_bg: str
    code_bg: str


LIGHT = ColorPalette(
    bg               = "#ffffff",
    sidebar_bg       = "#f0f2f6",
    input_bg         = "#ffffff",
    text             = "#31333f",
    text_muted       = "#888888",
    border           = "#d0d0d8",
    btn_bg           = "#ffffff",
    btn_hover_bg     = "#f0f2f6",
    btn_hover_border = "#7c3aed",
    alert_bg         = "#f0f2f6",
    code_bg          = "#f0f2f6",
)

DARK = ColorPalette(
    bg               = "#0e1117",
    sidebar_bg       = "#1a1c26",
    input_bg         = "#1e2130",
    text             = "#fafafa",
    text_muted       = "#aaaaaa",
    border           = "#4a4a5a",
    btn_bg           = "#2a2a3a",
    btn_hover_bg     = "#3a3a4f",
    btn_hover_border = "#7c3aed",
    alert_bg         = "#1e2130",
    code_bg          = "#1e2130",
)


def build_css(p: ColorPalette) -> str:
    return f"""
<style>
    .stApp                                      {{ background-color: {p.bg} !important; }}
    .stApp > header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"]                {{ background-color: {p.bg} !important; }}
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div             {{ background-color: {p.sidebar_bg} !important; }}
    .block-container                            {{ background-color: {p.bg} !important; }}

    html, body, .stApp, .stMarkdown,
    p, li, span, label, div                     {{ color: {p.text} !important; }}
    h1, h2, h3, h4, h5, h6                     {{ color: {p.text} !important; }}
    [data-testid="stSidebar"] *                 {{ color: {p.text} !important; }}
    .stCaption, small                           {{ color: {p.text_muted} !important; }}

    [data-testid="stTextArea"] textarea,
    [data-testid="stTextArea"] textarea:disabled,
    [data-testid="stTextInput"] input,
    [data-testid="stTextInput"] input:disabled    {{
        background-color: {p.input_bg} !important;
        color: {p.text} !important;
        border-color: {p.border} !important;
        -webkit-text-fill-color: {p.text} !important;
        opacity: 1 !important;
    }}

    .stButton > button                          {{
        background-color: {p.btn_bg} !important;
        color: {p.text} !important;
        border-color: {p.border} !important;
    }}
    .stButton > button:hover                    {{
        background-color: {p.btn_hover_bg} !important;
        border-color: {p.btn_hover_border} !important;
    }}

    [data-testid="stExpander"],
    [data-testid="stExpander"] > details,
    [data-testid="stExpander"] > details > summary  {{
        background-color: {p.sidebar_bg} !important;
        border-color: {p.border} !important;
    }}
    [data-testid="stExpander"] > details > summary,
    [data-testid="stExpander"] > details > summary *,
    [data-testid="stExpander"] > details > summary p,
    [data-testid="stExpander"] > details > summary span,
    [data-testid="stExpander"] > details > summary svg,
    [data-testid="stExpander"] > details > summary svg *,
    .streamlit-expanderHeader,
    .streamlit-expanderHeader *                     {{ color: {p.text} !important;
                                                       fill: {p.text} !important; }}

    [data-testid="stAlert"]                     {{ background-color: {p.alert_bg} !important; }}
    .stCode, code, pre                          {{
        background-color: {p.code_bg} !important;
        color: {p.text} !important;
    }}
    hr                                          {{ border-color: {p.border} !important; }}
    [data-testid="stToggle"] span               {{ color: {p.text} !important; }}
</style>
"""
