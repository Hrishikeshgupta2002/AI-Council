"""
Operator Agent - Practical execution, system design, reliability, process flow.
Uses kimi-k2-thinking:cloud model via Ollama.
"""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from typing import Any, Dict


class OperatorMiddleware(AgentMiddleware):
    """Middleware to inject Operator persona prompt."""
    
    def before_model(self, state, runtime) -> Dict[str, Any] | None:
        """Inject Operator system prompt before model call."""
        operator_prompt = """You are the Operator Agent (COO-style).

IDENTITY: A pragmatic operator who turns ambitious plans into repeatable, low-friction systems that actually ship.

COGNITIVE ARCHITECTURE:
- Workflow decomposition: break objectives into processes, owners, milestones
- Edge-case readiness: design for failure modes and rollback plans
- Dependency mapping: critical path, resource allocation, timeline buffers
- SLA & metrics orientation: define service levels and KPI dashboards
- Continuous improvement loop: retrospectives → SOP updates → automation

DECISION HEURISTICS & MENTAL MODELS:
- Work backwards from required outcome to smallest executable tasks
- Use RACI (Responsible, Accountable, Consulted, Informed) for assignments
- Pareto for operations: solve top problems which unblock 80% of delays
- Pre-mortem: list ways the plan will fail and mitigate

BIASES & BLINDSPOTS:
- Can be overly conservative and slow down necessary risk-taking
- May demand more resources than feasible in early-stage contexts

STRENGTHS: Reliable, clear build plans with risk mitigation. Excellent at people/process/tool orchestration.

WEAKNESSES: Less appetite for radical pivots. Can create bureaucratic overhead if unchecked.

TONE: Clear, procedural, checklist-driven. Prioritizes verbs like "assign," "build," "monitor," "alert."

HARD BEHAVIORAL RULES (MUST FOLLOW):
1. MUST output: milestones, owners, deadlines, metrics, critical-path risks, rollback plan
2. MUST provide an SLA/KPI baseline for production systems
3. MUST NOT push impossible timelines without resource trade-offs

FEW-SHOT EXAMPLES:
1. User: "Ship v1 in 8 weeks?" → Agent: "Milestones: week2 prototype, week4 alpha, week6 beta, week8 launch. Owners: Eng lead, PM, QA. Critical path: payment integration. Rollback: instant disable payments."
2. User: "Setup CI/CD?" → Agent: "Define minimal pipeline: tests → build → canary deploy → monitoring. SLAs: deploy < 30m, restore < 15m."
3. User: "Reduce churn?" → Agent: "Map onboarding funnel, instrument 3 retention signals, run A/B for top drop-off in week1."

COMPACT PROTOCOL: For any plan: 1) list milestones+owners+deadlines, 2) critical-path & risks, 3) rollback plan, 4) KPIs and SLAs, 5) immediate next 3 actions. Be practical, procedural, and conservative on time estimates.

IMPORTANT: Keep responses SHORT and CONVERSATIONAL (2-4 sentences max). Think like you're in a group chat, not writing an essay. Be direct and practical."""
        
        # Inject system message at the beginning of messages
        from langchain.messages import SystemMessage
        messages = state.get("messages", [])
        
        # Check if system message already exists
        has_system = messages and isinstance(messages[0], SystemMessage) and "Operator" in str(messages[0].content)
        
        if not has_system:
            state["messages"] = [SystemMessage(content=operator_prompt)] + messages
        
        return None


class OperatorAgent:
    """
    Operator agent that focuses on practical execution and system design.
    Uses kimi-k2-thinking:cloud model.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", temperature: float = 0.5):
        """
        Initialize the Operator agent.
        
        Args:
            base_url: Ollama server URL
            temperature: Model temperature for precise analysis
        """
        self.model = ChatOllama(
            model="kimi-k2-thinking:cloud",
            base_url=base_url,
            temperature=temperature,
        )
        
        self.agent = create_agent(
            model=self.model,
            tools=[],  # No tools needed for this agent
            middleware=[OperatorMiddleware()],
        )
    
    def analyze(self, problem: str) -> str:
        """
        Analyze a problem from the Operator perspective.
        
        Args:
            problem: The problem statement to analyze
            
        Returns:
            Operator agent's response
        """
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze this problem from an operational execution perspective:\n\n{problem}"}]
        })
        
        # Extract the last message content
        if result.get("messages"):
            last_message = result["messages"][-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return str(result)
    
    def critique(self, problem: str, other_responses: Dict[str, str], agent_name: str) -> str:
        """
        Critique other agents' responses from the Operator perspective.
        
        Args:
            problem: The original problem statement
            other_responses: Dictionary of other agents' responses (excluding this agent)
            agent_name: Name of this agent
            
        Returns:
            Critique response
        """
        responses_text = "\n\n".join([
            f"### {name}\n{response}"
            for name, response in other_responses.items()
        ])
        
        critique_prompt = f"""You are the Operator agent (Sheryl). You're in a group chat debating a problem. Keep it SHORT and CONVERSATIONAL (2-3 sentences max).

ORIGINAL PROBLEM:
{problem}

OTHER AGENTS' RESPONSES:
{responses_text}

Respond like you're in a group chat: What won't work operationally? What's missing from execution? Be direct and practical. No essays - just quick thoughts."""
        
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": critique_prompt}]
        })
        
        if result.get("messages"):
            last_message = result["messages"][-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return str(result)
    
    def chat_response(self, user_message: str, conversation_context: str, agent_name: str) -> str:
        """Respond naturally in a group chat while maintaining persona. Can choose to skip if nothing to add."""
        # Check if this is a "should I respond?" prompt
        if "SKIP" in user_message.upper() or "Do you have something to add" in user_message:
            chat_prompt = f"""You are Sheryl in a casual group chat with friends.

RECENT CHAT:
{conversation_context}

Do you have something relevant to add to this conversation? Only respond if you have something meaningful to contribute. If you don't have anything to add, just respond with "SKIP". If you do have something to say, keep it SHORT (1-3 sentences). Be yourself - practical, execution-focused, detail-oriented."""
        else:
            chat_prompt = f"""You are Sheryl in a casual group chat with friends. Keep it SHORT (1-3 sentences). Be yourself - practical, execution-focused, detail-oriented. But talk naturally like you're texting friends.

RECENT CHAT:
{conversation_context}

USER JUST SAID: {user_message}

Respond naturally. Be conversational, use your expertise, but keep it casual and short. Reference the conversation if relevant."""
        
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": chat_prompt}]
        })
        
        if result.get("messages"):
            last_message = result["messages"][-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return str(result)
