"""
LinkedIn Content Ops — Streamlit App
=====================================
Content operations dashboard for Rahul Jindal's LinkedIn Growth project.
Pages: Content Calendar, Post Drafting, Series Dashboard, Performance Analytics.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------------------------
# Cloud detection & auth
# ---------------------------------------------------------------------------

def _is_cloud() -> bool:
    """Check if running on Streamlit Cloud."""
    return (
        os.environ.get("STREAMLIT_SHARING_MODE") == "true"
        or os.path.exists("/mount/src")
    )


def _check_auth():
    """Password gate — blocks access until correct password is entered."""
    if st.session_state.get("authenticated"):
        return

    st.title("LinkedIn Content Ops")
    st.markdown(
        '<p style="color:#8b949e; font-size:15px;">Enter password to continue.</p>',
        unsafe_allow_html=True,
    )
    password = st.text_input("Password", type="password", key="login_password")
    if password:
        app_password = st.secrets.get("app_password", "contentops2024")
        if password == app_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
CONTENT_DIR = APP_DIR / "content"
DATA_DIR = APP_DIR / "data"
DRAFTS_DIR = APP_DIR / "drafts"
JSON_PATH = DATA_DIR / "scraped_posts.json"

LINKEDIN_CHAR_LIMIT = 3000

# Series definitions — maps series key to display info and source files
SERIES_CONFIG = {
    "org_metabolism": {
        "name": "Organizational Metabolism",
        "color": "#58a6ff",
        "files": ["org_metabolism_series.md"],
        "description": "Framework for how enterprises convert AI intelligence into structural advantage. 12-chapter book plan.",
        "target_posts": 10,
    },
    "career_volume": {
        "name": "Career Volume",
        "color": "#3fb950",
        "files": ["career_volume_series.md", "career_volume_expansion.md"],
        "description": "Length x Breadth x Depth — a framework for multi-dimensional careers. 15-chapter book plan.",
        "target_posts": 15,
    },
    "life_after_ai": {
        "name": "Life After AI",
        "color": "#bc8cff",
        "files": [
            "life_after_ai_series.md",
            "life_after_ai_series_part2.md",
            "life_after_ai_series_part3.md",
        ],
        "description": "15 dimensions of human life reshaped by AI — from daily schedules to love, income to meaning. 27 posts drafted.",
        "target_posts": 27,
    },
    "shadow_and_shade": {
        "name": "Shadow and Shade",
        "color": "#f0883e",
        "files": [
            "shadow_and_shade_series.md",
            "shadow_and_shade_hard_conversations.md",
        ],
        "description": "The Honest Manager's Playbook — Good vs Nice, the daily choice every manager faces.",
        "target_posts": 15,
    },
    "awakening_assets_access": {
        "name": "Awakening, Assets & Access",
        "color": "#f778ba",
        "files": [
            "awakening_assets_access_series.md",
            "awakening_missing_stories.md",
        ],
        "description": "Lessons from an unlikely life — memoir meets philosophy. Awakening + Assets + Access = Impact.",
        "target_posts": 15,
    },
}

STATUS_OPTIONS = ["Draft", "Review", "Scheduled", "Published"]
STATUS_COLORS = {
    "Draft": "#8b949e",
    "Review": "#d29922",
    "Scheduled": "#58a6ff",
    "Published": "#3fb950",
}


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def _state_file() -> Path:
    """Path to the local state file tracking post statuses and metadata."""
    return APP_DIR / "data" / "content_ops_state.json"


def load_state() -> dict:
    """Load the content ops state (post statuses, scheduled dates, etc.).

    On Cloud: uses st.session_state (ephemeral, lost on restart).
    Locally: reads from data/content_ops_state.json.
    """
    if _is_cloud():
        return st.session_state.get("_content_ops_state", {"posts": {}, "drafts": {}})
    path = _state_file()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posts": {}, "drafts": {}}


def save_state(state: dict):
    """Persist content ops state.

    On Cloud: saves to st.session_state (ephemeral).
    Locally: writes to data/content_ops_state.json.
    """
    if _is_cloud():
        st.session_state["_content_ops_state"] = state
        return
    path = _state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def parse_posts_from_md(filepath: Path) -> list[dict]:
    """Parse a series markdown file into individual posts.

    Returns list of dicts with keys: title, number, body, series_file.
    """
    if not filepath.exists():
        return []
    text = filepath.read_text(encoding="utf-8")
    # Split on ## Post N: ...
    pattern = r"^## Post (\d+)(?:/\d+)?:\s*(.+?)$"
    parts = re.split(pattern, text, flags=re.MULTILINE)
    posts = []
    # parts[0] is the header before first post
    # then groups of 3: number, title, body
    i = 1
    while i + 2 <= len(parts):
        num = parts[i].strip()
        title = parts[i + 1].strip()
        body = parts[i + 2].strip()
        # Clean up body — remove trailing --- dividers
        body = re.sub(r"\n---\s*$", "", body).strip()
        posts.append({
            "number": int(num),
            "title": title,
            "body": body,
            "series_file": filepath.name,
        })
        i += 3
    return posts


def get_all_series_posts() -> dict[str, list[dict]]:
    """Load all posts from all series. Returns {series_key: [post_dicts]}."""
    result = {}
    for key, cfg in SERIES_CONFIG.items():
        posts = []
        for fname in cfg["files"]:
            fpath = CONTENT_DIR / fname
            posts.extend(parse_posts_from_md(fpath))
        result[key] = posts
    return result


def load_scraped_posts() -> pd.DataFrame:
    """Load scraped_posts.json into a DataFrame."""
    if not JSON_PATH.exists():
        return pd.DataFrame(columns=[
            "post_text", "date", "reactions", "comments",
            "impressions", "post_url", "source", "collected_at",
        ])
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["reactions", "comments", "impressions"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


def get_post_key(series_key: str, post_number: int, post_title: str) -> str:
    """Create a unique key for a post in the state store."""
    return f"{series_key}::{post_number}::{post_title[:40]}"


def ensure_drafts_dir():
    """Create drafts directory if it doesn't exist."""
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Page: Content Calendar
# ---------------------------------------------------------------------------


