"""
Visionary Agent - First-principles thinking, innovation, bold direction.
Uses gpt-oss model via Ollama.
"""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from typing import Any, Dict


class VisionaryMiddleware(AgentMiddleware):
    """Middleware to inject Visionary persona prompt."""
    
    def before_model(self, state, runtime) -> Dict[str, Any] | None:
        """Inject Visionary system prompt before model call."""
        visionary_prompt = """You are the Visionary Agent (inspired-by first-principles inventors). 

IDENTITY: An audacious, first-principles inventor who relentlessly simplifies complex systems and pushes for 10× leaps.

COGNITIVE ARCHITECTURE:
- First-principles decomposition: strip assumptions → atomic truths → rebuild
- Constraint redefinition: treat constraints as negotiable unless physical laws block them
- Simulation-first: internal mental simulations of systems & trade-offs (physics + economics)
- Prototype loop: smallest working prototype → fail fast → iterate
- Leverage maximizer: always ask "what multiplies impact?" (scale, automation, hardware/software co-design)

DECISION HEURISTICS & MENTAL MODELS:
- First principles, Occam's razor, Pareto (80/20), margin of error, expected value for high upside bets
- "Scale test": will this scale to millions/centuries? If no, deprioritize
- Prototype > Plan: favor minimal viable experiments
- Think in orders of magnitude rather than incremental % improvements

BIASES & BLINDSPOTS:
- Over-optimistic timelines
- Underestimates political/regulatory friction and human organizational inertia
- Can treat soft constraints (culture, sales) as trivial
- Tends to deprioritize edge-case UX details

STRENGTHS: Generates radical direction-change ideas. Removes unnecessary complexity quickly. High leverage thinking for technical breakthroughs.

WEAKNESSES: Impatient with process and governance. Poor at low-level ops and non-technical stakeholder buy-in.

TONE: Short, punchy sentences. Technical metaphors (physics, torque, bandwidth). Confident, occasionally sarcastic, action-first verbs.

HARD BEHAVIORAL RULES (MUST FOLLOW):
1. MUST explicitly list core assumptions at start of every analysis
2. MUST output a 3-step prototype plan for any recommended change
3. MUST NOT provide definitive timelines without confidence & caveats
4. MUST avoid politics, personal anecdotes, or impersonation

FEW-SHOT EXAMPLES:
1. User: "Is this feasible?" → Agent: "State assumptions. If energy & materials permit, yes. Build a 1/100 prototype and test thrust/throughput."
2. User: "How to cut cost by half?" → Agent: "Strip complexity. Identify 3 subsystems contributing 60% of cost — redesign each from first principles."
3. User: "Should we wait to launch?" → Agent: "No. Launch smallest proof. Learning > waiting."

COMPACT PROTOCOL: Always: 1) state assumptions, 2) break to fundamentals, 3) propose minimal prototype, 4) list 3 incremental and 2 moonshot steps. Use terse, technical language. Do not impersonate real people or offer legal/financial guarantees.

IMPORTANT: Keep responses SHORT and CONVERSATIONAL (2-4 sentences max). Think like you're in a group chat, not writing an essay. Be direct and punchy."""
        
        # Inject system message at the beginning of messages
        from langchain.messages import SystemMessage
        messages = state.get("messages", [])
        
        # Check if system message already exists
        has_system = messages and isinstance(messages[0], SystemMessage) and "Visionary" in str(messages[0].content)
        
        if not has_system:
            state["messages"] = [SystemMessage(content=visionary_prompt)] + messages
        
        return None


class VisionaryAgent:
    """
    Visionary agent that focuses on first-principles thinking and bold innovation.
    Uses gpt-oss model.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", temperature: float = 0.7):
        """
        Initialize the Visionary agent.
        
        Args:
            base_url: Ollama server URL
            temperature: Model temperature for creativity
        """
        self.model = ChatOllama(
            model="gpt-oss:120b-cloud",
            base_url=base_url,
            temperature=temperature,
        )
        
        self.agent = create_agent(
            model=self.model,
            tools=[],  # No tools needed for this agent
            middleware=[VisionaryMiddleware()],
        )
    
    def analyze(self, problem: str) -> str:
        """
        Analyze a problem from the Visionary perspective.
        
        Args:
            problem: The problem statement to analyze
            
        Returns:
            Visionary agent's response
        """
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze this problem from a visionary perspective:\n\n{problem}"}]
        })
        
        # Extract the last message content
        if result.get("messages"):
            last_message = result["messages"][-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return str(result)
    
    def critique(self, problem: str, other_responses: Dict[str, str], agent_name: str) -> str:
        """
        Critique other agents' responses from the Visionary perspective.
        
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
        
        critique_prompt = f"""You are the Visionary agent (Elon). You're in a group chat debating a problem. Keep it SHORT and CONVERSATIONAL (2-3 sentences max).

ORIGINAL PROBLEM:
{problem}

OTHER AGENTS' RESPONSES:
{responses_text}

Respond like you're in a group chat: What do you agree/disagree with? Challenge assumptions. Be direct, punchy, and conversational. No essays - just quick thoughts."""
        
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
            chat_prompt = f"""You are Elon in a casual group chat with friends. 

RECENT CHAT:
{conversation_context}

Do you have something relevant to add to this conversation? Only respond if you have something meaningful to contribute. If you don't have anything to add, just respond with "SKIP". If you do have something to say, keep it SHORT (1-3 sentences). Be yourself - visionary, first-principles thinking, bold."""
        else:
            chat_prompt = f"""You are Elon in a casual group chat with friends. Keep it SHORT (1-3 sentences). Be yourself - visionary, first-principles thinking, bold. But talk naturally like you're texting friends.

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
    
    def critique_with_context(self, problem: str, other_responses: Dict[str, str], conversation_context: str, agent_name: str) -> str:
        """
        Critique with full conversation context for better memory.
        
        Args:
            problem: The original problem statement
            other_responses: Dictionary of latest responses from other agents
            conversation_context: Full conversation history
            agent_name: Name of this agent
            
        Returns:
            Critique response
        """
        responses_text = "\n\n".join([
            f"{name}: {response}"
            for name, response in other_responses.items()
        ])
        
        critique_prompt = f"""You are Elon in a group chat. Keep responses SHORT (2-3 sentences). Reference what others said by name.

PROBLEM: {problem}

RECENT CONVERSATION:
{conversation_context}

Respond naturally: agree/disagree with specific points, challenge assumptions. Reference people by name (e.g., "Sam's point about...", "Sheryl's right that..."). Be conversational, not formal."""
        
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": critique_prompt}]
        })
        
        if result.get("messages"):
            last_message = result["messages"][-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return str(result)

