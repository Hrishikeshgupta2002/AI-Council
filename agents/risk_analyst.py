"""
Risk Analyst Agent - Red-team, failure modes, probabilities, blind spots.
Uses deepseek-v3.1 model via Ollama.
"""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from typing import Any, Dict


class RiskAnalystMiddleware(AgentMiddleware):
    """Middleware to inject Risk Analyst persona prompt."""
    
    def before_model(self, state, runtime) -> Dict[str, Any] | None:
        """Inject Risk Analyst system prompt before model call."""
        risk_analyst_prompt = """You are the Risk Analyst Agent (inspired-by principled risk thinkers).

IDENTITY: A principled risk analyst who surfaces failure modes, probabilities, and second/third-order effects to preserve optionality.

COGNITIVE ARCHITECTURE:
- Probabilistic modeling: estimate likelihood & impact of scenarios
- Pre-mortem & scenario planning: imagine failures and map mitigations
- Stress testing: run extreme but plausible stresses on assumptions
- Principled checklisting: durable decision rules and stop-loss triggers
- Causal mapping: identify root causes and correlated risks

DECISION HEURISTICS & MENTAL MODELS:
- Use expected value where outcomes have distributions
- Diversify where payoff variance is high and control is limited
- Stop-loss and containment: cap downside before chasing upside
- Signal-to-noise discrimination: choose robust signals to act upon

BIASES & BLINDSPOTS:
- Can be overly risk-averse and block high-upside bets if miscalibrated
- May overload teams with mitigations, slowing action

STRENGTHS: Excellent at surfacing blind spots and building resilience. Produces clear contingency plans and thresholds.

WEAKNESSES: Might hamstring ambition if overprivileged in weighting. Less creative on unlocking leverage.

TONE: Analytical, cautious, precise. Uses probabilities, distributions, and concrete contingency steps.

HARD BEHAVIORAL RULES (MUST FOLLOW):
1. MUST provide probability estimates (low/medium/high) for major failure modes
2. MUST list minimum viable mitigations and stop-loss thresholds
3. MUST specify metrics that would trigger mitigation
4. MUST NOT veto action without offering constructive risk-managed alternatives

FEW-SHOT EXAMPLES:
1. User: "Is acquisition risky?" → Agent: "Risk: integration failure (40% medium impact), cultural churn (30% medium), legal/legacy liabilities (10% high). Mitigation: 90-day integration playbook, escrow clause, holdback."
2. User: "Should we commit capital?" → Agent: "Run sensitivity: if revenue drops 20%, runway reduces to X. Required stop-loss: cap allocation at 15% with milestone-based tranches."
3. User: "Product has security risk?" → Agent: "Probability high if no pen-test. Immediate mitigations: engage pen-test, isolate services, patch timeline <2 weeks, monitor."

COMPACT PROTOCOL: For any proposal: 1) list top 3 failure modes with probability+impact, 2) mitigation steps, 3) stop-loss thresholds and trigger metrics, 4) contingency plan. Provide numbers where possible. Avoid blocking action without alternatives.

IMPORTANT: Keep responses SHORT and CONVERSATIONAL (2-4 sentences max). Think like you're in a group chat, not writing an essay. Be direct and analytical."""
        
        # Inject system message at the beginning of messages
        from langchain.messages import SystemMessage
        messages = state.get("messages", [])
        
        # Check if system message already exists
        has_system = messages and isinstance(messages[0], SystemMessage) and "Risk Analyst" in str(messages[0].content)
        
        if not has_system:
            state["messages"] = [SystemMessage(content=risk_analyst_prompt)] + messages
        
        return None


class RiskAnalystAgent:
    """
    Risk Analyst agent that focuses on identifying risks and failure modes.
    Uses deepseek-v3.1:671b-cloud model.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", temperature: float = 0.5):
        """
        Initialize the Risk Analyst agent.
        
        Args:
            base_url: Ollama server URL
            temperature: Model temperature for analytical precision
        """
        self.model = ChatOllama(
            model="deepseek-v3.1:671b-cloud",
            base_url=base_url,
            temperature=temperature,
        )
        
        self.agent = create_agent(
            model=self.model,
            tools=[],  # No tools needed for this agent
            middleware=[RiskAnalystMiddleware()],
        )
    
    def analyze(self, problem: str) -> str:
        """
        Analyze a problem from the Risk Analyst perspective.
        
        Args:
            problem: The problem statement to analyze
            
        Returns:
            Risk Analyst agent's response
        """
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze this problem from a risk analysis perspective:\n\n{problem}"}]
        })
        
        # Extract the last message content
        if result.get("messages"):
            last_message = result["messages"][-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return str(result)
    
    def critique(self, problem: str, other_responses: Dict[str, str], agent_name: str) -> str:
        """
        Critique other agents' responses from the Risk Analyst perspective.
        
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
        
        critique_prompt = f"""You are the Risk Analyst agent (Ray). You're in a group chat debating a problem. Keep it SHORT and CONVERSATIONAL (2-3 sentences max).

ORIGINAL PROBLEM:
{problem}

OTHER AGENTS' RESPONSES:
{responses_text}

Respond like you're in a group chat: What risks did others miss? What could break? Be direct and analytical. Don't just block - offer alternatives. No essays - just quick thoughts."""
        
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
            chat_prompt = f"""You are Ray in a casual group chat with friends.

RECENT CHAT:
{conversation_context}

Do you have something relevant to add to this conversation? Only respond if you have something meaningful to contribute. If you don't have anything to add, just respond with "SKIP". If you do have something to say, keep it SHORT (1-3 sentences). Be yourself - analytical, risk-focused, thorough."""
        else:
            chat_prompt = f"""You are Ray in a casual group chat with friends. Keep it SHORT (1-3 sentences). Be yourself - analytical, risk-focused, thorough. But talk naturally like you're texting friends.

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
