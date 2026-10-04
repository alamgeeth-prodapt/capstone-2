from langgraph.graph import StateGraph, START, END

from langgraph_state import AgentState
from supervisor import supervisor

from workers.network_diagnostics_worker import network_diagnostics_worker
from workers.billing_resolution_worker import billing_resolution_worker
from workers.network_analytics_worker import network_analytics_worker
from workers.policy_rag_worker import policy_rag_worker
from workers.customer_comms_worker import customer_comms_worker


def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("supervisor", supervisor)
    graph.add_node(
        "network_diagnostics_adk",
        network_diagnostics_worker,
    )
    graph.add_node(
        "billing_resolution_adk",
        billing_resolution_worker,
    )
    graph.add_node(
        "network_analytics",
        network_analytics_worker,
    )
    graph.add_node(
        "policy_rag",
        policy_rag_worker,
    )
    graph.add_node(
        "customer_comms_crew",
        customer_comms_worker,
    )

    # Start
    graph.add_edge(START, "supervisor")

    # Supervisor decides next worker
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "network_diagnostics_adk": "network_diagnostics_adk",
            "billing_resolution_adk": "billing_resolution_adk",
            "network_analytics": "network_analytics",
            "policy_rag": "policy_rag",
            "customer_comms_crew": "customer_comms_crew",
            "finish": END,
        },
    )

    # Specialist workers return to supervisor
    graph.add_edge(
        "network_diagnostics_adk",
        "supervisor",
    )

    graph.add_edge(
        "billing_resolution_adk",
        "supervisor",
    )

    graph.add_edge(
        "network_analytics",
        "supervisor",
    )

    graph.add_edge(
        "policy_rag",
        "supervisor",
    )

    # CrewAI produces the final response
    graph.add_edge(
        "customer_comms_crew",
        END,
    )

    return graph.compile()


graph = build_graph()