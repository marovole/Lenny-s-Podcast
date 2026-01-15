"""
Lenny's Podcast Analyzer - Streamlit Frontend.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from src.processor import parse_transcript, process_all_transcripts
from src.search import PodcastSearch
from src.taxonomy import (
    TOPICS, FAILURE_PATTERNS, FRAMEWORKS, 
    INTERVIEW_CATEGORIES, classify_text
)
from src.insights import InsightExtractor

# Page config
st.set_page_config(
    page_title="Lenny's Podcast Analyzer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'search_engine' not in st.session_state:
    st.session_state.search_engine = None
if 'transcripts_loaded' not in st.session_state:
    st.session_state.transcripts_loaded = False


@st.cache_resource
def load_search_index():
    """Load the search index (cached)."""
    engine = PodcastSearch()
    engine.load_index('data/search')
    return engine


def load_insights():
    """Load extracted insights."""
    insights_dir = Path('data/insights')
    if not insights_dir.exists():
        return None
    
    insights = []
    for file in insights_dir.glob('*_insights.json'):
        with open(file, 'r', encoding='utf-8') as f:
            insights.append(json.load(f))
    return insights


def main():
    # Sidebar
    st.sidebar.title("🎙️ Lenny's Podcast")
    st.sidebar.markdown("**320期播客转录分析**")
    
    # Navigation
    page = st.sidebar.selectbox(
        "导航",
        ["搜索", "主题浏览", "Failure Playbook", "框架库", "面试题库", "嘉宾列表"]
    )
    
    # Load search engine
    if st.session_state.search_engine is None:
        with st.spinner("加载索引中..."):
            st.session_state.search_engine = load_search_index()
    
    # Main content
    if page == "搜索":
        search_page()
    elif page == "主题浏览":
        browse_page()
    elif page == "Failure Playbook":
        failure_page()
    elif page == "框架库":
        framework_page()
    elif page == "面试题库":
        interview_page()
    elif page == "嘉宾列表":
        speakers_page()


def search_page():
    """Semantic search page."""
    st.title("🔍 语义搜索")
    st.markdown("用自然语言搜索播客内容")
    
    query = st.text_input("搜索问题", placeholder="例如：如何做好产品定价？")
    
    if query and st.session_state.search_engine:
        with st.spinner("搜索中..."):
            results = st.session_state.search_engine.search(query, k=10)
        
        st.markdown(f"**找到 {len(results)} 条相关结果**")
        
        for r in results:
            with st.expander(f"#{r['rank']} [{r['episode_name']}] {r['speaker']} ({r['timestamp']})"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(r['content'])
                with col2:
                    st.metric("相关度", f"{r['score']:.2f}")
    
    # Quick queries
    st.markdown("---")
    st.markdown("**快速查询：**")
    quick_queries = [
        "如何做好产品经理？",
        "增长的最佳实践",
        "领导力的关键要素",
        "如何应对失败？",
        "面试 PM 最好的问题"
    ]
    
    cols = st.columns(5)
    for i, q in enumerate(quick_queries):
        if cols[i % 5].button(q, key=f"quick_{i}"):
            st.query_params.q = q
            st.rerun()


def browse_page():
    """Browse by topics."""
    st.title("📚 主题浏览")
    
    # Topic selection
    topic = st.selectbox(
        "选择主题",
        options=list(TOPICS.keys()),
        format_func=lambda x: TOPICS[x]['name']
    )
    
    if topic:
        st.markdown(f"**关键词：** {', '.join(TOPICS[topic]['keywords'])}")
        
        # Search for this topic
        if st.session_state.search_engine:
            results = st.session_state.search_engine.search(
                TOPICS[topic]['keywords'][0], k=20
            )
            
            st.markdown(f"**找到 {len(results)} 条相关内容**")
            
            for r in results:
                with st.expander(f"[{r['episode_name']}] {r['speaker']}"):
                    st.markdown(r['content'])


def failure_page():
    """Failure playbook page."""
    st.title("📕 Failure Playbook")
    st.markdown("从失败中学习的最佳实践")
    
    # Failure pattern selection
    pattern = st.selectbox(
        "失败类型",
        options=list(FAILURE_PATTERNS.keys()),
        format_func=lambda x: FAILURE_PATTERNS[x]['name']
    )
    
    if pattern:
        st.markdown(f"**典型案例：**")
        for example in FAILURE_PATTERNS[pattern]['examples']:
            st.markdown(f"- {example}")
        
        # Search for failure stories
        if st.session_state.search_engine:
            search_term = FAILURE_PATTERNS[pattern]['examples'][0]
            results = st.session_state.search_engine.search(
                f"failure mistake {search_term}", k=10
            )
            
            st.markdown("---")
            st.markdown("**相关失败案例：**")
            
            for r in results:
                if 'fail' in r['content'].lower() or 'mistake' in r['content'].lower():
                    with st.expander(f"[{r['episode_name']}] {r['speaker']}"):
                        st.markdown(r['content'])


def framework_page():
    """Decision frameworks page."""
    st.title("🧠 决策框架库")
    st.markdown("从播客嘉宾那里学到的决策框架")
    
    # Framework categories
    framework_tabs = st.tabs(list(FRAMEWORKS.keys()))
    
    for i, (fid, f) in enumerate(FRAMEWORKS.items()):
        with framework_tabs[i]:
            st.subheader(f"【{f['name']}】")
            st.markdown(f"**来源：** {f['source']}")
            st.markdown(f"**描述：** {f['description']}")
            if 'template' in f:
                st.info(f"**模板：** {f['template']}")
            if 'example' in f:
                st.markdown(f"**案例：** {f['example']}")


def interview_page():
    """Interview questions page."""
    st.title("📝 面试题库")
    st.markdown("从播客嘉宾那里收集的最佳面试问题")
    
    category = st.selectbox(
        "面试类型",
        options=list(INTERVIEW_CATEGORIES.keys()),
        format_func=lambda x: INTERVIEW_CATEGORIES[x]['name']
    )
    
    if category:
        for i, q in enumerate(INTERVIEW_CATEGORIES[category]['questions']):
            with st.expander(f"Q{i+1}: {q}"):
                st.markdown("**考察要点：**")
                st.markdown("- 候选人是否具备相关经验")
                st.markdown("- 问题解决能力")
                st.markdown("- 沟通表达能力")
        
        # Search for more interview questions
        if st.session_state.search_engine:
            st.markdown("---")
            st.markdown("**更多来自播客的面试问题：**")
            
            results = st.session_state.search_engine.search(
                "interview question favorite ask candidate", k=10
            )
            
            for r in results:
                if 'interview' in r['content'].lower() or 'question' in r['content'].lower():
                    with st.expander(f"[{r['episode_name']}] {r['speaker']}"):
                        st.markdown(r['content'])


def speakers_page():
    """Guest speakers page."""
    st.title("👥 嘉宾列表")
    
    if st.session_state.search_engine:
        speakers = st.session_state.search_engine.get_speaker_list()
        
        # Search for specific speaker
        search_name = st.text_input("搜索嘉宾")
        if search_name:
            speakers = {k: v for k, v in speakers.items() 
                       if search_name.lower() in k.lower()}
        
        # Display in columns
        cols = st.columns(3)
        for i, (speaker, count) in enumerate(list(speakers.items())[:50]):
            with cols[i % 3]:
                st.markdown(f"**{speaker}**")
                st.caption(f"出现 {count} 次")
        
        if len(speakers) > 50:
            st.markdown(f"... 还有 {len(speakers) - 50} 位嘉宾")


if __name__ == '__main__':
    main()