def page_content_calendar():
    st.header("Content Calendar")
    st.caption("Track all drafted posts across series — from Draft to Published.")

    state = load_state()
    all_posts = get_all_series_posts()

    # Flatten all posts with their status
    flat = []
    for series_key, posts in all_posts.items():
        cfg = SERIES_CONFIG[series_key]
        for p in posts:
            pkey = get_post_key(series_key, p["number"], p["title"])
            post_state = state.get("posts", {}).get(pkey, {})
            status = post_state.get("status", "Draft")
            scheduled_date = post_state.get("scheduled_date", "")
            flat.append({
                "Series": cfg["name"],
                "Post #": p["number"],
                "Title": p["title"],
                "Status": status,
                "Scheduled": scheduled_date,
                "Key": pkey,
                "series_key": series_key,
                "color": cfg["color"],
            })

    if not flat:
        st.info("No series posts found. Check that content/ directory has series markdown files.")
        return

    df = pd.DataFrame(flat)

    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        series_filter = st.multiselect(
            "Filter by Series",
            options=sorted(df["Series"].unique()),
            default=sorted(df["Series"].unique()),
        )
    with col_f2:
        status_filter = st.multiselect(
            "Filter by Status",
            options=STATUS_OPTIONS,
            default=STATUS_OPTIONS,
        )

    mask = df["Series"].isin(series_filter) & df["Status"].isin(status_filter)
    filtered = df[mask].copy()

    # Summary metrics
    total = len(filtered)
    by_status = filtered["Status"].value_counts()
    cols = st.columns(4)
    for i, s in enumerate(STATUS_OPTIONS):
        count = by_status.get(s, 0)
        cols[i].metric(s, count)

    st.divider()

    # Status update section
    st.subheader("Update Post Status")
    st.caption("Select posts and change their status or set a scheduled date.")

    for series_key in series_filter:
        series_posts = filtered[filtered["Series"] == series_key].sort_values("Post #")
        if series_posts.empty:
            continue

        cfg_match = [v for v in SERIES_CONFIG.values() if v["name"] == series_key]
        color = cfg_match[0]["color"] if cfg_match else "#58a6ff"

        st.markdown(
            f'<div style="padding:8px 16px; background:{color}22; border-left:4px solid {color}; '
            f'border-radius:4px; margin-bottom:12px;">'
            f'<strong style="color:{color};">{series_key}</strong></div>',
            unsafe_allow_html=True,
        )

        for _, row in series_posts.iterrows():
            status_color = STATUS_COLORS.get(row["Status"], "#8b949e")
            col_title, col_status, col_date, col_save = st.columns([3, 1.5, 1.5, 1])
            with col_title:
                st.markdown(
                    f'<span style="font-size:14px;">**Post {row["Post #"]}:** {row["Title"]}</span>',
                    unsafe_allow_html=True,
                )
            with col_status:
                new_status = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(row["Status"]),
                    key=f"status_{row['Key']}",
                    label_visibility="collapsed",
                )
            with col_date:
                sched = row["Scheduled"]
                default_date = datetime.now().date()
                if sched:
                    try:
                        default_date = datetime.strptime(sched, "%Y-%m-%d").date()
                    except ValueError:
                        pass
                new_date = st.date_input(
                    "Date",
                    value=default_date,
                    key=f"date_{row['Key']}",
                    label_visibility="collapsed",
                )
            with col_save:
                if st.button("Save", key=f"save_{row['Key']}"):
                    if "posts" not in state:
                        state["posts"] = {}
                    state["posts"][row["Key"]] = {
                        "status": new_status,
                        "scheduled_date": new_date.strftime("%Y-%m-%d"),
                    }
                    save_state(state)
                    st.toast(f"Updated: Post {row['Post #']} - {row['Title']}")

    # Key Insights
    st.divider()
    draft_count = by_status.get("Draft", 0)
    published_count = by_status.get("Published", 0)
    scheduled_count = by_status.get("Scheduled", 0)
    total_all = len(df)
    st.markdown(
        f"""<div style="background:#161b22; border:1px solid #30363d; border-radius:8px; padding:16px; margin-top:8px;">
<strong style="color:#58a6ff; font-size:15px;">Key Insights</strong><br>
<span style="color:#c9d1d9; font-size:14px;">
- <strong>Action:</strong> {total_all} total posts across {len(SERIES_CONFIG)} series. {draft_count} still in Draft status.<br>
- <strong>Action:</strong> {published_count} published, {scheduled_count} scheduled. {"Set dates for drafts to build your publishing pipeline." if draft_count > 0 else "Pipeline is flowing."}<br>
- <strong>Action:</strong> {"Move your best drafted posts to Review, then Schedule with specific dates to maintain posting cadence." if draft_count > scheduled_count else "Good pipeline coverage."}<br>
</span></div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page: Post Drafting
# ---------------------------------------------------------------------------


def page_post_drafting():
    st.header("Post Drafting")
    st.caption("Draft new posts for any series. Preview formatting and character count.")

    # Select series
    series_options = {cfg["name"]: key for key, cfg in SERIES_CONFIG.items()}
    selected_name = st.selectbox("Select Series", list(series_options.keys()))
    series_key = series_options[selected_name]
    cfg = SERIES_CONFIG[series_key]

    # Show series context
    st.markdown(
        f'<div style="background:{cfg["color"]}15; border-left:4px solid {cfg["color"]}; '
        f'padding:12px 16px; border-radius:4px; margin-bottom:16px;">'
        f'<strong style="color:{cfg["color"]};">{cfg["name"]}</strong><br>'
        f'<span style="color:#c9d1d9; font-size:14px;">{cfg["description"]}</span><br>'
        f'<span style="color:#8b949e; font-size:13px;">Target: {cfg["target_posts"]} posts | '
        f'Files: {", ".join(cfg["files"])}</span></div>',
        unsafe_allow_html=True,
    )

    # Show existing posts in this series
    all_posts = get_all_series_posts()
    series_posts = all_posts.get(series_key, [])

    with st.expander(f"Existing Posts in {cfg['name']} ({len(series_posts)} posts)", expanded=False):
        for p in series_posts:
            st.markdown(f"**Post {p['number']}:** {p['title']}")

    st.divider()

    # Draft editor
    st.subheader("New Draft")

    col_title, col_num = st.columns([3, 1])
    with col_title:
        draft_title = st.text_input(
            "Post Title",
            placeholder="e.g., The Metabolism Gap — Why AI Transformations Fail",
        )
    with col_num:
        next_num = max([p["number"] for p in series_posts], default=0) + 1
        draft_number = st.number_input("Post Number", min_value=1, value=next_num)

    # Series header suggestion
    series_header = f"{cfg['name']} | Part {draft_number}"
    st.caption(f"Suggested series header: **{series_header}**")

    draft_body = st.text_area(
        "Post Content",
        height=350,
        placeholder="Write your LinkedIn post here...\n\nTips:\n- Keep it 150-350 words for feed posts\n- Start with a hook (story, surprising stat, question)\n- End with a question to drive comments\n- Use **bold** for key frameworks/terms",
    )

    # Character count and word count
    if draft_body:
        char_count = len(draft_body)
        word_count = len(draft_body.split())
        char_pct = (char_count / LINKEDIN_CHAR_LIMIT) * 100

        col_c, col_w = st.columns(2)
        with col_c:
            bar_color = "#3fb950" if char_count <= LINKEDIN_CHAR_LIMIT else "#f85149"
            st.markdown(
                f'<div style="font-size:14px; color:{bar_color};">'
                f'{char_count:,} / {LINKEDIN_CHAR_LIMIT:,} characters ({char_pct:.0f}%)</div>',
                unsafe_allow_html=True,
            )
        with col_w:
            word_color = "#3fb950" if 150 <= word_count <= 350 else "#d29922"
            st.markdown(
                f'<div style="font-size:14px; color:{word_color};">'
                f'{word_count} words {"(sweet spot!)" if 150 <= word_count <= 350 else "(aim for 150-350)"}</div>',
                unsafe_allow_html=True,
            )

        # Preview
        with st.expander("LinkedIn Preview", expanded=False):
            preview_text = f"**{series_header}**\n\n{draft_body}"
            st.markdown(
                f'<div style="background:#1b1f23; border:1px solid #30363d; border-radius:8px; '
                f'padding:20px; font-family:system-ui; font-size:14px; line-height:1.6; color:#e1e4e8;">'
                f'{preview_text}</div>',
                unsafe_allow_html=True,
            )

    # Save draft
    st.divider()
    if st.button("Save Draft", type="primary", disabled=not (draft_title and draft_body)):
        safe_title = re.sub(r"[^\w\s-]", "", draft_title).strip().replace(" ", "_")[:50]
        filename = f"{series_key}_post{draft_number}_{safe_title}.md"

        content = f"""# {cfg['name']} | Post {draft_number}: {draft_title}

Series: {cfg['name']}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Status: Draft
Word Count: {len(draft_body.split())}
Characters: {len(draft_body)}

---

**{series_header}**

{draft_body}
"""

        if _is_cloud():
            # On Cloud: store in session_state (ephemeral)
            if "_draft_files" not in st.session_state:
                st.session_state["_draft_files"] = {}
            st.session_state["_draft_files"][filename] = content
        else:
            # Locally: write to drafts/ directory
            ensure_drafts_dir()
            filepath = DRAFTS_DIR / filename
            filepath.write_text(content, encoding="utf-8")

        # Update state
        state = load_state()
        pkey = get_post_key(series_key, draft_number, draft_title)
        if "posts" not in state:
            state["posts"] = {}
        state["posts"][pkey] = {
            "status": "Draft",
            "scheduled_date": "",
            "draft_file": filename,
        }
        if "drafts" not in state:
            state["drafts"] = {}
        state["drafts"][pkey] = {
            "file": filename,
            "created": datetime.now().isoformat(),
        }
        save_state(state)

        st.success(f"Draft saved: {filename}")

    # Show existing drafts
    _show_saved_drafts()


def _show_saved_drafts():
    """Display saved drafts from filesystem (local) or session_state (Cloud)."""
    if _is_cloud():
        draft_store = st.session_state.get("_draft_files", {})
        if draft_store:
            st.divider()
            st.subheader("Saved Drafts (this session)")
            for fname, content in sorted(draft_store.items()):
                col_name, col_view = st.columns([4, 1])
                with col_name:
                    st.text(fname)
                with col_view:
                    if st.button("View", key=f"view_{fname}"):
                        st.code(content, language="markdown")
    else:
        if DRAFTS_DIR.exists():
            draft_files = sorted(DRAFTS_DIR.glob("*.md"))
            if draft_files:
                st.divider()
                st.subheader("Saved Drafts")
                for df_path in draft_files:
                    col_name, col_del = st.columns([4, 1])
                    with col_name:
                        st.text(df_path.name)
                    with col_del:
                        if st.button("View", key=f"view_{df_path.name}"):
                            st.code(df_path.read_text(encoding="utf-8"), language="markdown")


# ---------------------------------------------------------------------------
# Page: Series Dashboard
# ---------------------------------------------------------------------------


def page_series_dashboard():
    st.header("Series Dashboard")
    st.caption("Overview of content production across all series.")

    all_posts = get_all_series_posts()
    state = load_state()
    scraped = load_scraped_posts()

    # Build series stats
    series_stats = []
    for key, cfg in SERIES_CONFIG.items():
        posts = all_posts.get(key, [])
        total_drafted = len(posts)
        target = cfg["target_posts"]

        # Count by status from state
        published = 0
        scheduled = 0
        review = 0
        draft = 0
        for p in posts:
            pkey = get_post_key(key, p["number"], p["title"])
            s = state.get("posts", {}).get(pkey, {}).get("status", "Draft")
            if s == "Published":
                published += 1
            elif s == "Scheduled":
                scheduled += 1
            elif s == "Review":
                review += 1
            else:
                draft += 1

        series_stats.append({
            "series_key": key,
            "name": cfg["name"],
            "color": cfg["color"],
            "target": target,
            "drafted": total_drafted,
            "published": published,
            "scheduled": scheduled,
            "review": review,
            "draft": draft,
            "completion_pct": round((total_drafted / target) * 100) if target else 0,
        })

    # Series cards
    for s in series_stats:
        pct = s["completion_pct"]
        bar_w = min(pct, 100)

        st.markdown(
            f"""<div style="background:#161b22; border:1px solid #30363d; border-radius:10px; padding:20px; margin-bottom:16px;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
    <div>
      <strong style="color:{s['color']}; font-size:17px;">{s['name']}</strong>
      <span style="color:#8b949e; font-size:13px; margin-left:12px;">{s['drafted']}/{s['target']} posts drafted</span>
    </div>
    <span style="color:{s['color']}; font-size:22px; font-weight:700;">{pct}%</span>
  </div>
  <div style="background:#0d1117; border-radius:4px; height:8px; overflow:hidden; margin-bottom:12px;">
    <div style="background:{s['color']}; width:{bar_w}%; height:100%; border-radius:4px;"></div>
  </div>
  <div style="display:flex; gap:24px; font-size:13px;">
    <span style="color:#3fb950;">Published: {s['published']}</span>
    <span style="color:#58a6ff;">Scheduled: {s['scheduled']}</span>
    <span style="color:#d29922;">Review: {s['review']}</span>
    <span style="color:#8b949e;">Draft: {s['draft']}</span>
  </div>
</div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # Content mix chart
    st.subheader("Content Mix")

    mix_data = pd.DataFrame([{
        "Series": s["name"],
        "Posts": s["drafted"],
        "Color": s["color"],
    } for s in series_stats])

    if not mix_data.empty and mix_data["Posts"].sum() > 0:
        fig_mix = px.pie(
            mix_data,
            values="Posts",
            names="Series",
            color="Series",
            color_discrete_map={s["name"]: s["color"] for s in series_stats},
        )
        fig_mix.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            margin=dict(t=20, b=20, l=20, r=20),
            height=350,
        )
        fig_mix.update_traces(textinfo="label+percent", textfont_size=12)
        st.plotly_chart(fig_mix, use_container_width=True)

    # Posting cadence
    st.subheader("Posting Cadence")
    if not scraped.empty and "date" in scraped.columns:
        scraped_sorted = scraped.dropna(subset=["date"]).sort_values("date")
        # Group by month
        scraped_sorted["month"] = scraped_sorted["date"].dt.to_period("M").astype(str)
        monthly = scraped_sorted.groupby("month").size().reset_index(name="Posts")

        fig_cadence = px.bar(
            monthly,
            x="month",
            y="Posts",
            color_discrete_sequence=["#58a6ff"],
        )
        fig_cadence.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            xaxis_title="Month",
            yaxis_title="Posts Published",
            margin=dict(t=20, b=40, l=40, r=20),
            height=300,
        )
        st.plotly_chart(fig_cadence, use_container_width=True)
    else:
        st.info("No published post data available for cadence chart.")

    # Key Insights
    total_drafted = sum(s["drafted"] for s in series_stats)
    total_target = sum(s["target"] for s in series_stats)
    total_published = sum(s["published"] for s in series_stats)
    lowest = min(series_stats, key=lambda x: x["completion_pct"])
    highest = max(series_stats, key=lambda x: x["completion_pct"])

    st.markdown(
        f"""<div style="background:#161b22; border:1px solid #30363d; border-radius:8px; padding:16px; margin-top:8px;">
<strong style="color:#58a6ff; font-size:15px;">Key Insights</strong><br>
<span style="color:#c9d1d9; font-size:14px;">
- <strong>Action:</strong> {total_drafted} posts drafted across {len(SERIES_CONFIG)} series (target: {total_target}). Overall {round((total_drafted/total_target)*100)}% complete.<br>
- <strong>Action:</strong> {highest['name']} is furthest along at {highest['completion_pct']}%. Keep momentum here — publish the backlog before drafting more.<br>
- <strong>Action:</strong> {lowest['name']} is at {lowest['completion_pct']}%. {"Prioritize drafting here if this series is strategic." if lowest["completion_pct"] < 80 else "All series are well-covered."}<br>
- <strong>Action:</strong> {total_published} posts marked as published. Update statuses as you publish to keep the pipeline accurate.<br>
</span></div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page: Performance Analytics
# ---------------------------------------------------------------------------


def page_performance_analytics():
    st.header("Performance Analytics")
    st.caption("Engagement metrics from scraped LinkedIn data.")

    scraped = load_scraped_posts()

    if scraped.empty:
        st.warning(
            "No scraped data found. Run the scraper to collect post metrics:\n\n"
            "```\npython scraper.py --report\n```"
        )
        return

    # Top-level metrics
    total_posts = len(scraped)
    total_reactions = int(scraped["reactions"].sum())
    total_comments = int(scraped["comments"].sum())
    total_impressions = int(scraped["impressions"].sum())
    avg_reactions = round(scraped["reactions"].mean())
    avg_comments = round(scraped["comments"].mean())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Posts", f"{total_posts}")
    col2.metric("Total Reactions", f"{total_reactions:,}")
    col3.metric("Total Comments", f"{total_comments:,}")
    col4.metric("Avg Reactions/Post", f"{avg_reactions}")

    st.divider()

    # Top performing posts
    st.subheader("Top Performing Posts")
    top_n = st.slider("Show top N", 5, 30, 15)
    top_posts = scraped.nlargest(top_n, "reactions")[
        ["post_text", "date", "reactions", "comments", "impressions"]
    ].copy()
    top_posts["date"] = top_posts["date"].dt.strftime("%Y-%m-%d")
    top_posts.columns = ["Post", "Date", "Reactions", "Comments", "Impressions"]
    st.dataframe(
        top_posts,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # Engagement over time
    st.subheader("Engagement Over Time")
    if "date" in scraped.columns:
        time_data = scraped.dropna(subset=["date"]).sort_values("date")
        fig_time = px.scatter(
            time_data,
            x="date",
            y="reactions",
            size="comments",
            hover_data=["post_text"],
            color_discrete_sequence=["#58a6ff"],
            size_max=20,
        )
        fig_time.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            xaxis_title="Date",
            yaxis_title="Reactions",
            margin=dict(t=20, b=40, l=40, r=20),
            height=400,
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # Reactions distribution
    st.subheader("Reactions Distribution")
    fig_hist = px.histogram(
        scraped,
        x="reactions",
        nbins=20,
        color_discrete_sequence=["#bc8cff"],
    )
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#c9d1d9",
        xaxis_title="Reactions",
        yaxis_title="Number of Posts",
        margin=dict(t=20, b=40, l=40, r=20),
        height=300,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Engagement by year
    st.subheader("Engagement by Year")
    if "date" in scraped.columns:
        yearly = scraped.dropna(subset=["date"]).copy()
        yearly["year"] = yearly["date"].dt.year
        yearly_agg = yearly.groupby("year").agg(
            posts=("reactions", "count"),
            total_reactions=("reactions", "sum"),
            avg_reactions=("reactions", "mean"),
            total_comments=("comments", "sum"),
        ).reset_index()
        yearly_agg["avg_reactions"] = yearly_agg["avg_reactions"].round(0).astype(int)

        fig_year = go.Figure()
        fig_year.add_trace(go.Bar(
            x=yearly_agg["year"],
            y=yearly_agg["total_reactions"],
            name="Total Reactions",
            marker_color="#58a6ff",
        ))
        fig_year.add_trace(go.Scatter(
            x=yearly_agg["year"],
            y=yearly_agg["avg_reactions"],
            name="Avg Reactions",
            yaxis="y2",
            mode="lines+markers",
            marker_color="#3fb950",
            line=dict(width=2),
        ))
        fig_year.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            yaxis=dict(title="Total Reactions"),
            yaxis2=dict(title="Avg Reactions", overlaying="y", side="right"),
            margin=dict(t=20, b=40, l=40, r=60),
            height=350,
            legend=dict(x=0, y=1.1, orientation="h"),
        )
        st.plotly_chart(fig_year, use_container_width=True)

        st.dataframe(
            yearly_agg.rename(columns={
                "year": "Year",
                "posts": "Posts",
                "total_reactions": "Total Reactions",
                "avg_reactions": "Avg Reactions",
                "total_comments": "Total Comments",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # Comments vs Reactions scatter
    st.subheader("Comments vs Reactions (Engagement Quality)")
    fig_cr = px.scatter(
        scraped,
        x="reactions",
        y="comments",
        hover_data=["post_text"],
        color_discrete_sequence=["#f0883e"],
        size_max=12,
    )
    fig_cr.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#c9d1d9",
        xaxis_title="Reactions",
        yaxis_title="Comments",
        margin=dict(t=20, b=40, l=40, r=20),
        height=350,
    )
    st.plotly_chart(fig_cr, use_container_width=True)

    # Key Insights
    best_post = scraped.loc[scraped["reactions"].idxmax()]
    comment_champ = scraped.loc[scraped["comments"].idxmax()]
    median_reactions = int(scraped["reactions"].median())
    posts_above_200 = len(scraped[scraped["reactions"] >= 200])

    st.markdown(
        f"""<div style="background:#161b22; border:1px solid #30363d; border-radius:8px; padding:16px; margin-top:8px;">
<strong style="color:#58a6ff; font-size:15px;">Key Insights</strong><br>
<span style="color:#c9d1d9; font-size:14px;">
- <strong>Action:</strong> Your top post "{best_post['post_text'][:50]}..." earned {int(best_post['reactions']):,} reactions. Study its structure — story-led + relatable topic = virality.<br>
- <strong>Action:</strong> {posts_above_200} posts crossed 200 reactions. Median is {median_reactions}. Posts above median share a pattern: personal story + named framework.<br>
- <strong>Action:</strong> "{comment_champ['post_text'][:50]}..." drove {int(comment_champ['comments'])} comments. High-comment posts tend to ask direct questions at the end.<br>
- <strong>Action:</strong> Average engagement is {avg_reactions} reactions and {avg_comments} comments per post. Target 200+ reactions on every new series post.<br>
</span></div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------


def main():
    st.set_page_config(
        page_title="LinkedIn Content Ops",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Password gate
    _check_auth()

    # Cloud warning banner
    if _is_cloud():
        st.markdown(
            '<div style="background:#d292221a; border:1px solid #d29922; border-radius:6px; '
            'padding:10px 14px; margin-bottom:12px; font-size:13px; color:#d29922;">'
            'Running on Streamlit Cloud. Status changes and drafts are stored in your '
            'session only and will be lost when the app restarts.</div>',
            unsafe_allow_html=True,
        )

    # Sidebar navigation
    st.sidebar.title("Content Ops")
    st.sidebar.caption("LinkedIn Growth Engine")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigate",
        [
            "Content Calendar",
            "Post Drafting",
            "Series Dashboard",
            "Performance Analytics",
        ],
        label_visibility="collapsed",
    )

    # Quick stats in sidebar
    scraped = load_scraped_posts()
    if not scraped.empty:
        st.sidebar.divider()
        st.sidebar.metric("Published Posts", len(scraped))
        st.sidebar.metric("Total Reactions", f"{int(scraped['reactions'].sum()):,}")
        st.sidebar.metric("Avg Reactions", f"{int(scraped['reactions'].mean())}")

    all_posts = get_all_series_posts()
    total_drafted = sum(len(v) for v in all_posts.values())
    st.sidebar.metric("Series Drafts", total_drafted)

    # Route to page
    if page == "Content Calendar":
        page_content_calendar()
    elif page == "Post Drafting":
        page_post_drafting()
    elif page == "Series Dashboard":
        page_series_dashboard()
    elif page == "Performance Analytics":
        page_performance_analytics()


if __name__ == "__main__":
    main()
