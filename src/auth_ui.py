import base64
from pathlib import Path
import streamlit as st


def _get_bg_image_css() -> str:
    base_dir = Path(__file__).resolve().parent
    for fname in ["infosys_bg.png", "infosys_bg.jpg", "image_24a160.png"]:
        fpath = base_dir / fname
        if fpath.exists():
            encoded = base64.b64encode(fpath.read_bytes()).decode()
            ext = "png" if fname.endswith(".png") else "jpeg"
            return f"url('data:image/{ext};base64,{encoded}')"
    return "url('https://upload.wikimedia.org/wikipedia/commons/e/e5/Infosys_%284911287708%29.jpg')"


def render_infosys_auth_gateway(verify_user_fn, register_user_fn):
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "auth_view_mode" not in st.session_state:
        st.session_state.auth_view_mode = "Login"

    if st.session_state.authenticated:
        return

    bg_url = _get_bg_image_css()

    css_styles = f"""
        <style>
        @keyframes springboardFadeIn {{
            0% {{ opacity: 0; transform: translateY(18px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        header[data-testid="stHeader"], .stAppHeader, [data-testid="stSidebar"] {{
            display: none !important;
        }}
        .stApp {{
            background: linear-gradient(
                105deg,
                rgba(2, 10, 20, 0.95) 0%,
                rgba(3, 18, 36, 0.90) 50%,
                rgba(5, 25, 50, 0.82) 100%
            ), {bg_url} !important;
            background-size: cover !important;
            background-position: center center !important;
            background-attachment: fixed !important;
        }}
        /* Top Infosys Springboard  Equinox Navbar */
        .equinox-navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 36px;
            background: rgba(2, 14, 28, 0.92);
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 8px;
            margin-bottom: 1.8rem;
        }}
        .equinox-links span {{
            color: #F8FAFC !important;
            font-size: 13.5px;
            font-weight: 600;
            margin: 0 12px;
        }}
        .equinox-demo-btn {{
            background: #1D63FF;
            color: #FFFFFF !important;
            padding: 7px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
        }}
        
        /* SOLID OPAQUE CARD FOR LEFT HERO */
        .hero-solid-card {{
            background-color: #031226 !important;
            border: 2px solid rgba(56, 189, 248, 0.25) !important;
            border-radius: 14px !important;
            padding: 2.2rem !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8) !important;
        }}
        .hero-solid-card h1, .hero-solid-card p, .hero-solid-card span {{
            color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        /* White Infosys Springboard Card on Right */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.springboard-card-marker) {{
            background: #FFFFFF !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 2rem 2.2rem 1.6rem 2.2rem !important;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.50) !important;
            animation: springboardFadeIn 0.5s ease-out forwards !important;
        }}

        div[data-baseweb="input"] {{
            border-radius: 3px !important;
            border: 1px solid #6B8EA8 !important;
            background-color: #FFFFFF !important;
            min-height: 42px !important;
        }}
        div[data-baseweb="input"]:focus-within {{
            border-color: #005A8B !important;
            box-shadow: 0 0 0 2px rgba(0, 90, 139, 0.18) !important;
        }}
        div[data-baseweb="input"] button {{
            background: transparent !important;
            color: #005A8B !important;
            border: none !important;
        }}
        
        /* Primary Button (Log In) */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.springboard-card-marker) div.stButton > button[kind="primary"] {{
            background: #005A8B !important;
            color: #FFFFFF !important;
            border: 1px solid #004870 !important;
            border-radius: 3px !important;
            height: 42px !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.springboard-card-marker) div.stButton > button[kind="primary"]:hover {{
            background: #00446B !important;
        }}

        /* Secondary Button (Register / Toggle) */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.springboard-card-marker) div.stButton > button[kind="secondary"] {{
            background: #F0F7FC !important;
            color: #005A8B !important;
            border: 1px solid #005A8B !important;
            border-radius: 3px !important;
            height: 40px !important;
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            width: 100% !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.springboard-card-marker) div.stButton > button[kind="secondary"]:hover {{
            background: #DDEBF7 !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.springboard-card-marker) div.stButton > button[kind="secondary"] p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.springboard-card-marker) div.stButton > button[kind="secondary"] span {{
            color: #005A8B !important;
            font-weight: 700 !important;
        }}
        </style>
        <div class="equinox-navbar">
            <div>
                <span style="color:#FFFFFF; font-size:21px; font-weight:700;">Infosys Springboard</span>
                <span style="color:#38BDF8; font-size:21px; font-weight:300;">equinox</span>
            </div>
            <div class="equinox-links">
                <span>Platform ⌄</span>
                <span>5-Agent Pipeline ⌄</span>
                <span>Vector KB</span>
                <span>Telemetry</span>
                <span>About Us ⌄</span>
            </div>
            <div class="equinox-demo-btn">Live Telemetry ↗</div>
        </div>
    """

    st.markdown(css_styles, unsafe_allow_html=True)

    left_hero, right_card = st.columns([1.3, 1], gap="large")

    with left_hero:
        st.markdown(
            """
            <div class="hero-solid-card">
                <h1 style="color: #FFFFFF !important; font-size: 38px; font-weight: 900; line-height: 1.15; margin-bottom: 16px; font-family: 'Segoe UI', sans-serif;">
                    The Agentic Bug Diagnosis Platform for a New Era
                </h1>
                <p style="color: #38BDF8 !important; font-size: 15px; font-weight: 700; margin-bottom: 14px;">
                    Embed autonomous defect intelligence across the software value chain.
                </p>
                <p style="color: #E2E8F0 !important; font-size: 14px; line-height: 1.65; margin-bottom: 16px;">
                    Intelligent Bug Diagnosis Platform is an AI-first, multi-agent composable diagnostic
                    engine that embeds autonomous triage, log analysis, RAG root-cause hypothesis,
                    duplicate detection, and code remediation across 29,161+ historical defects.
                </p>
                <p style="color: #93C5FD !important; font-weight: 700; font-size: 13px; margin-top: 18px;">
                    AI-First Diagnosis Platform &nbsp;|&nbsp; Powered by <strong>5-Agent RAG Fabric</strong> &nbsp;|&nbsp; Enterprise Scale
                </p>
                <div style="display:flex; gap:14px; margin-top:20px;">
                    <span style="background:#1D63FF; color:#FFF; padding:10px 20px; border-radius:6px; font-weight:600; font-size:13.5px; box-shadow: 0 4px 12px rgba(29,99,255,0.4);">
                        Explore Agentic Triage ↗
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_card:
        with st.container(border=True):
            st.markdown(
                """
                <div class="springboard-card-marker"></div>
                <div style="text-align: center; margin-bottom: 12px;">
                    <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 30px; font-weight: 700; color: #007CC3; line-height: 1;">
                        Infosys
                    </div>
                    <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: 700; margin-top: 2px;">
                        <span style="color: #007CC3;">Spring</span><span style="color: #F26B3A;">board</span>
                        <span style="color: #64748B; font-size: 11px; font-weight: 600;">| Defect Portal</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 10px;">
                    <span style="color: #005A8B; font-weight: 800; font-size: 13px;">Email</span>
                    <span style="display: inline-flex; align-items: center; background: #005A8B; color: #FFF; border-radius: 12px; padding: 1px 8px; font-size: 10px; font-weight: 700;">
                        ● Active
                    </span>
                    <span style="color: #64748B; font-size: 12px; margin-left: auto;">Phone</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            mode = st.session_state.auth_view_mode

            # Custom HTML Label for Email to guarantee 100% visibility
            st.markdown('<div style="color: #005A8B; font-weight: 800; font-size: 13px; margin-bottom: 4px;">Email ID</div>', unsafe_allow_html=True)
            email_input = st.text_input(
                "Email",
                placeholder="✉️  Enter your registered email id",
                label_visibility="collapsed",
            )

            # Custom HTML Label for Password to guarantee 100% visibility
            st.markdown('<div style="color: #005A8B; font-weight: 800; font-size: 13px; margin: 10px 0 4px 0;">Password</div>', unsafe_allow_html=True)
            pass_input = st.text_input(
                "Password",
                type="password",
                placeholder="🔒  Enter your password",
                label_visibility="collapsed",
            )

            st.markdown(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0 12px 0; font-size: 12px;">
                    <span style="color: #005A8B; font-weight: 700;">Forgot Password?</span>
                    <label style="color: #475569; display: inline-flex; align-items: center; gap: 5px; font-size: 12px;">
                        <input type="checkbox" checked style="accent-color: #005A8B;"> Remember me
                    </label>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if mode == "Login":
                if st.button("Log In", type="primary", width="stretch"):
                    if verify_user_fn(email_input, pass_input):
                        st.session_state.authenticated = True
                        st.session_state.user_email = email_input.strip().lower()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
            else:
                if st.button("Register Account", type="primary", width="stretch"):
                    success, msg = register_user_fn(email_input, pass_input)
                    if success:
                        st.success(msg)
                        st.session_state.auth_view_mode = "Login"
                    else:
                        st.error(msg)

            st.markdown('<hr style="border: none; border-top: 1px solid #CBD8E6; margin: 16px 0 12px 0;">', unsafe_allow_html=True)

            toggle_label = "New user? Register" if mode == "Login" else "Existing user? Log In"
            if st.button(toggle_label, type="secondary", width="stretch"):
                st.session_state.auth_view_mode = "Register" if mode == "Login" else "Login"
                st.rerun()

    st.stop()