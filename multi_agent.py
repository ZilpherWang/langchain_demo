from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

# Define the state to track the campaign plan
class CampaignState(TypedDict):
    objective: str
    target_audience: str
    strategy: str
    content_draft: str
    feedback: List[str]
    final_plan: str

# Initialize the LLM (assuming OpenAI API key is set in environment)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Strategist Agent: Defines campaign strategy
strategist_prompt = ChatPromptTemplate.from_template(
    """You are a marketing strategist. Based on the campaign objective: '{objective}' and target audience: '{target_audience}',
    create a detailed marketing strategy. Include key messaging, channels, and tactics."""
)

def strategist_node(state: CampaignState) -> CampaignState:
    prompt = strategist_prompt.format(
        objective=state["objective"],
        target_audience=state["target_audience"]
    )
    response = llm.invoke(prompt)
    state["strategy"] = response.content
    return state

# Content Creator Agent: Generates campaign content
content_creator_prompt = ChatPromptTemplate.from_template(
    """You are a content creator. Based on the strategy: '{strategy}',
    create a draft of marketing content (e.g., social media posts, email copy, or ad copy)."""
)

def content_creator_node(state: CampaignState) -> CampaignState:
    prompt = content_creator_prompt.format(strategy=state["strategy"])
    response = llm.invoke(prompt)
    state["content_draft"] = response.content
    return state

# Reviewer Agent: Provides feedback and approves content
reviewer_prompt = ChatPromptTemplate.from_template(
    """You are a content reviewer. Review the content draft: '{content_draft}'.
    Provide constructive feedback and suggest improvements. If the content is satisfactory, mark it as approved."""
)

def reviewer_node(state: CampaignState) -> CampaignState:
    prompt = reviewer_prompt.format(content_draft=state["content_draft"])
    response = llm.invoke(prompt)
    feedback = response.content
    state["feedback"].append(feedback)
    
    # Check if content is approved
    if "approved" in feedback.lower():
        state["final_plan"] = state["content_draft"]
        return state
    else:
        # If not approved, send back to content creator
        return state

# Define the workflow
workflow = StateGraph(CampaignState)

# Add nodes
workflow.add_node("strategist", strategist_node)
workflow.add_node("content_creator", content_creator_node)
workflow.add_node("reviewer", reviewer_node)

# Define edges
workflow.set_entry_point("strategist")
workflow.add_edge("strategist", "content_creator")
workflow.add_conditional_edges(
    "reviewer",
    lambda state: "content_creator" if not state.get("final_plan") else END,
    {
        "content_creator": "content_creator",
        END: END
    }
)
workflow.add_edge("content_creator", "reviewer")

# Compile the graph
graph = workflow.compile()

# Example invocation
def run_campaign_planning(objective: str, target_audience: str) -> Dict[str, Any]:
    initial_state = CampaignState(
        objective=objective,
        target_audience=target_audience,
        strategy="",
        content_draft="",
        feedback=[],
        final_plan=""
    )
    result = graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Example usage
    result = run_campaign_planning(
        objective="Promote a new eco-friendly product",
        target_audience="Environmentally conscious consumers aged 25-40"
    )
    print("Final Campaign Plan:")
    print(result["final_plan"])