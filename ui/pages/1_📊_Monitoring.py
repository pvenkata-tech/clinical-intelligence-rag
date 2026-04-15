"""
Clinical RAG Monitoring Dashboard
Real-time query metrics, performance analysis, and observability
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.monitoring import get_monitoring_service

st.set_page_config(
    page_title="📊 Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Clinical RAG Monitoring Dashboard")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Get monitoring service
monitoring = get_monitoring_service()
stats = monitoring.get_stats()
provider_stats = monitoring.get_provider_stats()
recent_queries = monitoring.get_recent_queries(limit=100)

# ============================================================================
# METRICS ROW
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📈 Total Queries",
        stats.get("total_queries", 0),
    )

with col2:
    st.metric(
        "✅ Successful",
        stats.get("successful_queries", 0),
        delta=f"{100 - stats.get('error_rate', 0):.1f}% success"
    )

with col3:
    st.metric(
        "⏱️ Avg Latency",
        f"{stats.get('avg_latency_ms', 0):.0f}ms",
    )

with col4:
    st.metric(
        "❌ Error Rate",
        f"{stats.get('error_rate', 0):.1f}%",
    )

st.divider()

# ============================================================================
# CHARTS
# ============================================================================

col1, col2 = st.columns(2)

# Latency trend
with col1:
    st.subheader("⏱️ Latency Trend")
    if recent_queries:
        df = pd.DataFrame(recent_queries)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['latency_ms'],
            mode='lines+markers',
            name='Latency',
            line=dict(color='#3498db', width=2),
            fill='tozeroy'
        ))
        fig.update_layout(
            hovermode='x unified',
            height=350,
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No queries tracked yet")

# Provider comparison
with col2:
    st.subheader("🏭 Provider Performance")
    if provider_stats:
        providers_data = []
        for provider, data in provider_stats.items():
            providers_data.append({
                'Provider': provider,
                'Latency (ms)': data['avg_latency'],
                'Queries': data['queries']
            })
        
        df_providers = pd.DataFrame(providers_data)
        
        fig = px.bar(
            df_providers,
            x='Provider',
            y='Latency (ms)',
            color='Queries',
            title='Avg Latency by Provider',
            labels={'Latency (ms)': 'Avg Latency (ms)'}
        )
        fig.update_layout(
            height=350,
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No provider data available")

st.divider()

# ============================================================================
# PROVIDER COMPARISON TABLE
# ============================================================================

st.subheader("🧪 Provider Comparison")
if provider_stats:
    comparison_rows = []
    for provider, data in provider_stats.items():
        comparison_rows.append({
            "Provider": provider,
            "Queries": int(data['queries']),
            "Avg Latency (ms)": f"{data['avg_latency']:.1f}",
            "Avg Tokens": f"{data['avg_tokens']:.0f}",
            "Error Rate (%)": f"{data['error_rate']:.1f}",
        })
    
    df_comparison = pd.DataFrame(comparison_rows)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
else:
    st.info("Run some queries to see provider comparisons")

st.divider()

# ============================================================================
# RECENT QUERIES
# ============================================================================

st.subheader("📝 Recent Queries")
if recent_queries:
    df_queries = pd.DataFrame(recent_queries)
    
    # Display last 10 recent queries
    for idx, query in enumerate(df_queries.head(10).to_dict('records')):
        with st.expander(f"Query {idx+1} | {query['provider']} | {query['timestamp'][:16]}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Question:**")
                st.text(query['question'][:150] + "..." if len(query['question']) > 150 else query['question'])
                
                st.write("**Answer:**")
                st.text(query['answer'][:200] + "..." if len(query['answer']) > 200 else query['answer'])
            
            with col2:
                st.write("**Metrics:**")
                st.metric("Latency", f"{query['latency_ms']:.0f}ms")
                st.metric("Tokens", f"{query['token_count']}")
                st.metric("Chunks", f"{query['retrieved_chunks']}")
                
                if query['error']:
                    st.error(f"Error: {query['error'][:100]}")
else:
    st.info("No queries recorded yet. Start asking questions to see metrics here.")

st.divider()

# ============================================================================
# LANGSMITH INTEGRATION
# ============================================================================

st.subheader("🔍 LangSmith Integration")
if monitoring.langsmith_enabled:
    st.success("✅ LangSmith tracing is **ENABLED**")
    st.info(
        "📊 [View LangSmith Dashboard](https://smith.langchain.com/)\n\n"
        "All RAG queries are automatically traced. Monitor tokens, latency, and debug chain execution."
    )
else:
    st.warning("⚫ LangSmith tracing is **DISABLED**")
    st.info(
        "To enable LangSmith:\n\n"
        "1. Create account: https://smith.langchain.com\n"
        "2. Get API key\n"
        "3. Update `.env`:\n"
        "```\n"
        "LANGCHAIN_TRACING_V2=true\n"
        "LANGCHAIN_API_KEY=your-key\n"
        "```\n"
        "4. Restart the system\n\n"
        "LangSmith will then capture all chains, embeddings, and LLM calls automatically."
    )

st.divider()
st.caption("🔒 This dashboard shows local metrics. LangSmith dashboard shows LLM chain details.")
