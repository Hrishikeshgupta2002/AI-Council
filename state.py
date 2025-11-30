"""
State management for the Agentic Council System.
Defines custom AgentState schema to track problem statements, agent responses,
synthesis output, and final decisions.
"""

"""
State management for the Agentic Council System.
Defines custom AgentState schema to track problem statements, agent responses,
synthesis output, and final decisions.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain.agents import AgentState


class CouncilState(AgentState):
    """
    Extended AgentState for the council system.
    Tracks the full conversation flow from problem statement to final decision.
    """
    
    # Problem statement from user
    problem_statement: str
    
    # Individual agent responses (parallel responses from STEP 2)
    agent_responses: Dict[str, str]
    
    # Debate/critique rounds (group chat style discussions)
    debate_rounds: List[Dict[str, Any]]  # Each round contains agent critiques and responses
    
    # Synthesis agent output (from STEP 3)
    synthesis_output: Optional[Dict[str, Any]]
    
    # Final decision with weighted recommendation (from STEP 4)
    final_decision: Optional[Dict[str, Any]]
    
    # Protocol step tracking
    current_step: int  # 1 = Broadcast, 2 = Parallel Responses, 2.5 = Debate, 3 = Synthesis, 4 = Final Decision
    
    # Additional metadata
    metadata: Dict[str, Any]

