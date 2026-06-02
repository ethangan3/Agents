import os

import requests
import streamlit as st


AGENT_OPTIONS = {
    "ReAct": "react",
    "Plan-and-Solve": "plan-solve",
    "Reflection": "reflection",
}


def render_step(step: dict):
    title = f"Step {step.get('step_id', '-')}: {step.get('action') or 'No action'}"
    with st.expander(title, expanded=True):
        if step.get("thought"):
            st.markdown("**Thought**")
            st.write(step["thought"])
        if step.get("action_input") is not None:
            st.markdown("**Action Input**")
            st.code(str(step["action_input"]), language="text")
        if step.get("observation"):
            st.markdown("**Observation**")
            st.write(step["observation"])
        if step.get("error"):
            st.markdown("**Error**")
            st.error(step["error"])


def call_agent(api_base_url: str, agent_type: str, question: str, max_steps: int):
    response = requests.post(
        f"{api_base_url.rstrip('/')}/v1/agents/{agent_type}/run",
        json={
            "question": question,
            "max_steps": max_steps,
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


st.set_page_config(
    page_title="MiniAgent Runtime",
    layout="wide",
)

st.title("MiniAgent Runtime")

with st.sidebar:
    api_base_url = st.text_input(
        "API URL",
        value=os.getenv("MINI_AGENT_API_URL", "http://localhost:8000"),
    )
    agent_label = st.selectbox("Agent", options=list(AGENT_OPTIONS.keys()))
    max_steps = st.number_input("Max steps", min_value=1, max_value=20, value=6)

question = st.text_area(
    "Question",
    value="计算 12 * 8，然后告诉我当前时间",
    height=120,
)

run_clicked = st.button("Run", type="primary", use_container_width=True)

if run_clicked:
    if not question.strip():
        st.warning("请输入问题。")
    else:
        with st.spinner("Agent is running..."):
            try:
                result = call_agent(
                    api_base_url=api_base_url,
                    agent_type=AGENT_OPTIONS[agent_label],
                    question=question.strip(),
                    max_steps=int(max_steps),
                )
            except requests.RequestException as exc:
                st.error(f"请求失败: {exc}")
            else:
                status = result.get("status", "unknown")
                col_status, col_latency, col_run = st.columns([1, 1, 2])
                col_status.metric("Status", status)
                col_latency.metric("Latency", f"{result.get('latency_ms', 0)} ms")
                col_run.code(result.get("run_id", ""), language="text")

                st.subheader("Answer")
                if result.get("answer"):
                    st.write(result["answer"])
                else:
                    st.info("No final answer.")

                if result.get("error"):
                    st.error(result["error"])

                st.subheader("Trace")
                steps = result.get("steps", [])
                if not steps:
                    st.info("No steps recorded.")
                for step in steps:
                    render_step(step)
