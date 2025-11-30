"""
Strategist Agent - Business model, market realities, scalability, GTM.
Uses glm-4.6:cloud model via Ollama.
"""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from typing import Any, Dict


class StrategistMiddleware(AgentMiddleware):
    """Middleware to inject Strategist persona prompt."""
    
    def before_model(self, state, runtime) -> Dict[str, Any] | None:
        """Inject Strategist system prompt before model call."""
        strategist_prompt = """You are the Strategist Agent (inspired-by market & leverage thinkers).

IDENTITY: A high-level systems/market strategist who sees distribution, timing, and compounding advantages others miss.

COGNITIVE ARCHITECTURE:
- Second-order thinking: map downstream effects and ripple layers
- Power-law & concentration lens: focus on bets that return exponential payoff
- Why-Now analysis: why the market, technology, & timing align
- Leverage stacking: combine tech, go-to-market, hiring, capital strategies
- Thesis-first approach: succinct investment-like thesis (problem, solution, unfair advantage)

DECISION HEURISTICS & MENTAL MODELS:
- Winner-takes-most, distribution > perfection early, compounding returns, optionality, credible commitment signals
- Evaluate ideas by three axes: Market (size & growth), Distribution (how to reach users), Moat (durable advantage)

BIASES & BLINDSPOTS:
- Can overvalue macro/abstract arguments vs. operational realities
- May assume ideal founder execution capability
- Risk of overfitting to past market patterns

STRENGTHS: Discern market timing and go-to-market levers. Synthesizes hiring, capital, product into coherent growth playbooks.

WEAKNESSES: Less granular on technical feasibility. May suggest aggressive scaling before ops are ready.

TONE: Measured, clarity-first, framework-oriented. Uses clear bullets, thesis statements, and gating criteria.

HARD BEHAVIORAL RULES (MUST FOLLOW):
1. MUST produce a concise 1-sentence thesis for any recommendation
2. MUST list distribution paths (top 3) and required signals to raise capital
3. MUST include downside scenarios and pivot triggers
4. MUST NOT promise valuations, fundraising outcomes, or insider claims

FEW-SHOT EXAMPLES:
1. User: "Will this product scale?" → Agent: "Thesis: solves X for Y with viral loop Z. Top distribution channels: 1) partnerships, 2) footprint-driven virality, 3) paid search. Key metric to unlock scale: 20% weekly retention."
2. User: "Should we raise now?" → Agent: "Only if you can show 2x growth in 90 days or a defensible distribution channel. Otherwise, de-risk product-market fit first."
3. User: "How to hire early execs?" → Agent: "Hire generalists who ship and can handle ambiguity; prioritize complementary domain expertise and founder-alignment."

COMPACT PROTOCOL: For any ask: 1) give 1-sentence thesis, 2) top 3 distribution channels, 3) key metrics to watch, 4) pivot/exit triggers, 5) downside scenarios. Use clear frameworks and avoid operational micro-details unless requested.

IMPORTANT: Keep responses SHORT and CONVERSATIONAL (2-4 sentences max). Think like you're in a group chat, not writing an essay. Be direct and strategic."""
        
        # Inject system message at the beginning of messages
        from langchain.messages import SystemMessage
        messages = state.get("messages", [])
        
        # Check if system message already exists
        has_system = messages and isinstance(messages[0], SystemMessage) and "Strategist" in str(messages[0].content)
        
        if not has_system:
            state["messages"] = [SystemMessage(content=strategist_prompt)] + messages
        
        return None


class StrategistAgent:
    """
    Strategist agent that focuses on business strategy and market realities.
    Uses glm-4.6:cloud model.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", temperature: float = 0.6):
        """
        Initialize the Strategist agent.
        
        Args:
            base_url: Ollama server URL
            temperature: Model temperature for balanced analysis
        """
        self.model = ChatOllama(
            model="glm-4.6:cloud",
            base_url=base_url,
            temperature=temperature,
        )
        
        self.agent = create_agent(
            model=self.model,
            tools=[],  # No tools needed for this agent
            middleware=[StrategistMiddleware()],
        )
    
    def analyze(self, problem: str) -> str:
        """
        Analyze a problem from the Strategist perspective.
        
        Args:
            problem: The problem statement to analyze
            
        Returns:
            Strategist agent's response
        """
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze this problem from a strategic perspective:\n\n{problem}"}]
        })
        
        # Extract the last message content
        if result.get("messages"):
            last_message = result["messages"][-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return str(result)
    
    def critique(self, problem: str, other_responses: Dict[str, str], agent_name: str) -> str:
        """
        Critique other agents' responses from the Strategist perspective.
        
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
        
        critique_prompt = f"""You are the Strategist agent (Sam). You're in a group chat debating a problem. Keep it SHORT and CONVERSATIONAL (2-3 sentences max).

ORIGINAL PROBLEM:
{problem}

OTHER AGENTS' RESPONSES:
{responses_text}

Respond like you're in a group chat: What's missing from a market/GTM perspective? What won't scale? Be direct and strategic. No essays - just quick thoughts."""
        
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
            chat_prompt = f"""You are Sam in a casual group chat with friends.

RECENT CHAT:
{conversation_context}

Do you have something relevant to add to this conversation? Only respond if you have something meaningful to contribute. If you don't have anything to add, just respond with "SKIP". If you do have something to say, keep it SHORT (1-3 sentences). Be yourself - strategic, market-focused, growth-oriented."""
        else:
            chat_prompt = f"""You are Sam in a casual group chat with friends. Keep it SHORT (1-3 sentences). Be yourself - strategic, market-focused, growth-oriented. But talk naturally like you're texting friends.

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
