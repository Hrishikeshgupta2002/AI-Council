"""
Synthesis Agent - Meta-agent that analyzes all 4 council agent responses
and produces structured output: summary, agreements, conflicts, blind spots, and options.
"""

"""
Synthesis Agent - Meta-agent that analyzes all 4 council agent responses
and produces structured output: summary, agreements, conflicts, blind spots, and options.
"""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from .config import Config


class SynthesisOutput(BaseModel):
    """Structured output schema for synthesis analysis."""
    
    summary: str = Field(description="Comprehensive summary of all agent responses")
    agreements: List[str] = Field(description="Key points where agents agree")
    conflicts: List[str] = Field(description="Key points where agents disagree or have conflicting views")
    blind_spots: List[str] = Field(description="Potential blind spots or areas not adequately addressed")
    final_options: List[str] = Field(description="Final 2-3 recommended options or paths forward")


class SynthesisAgent:
    """
    Meta-agent that synthesizes responses from all 4 council agents.
    Produces structured analysis of agreements, conflicts, blind spots, and recommendations.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", temperature: float = 0.6):
        """
        Initialize the Synthesis agent.
        
        Args:
            base_url: Ollama server URL
            temperature: Model temperature for balanced synthesis
        """
        self.model = ChatOllama(
            model=Config.SYNTHESIS_MODEL,
            base_url=base_url or Config.OLLAMA_BASE_URL,
            temperature=temperature or Config.SYNTHESIS_TEMPERATURE,
        )
        
        self.agent = create_agent(
            model=self.model,
            tools=[],
            response_format=ToolStrategy(SynthesisOutput),
        )
    
    def synthesize(self, problem: str, agent_responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Synthesize responses from all 4 council agents.
        
        Args:
            problem: The original problem statement
            agent_responses: Dictionary mapping agent names to their responses
            
        Returns:
            Structured synthesis output as dictionary
        """
        # Format agent responses for synthesis prompt
        responses_text = "\n\n".join([
            f"### {agent_name}\n{response}"
            for agent_name, response in agent_responses.items()
        ])
        
        synthesis_prompt = f"""Analyze and synthesize the following responses from 4 specialized agents regarding this problem:

PROBLEM:
{problem}

AGENT RESPONSES:
{responses_text}

Your task:
1. Provide a comprehensive summary of all perspectives
2. Identify key agreements across agents
3. Highlight conflicts or disagreements
4. Identify blind spots or unaddressed areas
5. Propose 2-3 final options or paths forward based on the synthesis

Be thorough, balanced, and actionable in your synthesis."""
        
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": synthesis_prompt}]
        })
        
        # Extract structured response
        if result.get("structured_response"):
            return result["structured_response"].model_dump()
        
        # Fallback if structured output not available
        if result.get("messages"):
            last_message = result["messages"][-1]
            content = last_message.content if hasattr(last_message, "content") else str(last_message)
            
            # Return as dict with content in summary
            return {
                "summary": content,
                "agreements": [],
                "conflicts": [],
                "blind_spots": [],
                "final_options": []
            }
        
        return {
            "summary": "Synthesis unavailable",
            "agreements": [],
            "conflicts": [],
            "blind_spots": [],
            "final_options": []
        }

