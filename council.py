"""
Council Orchestrator - Manages the 4-step council protocol:
1. Broadcast problem to all agents
2. Collect parallel responses
3. Synthesis agent analysis
4. Weighted decision model
"""

"""
Council Orchestrator - Manages the 4-step council protocol and group chat interactions.
"""

import concurrent.futures
import time
from typing import Dict, Any, Optional, List

try:
    from .state import CouncilState
    from .agents import VisionaryAgent, StrategistAgent, OperatorAgent, RiskAnalystAgent
    from .synthesis import SynthesisAgent
    from .config import Config
except ImportError:
    # For direct execution
    from state import CouncilState
    from agents import VisionaryAgent, StrategistAgent, OperatorAgent, RiskAnalystAgent
    from synthesis import SynthesisAgent
    from config import Config


class CouncilOrchestrator:
    """
    Orchestrates the 4-agent council system following the 4-step protocol.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        use_weighted_model: Optional[bool] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the Council Orchestrator.
        
        Args:
            base_url: Ollama server URL (defaults to Config.OLLAMA_BASE_URL)
            use_weighted_model: Use weighted model (defaults to Config.USE_WEIGHTED_MODEL)
            custom_weights: Custom weights for agents (optional)
        """
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.use_weighted_model = use_weighted_model if use_weighted_model is not None else Config.USE_WEIGHTED_MODEL
        
        # Initialize all agents
        self.visionary = VisionaryAgent(base_url=base_url)
        self.strategist = StrategistAgent(base_url=base_url)
        self.operator = OperatorAgent(base_url=base_url)
        self.risk_analyst = RiskAnalystAgent(base_url=base_url)
        
        # Initialize synthesis agent
        self.synthesis = SynthesisAgent(base_url=base_url)
        
        # Set weights
        if custom_weights:
            self.weights = {**Config.AGENT_WEIGHTS, **custom_weights}
        else:
            self.weights = Config.AGENT_WEIGHTS.copy()
    
    def step_1_broadcast(self, problem: str) -> CouncilState:
        """
        STEP 1: Broadcast problem to all 4 agents.
        Creates initial state with problem statement.
        
        Args:
            problem: Problem statement to broadcast
            
        Returns:
            Initial council state
        """
        state = CouncilState(
            problem_statement=problem,
            agent_responses={},
            debate_rounds=[],
            synthesis_output=None,
            final_decision=None,
            current_step=1,
            metadata={},
            messages=[]  # Required by AgentState
        )
        return state
    
    def step_2_parallel_responses(self, state: CouncilState, verbose: bool = True) -> CouncilState:
        """
        STEP 2: Collect parallel responses from all 4 agents.
        Agents respond independently and simultaneously.
        
        Args:
            state: Current council state
            verbose: Whether to print progress updates
            
        Returns:
            Updated state with agent responses
        """
        problem = state["problem_statement"]
        start_time = time.time()
        
        if verbose:
            print("\n📡 STEP 2: Collecting parallel responses from all agents...")
            print("   └─ Starting parallel analysis...")
        
        # Collect responses in parallel for efficiency
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            if verbose:
                print("   ├─ 🤖 Visionary agent analyzing...")
            future_visionary = executor.submit(self.visionary.analyze, problem)
            
            if verbose:
                print("   ├─ 🤖 Strategist agent analyzing...")
            future_strategist = executor.submit(self.strategist.analyze, problem)
            
            if verbose:
                print("   ├─ 🤖 Operator agent analyzing...")
            future_operator = executor.submit(self.operator.analyze, problem)
            
            if verbose:
                print("   └─ 🤖 Risk Analyst agent analyzing...")
            
            future_risk_analyst = executor.submit(self.risk_analyst.analyze, problem)
            
            # Agent name mapping to normal names
            agent_name_mapping = {
                "Visionary": "Elon",
                "Strategist": "Sam",
                "Operator": "Sheryl",
                "Risk Analyst": "Ray"
            }
            
            # Wait for all responses with progress updates
            agent_responses = {}
            futures = {
                "Visionary": future_visionary,
                "Strategist": future_strategist,
                "Operator": future_operator,
                "Risk Analyst": future_risk_analyst,
            }
            
            # Monitor completion with real-time updates
            completed = set()
            agent_times = {}
            agent_starts = {name: time.time() for name in futures.keys()}
            
            # Use as_completed to show progress as agents finish
            import sys
            for future in concurrent.futures.as_completed(futures.values()):
                # Find which agent this future belongs to
                agent_role = None
                for name, f in futures.items():
                    if f == future:
                        agent_role = name
                        break
                
                if agent_role:
                    agent_start = agent_starts[agent_role]
                    agent_display_name = agent_name_mapping.get(agent_role, agent_role)
                    try:
                        result = future.result()
                        # Store with normal name for display
                        agent_responses[agent_display_name] = result
                        # Also keep role name for internal use
                        agent_responses[agent_role] = result
                        completed.add(agent_role)
                        agent_time = time.time() - agent_start
                        agent_times[agent_role] = agent_time
                        if verbose:
                            # Clear line and print completion
                            sys.stdout.write(f"\r   ✓ {agent_display_name} completed ({len(completed)}/4) [{agent_time:.1f}s]                    \n")
                            sys.stdout.flush()
                    except Exception as e:
                        agent_time = time.time() - agent_start
                        if verbose:
                            sys.stdout.write(f"\r   ✗ {agent_display_name} failed: {str(e)[:50]}... [{agent_time:.1f}s]                    \n")
                            sys.stdout.flush()
                        agent_responses[agent_display_name] = f"Error: {str(e)}"
                        agent_responses[agent_role] = f"Error: {str(e)}"
                        completed.add(agent_role)
        
        elapsed = time.time() - start_time
        if verbose:
            print(f"   ✅ All agents completed ({len(agent_responses)}/4 responses received) [Total: {elapsed:.1f}s]\n")
        
        state["agent_responses"] = agent_responses
        state["current_step"] = 2
        
        return state
    
    def step_2_5_debate(self, state: CouncilState, verbose: bool = True, rounds: int = 2) -> CouncilState:
        """
        STEP 2.5: Multi-round debate where agents respond to each other in a group chat style.
        
        Args:
            state: Current council state with agent responses
            verbose: Whether to print progress updates
            rounds: Number of debate rounds (default 2)
            
        Returns:
            Updated state with debate rounds
        """
        problem = state["problem_statement"]
        agent_responses = state["agent_responses"]
        start_time = time.time()
        
        # Agent name mapping
        agent_names = {
            "Visionary": "Elon",
            "Strategist": "Sam",
            "Operator": "Sheryl",
            "Risk Analyst": "Ray"
        }
        
        if verbose:
            print(f"\n💬 Group Chat: Agents discussing naturally...")
        
        agents = {
            "Elon": self.visionary,
            "Sam": self.strategist,
            "Sheryl": self.operator,
            "Ray": self.risk_analyst
        }
        
        # Convert initial responses to use normal names
        initial_responses = {}
        for full_name, short_name in agent_names.items():
            if full_name in agent_responses:
                initial_responses[short_name] = agent_responses[full_name]
        
        # Build conversation history starting with initial responses
        conversation_history = []
        for name, response in initial_responses.items():
            conversation_history.append(f"{name}: {response}")
        
        group_chat_messages = []
        
        # Natural group chat - agents respond to each other
        for round_num in range(rounds):
            if verbose:
                print(f"   └─ Round {round_num + 1}/{rounds}...")
            
            # Each agent responds naturally to the conversation
            for agent_name, agent in agents.items():
                if verbose:
                    print(f"   ├─ {agent_name} typing...")
                
                # Get recent conversation context (last 10 messages)
                recent_messages = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                
                # Format conversation history for natural chat
                conversation_context = "\n".join(recent_messages)
                
                try:
                    # Use chat_response for natural group chat interaction
                    # Create a simple prompt that encourages natural conversation
                    # The agent should respond to the ongoing discussion
                    conversation_prompt = f"The group is discussing:\n\n{conversation_context}\n\nWhat do you think? Respond naturally to the conversation."
                    
                    # Agents respond naturally to the ongoing conversation
                    response = agent.chat_response(
                        user_message=conversation_prompt,
                        conversation_context=conversation_context,
                        agent_name=agent_name
                    )
                    
                    # Add to conversation
                    conversation_history.append(f"{agent_name}: {response}")
                    
                    group_chat_messages.append({
                        "agent": agent_name,
                        "message": response,
                        "timestamp": time.time()
                    })
                    
                    if verbose:
                        print(f"   ✓ {agent_name} responded")
                except Exception as e:
                    if verbose:
                        print(f"   ✗ {agent_name} failed: {str(e)}")
                    error_msg = f"Error: {str(e)}"
                    conversation_history.append(f"{agent_name}: {error_msg}")
                    group_chat_messages.append({
                        "agent": agent_name,
                        "message": error_msg,
                        "timestamp": time.time()
                    })
        
        # Store group chat messages
        if "group_chat" not in state:
            state["group_chat"] = []
        state["group_chat"].extend(group_chat_messages)
        state["current_step"] = 2.5
        
        elapsed = time.time() - start_time
        if verbose:
            print(f"   ✅ Group chat complete ({rounds} rounds) [{elapsed:.1f}s]\n")
        
        return state
    
    def step_3_synthesis(self, state: CouncilState, verbose: bool = True) -> CouncilState:
        """
        STEP 3: Synthesis agent analyzes all responses and produces structured output.
        
        Args:
            state: Current council state with agent responses
            verbose: Whether to print progress updates
            
        Returns:
            Updated state with synthesis output
        """
        problem = state["problem_statement"]
        agent_responses = state["agent_responses"]
        start_time = time.time()
        
        if verbose:
            print("🔍 STEP 3: Synthesizing agent responses...")
            print("   └─ Meta-agent analyzing all 4 responses...")
        
        # Use role names for synthesis (internal processing)
        role_responses = {}
        role_to_name = {"Visionary": "Elon", "Strategist": "Sam", "Operator": "Sheryl", "Risk Analyst": "Ray"}
        for role_name, normal_name in role_to_name.items():
            # Prefer role name, fallback to normal name
            role_responses[role_name] = agent_responses.get(role_name) or agent_responses.get(normal_name, "")
        
        synthesis_output = self.synthesis.synthesize(problem, role_responses)
        
        elapsed = time.time() - start_time
        if verbose:
            print(f"   ✓ Synthesis complete [{elapsed:.1f}s]\n")
        
        state["synthesis_output"] = synthesis_output
        state["current_step"] = 3
        
        return state
    
    def step_4_final_decision(self, state: CouncilState, verbose: bool = True) -> CouncilState:
        """
        STEP 4: Generate final decision using weighted model or majority voting.
        
        Args:
            state: Current council state with synthesis output
            verbose: Whether to print progress updates
            
        Returns:
            Updated state with final decision
        """
        agent_responses = state["agent_responses"]
        synthesis_output = state["synthesis_output"]
        
        if verbose:
            method = "weighted model" if self.use_weighted_model else "majority voting"
            print(f"⚖️  STEP 4: Generating final decision using {method}...")
            if self.use_weighted_model:
                print("   └─ Applying weights: Visionary(35%), Strategist(30%), Operator(20%), Risk Analyst(15%)")
        
        if self.use_weighted_model:
            decision = self._weighted_decision(agent_responses, synthesis_output)
        else:
            decision = self._majority_voting(agent_responses, synthesis_output)
        
        if verbose:
            print("   ✓ Final decision generated\n")
        
        state["final_decision"] = decision
        state["current_step"] = 4
        
        return state
    
    def _weighted_decision(
        self,
        agent_responses: Dict[str, str],
        synthesis_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate weighted decision based on agent responses and synthesis.
        
        Args:
            agent_responses: Individual agent responses
            synthesis_output: Synthesis analysis
            
        Returns:
            Final decision with weighted recommendation
        """
        # Extract final options from synthesis
        options = synthesis_output.get("final_options", [])
        
        # Map role names to normal names for display
        role_to_name = {
            "Visionary": "Elon",
            "Strategist": "Sam",
            "Operator": "Sheryl",
            "Risk Analyst": "Ray"
        }
        
        # Create weighted recommendation with normal names for display
        weight_breakdown = {}
        for role_name, weight in self.weights.items():
            normal_name = role_to_name.get(role_name, role_name)
            # Try to get response by role name first, then normal name
            response = agent_responses.get(role_name) or agent_responses.get(normal_name, "")
            weight_breakdown[normal_name] = {
                "weight": weight,
                "response_preview": response[:200] + "..." if len(response) > 200 else response
            }
        
        recommendation = {
            "method": "weighted_model",
            "weights_used": {role_to_name.get(k, k): v for k, v in self.weights.items()},
            "synthesis_summary": synthesis_output.get("summary", ""),
            "recommended_options": options,
            "weight_breakdown": weight_breakdown,
            "key_agreements": synthesis_output.get("agreements", []),
            "key_conflicts": synthesis_output.get("conflicts", []),
            "identified_blind_spots": synthesis_output.get("blind_spots", []),
        }
        
        return recommendation
    
    def _majority_voting(
        self,
        agent_responses: Dict[str, str],
        synthesis_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate decision using majority voting (simple implementation).
        
        Args:
            agent_responses: Individual agent responses
            synthesis_output: Synthesis analysis
            
        Returns:
            Final decision with majority vote
        """
        options = synthesis_output.get("final_options", [])
        
        recommendation = {
            "method": "majority_voting",
            "synthesis_summary": synthesis_output.get("summary", ""),
            "recommended_options": options,
            "agent_responses": {
                agent: response[:200] + "..." if len(response) > 200 else response
                for agent, response in agent_responses.items()
            },
            "key_agreements": synthesis_output.get("agreements", []),
            "key_conflicts": synthesis_output.get("conflicts", []),
            "identified_blind_spots": synthesis_output.get("blind_spots", []),
        }
        
        return recommendation
    
    def run_tagged_debate(self, tagged_agents: list, user_message: str, conversation_history: list, verbose: bool = True) -> list:
        """
        Run a focused debate/conversation between tagged agents (2-3 exchanges to close the topic).
        
        Args:
            tagged_agents: List of agent names to participate in the debate
            user_message: The user's message/request
            conversation_history: Current conversation history
            verbose: Whether to print progress updates
            
        Returns:
            List of messages from the debate
        """
        agents = {
            "Elon": self.visionary,
            "Sam": self.strategist,
            "Sheryl": self.operator,
            "Ray": self.risk_analyst
        }
        
        # Filter to only tagged agents
        participating_agents = {name: agents[name] for name in tagged_agents if name in agents}
        
        if not participating_agents:
            return []
        
        debate_messages = []
        debate_history = list(conversation_history)  # Copy the list
        debate_history.append(f"You: {user_message}")
        
        if verbose:
            agent_names = ", ".join(tagged_agents)
            print(f"\n   💬 Debate between {agent_names}...")
            print(f"   └─ Topic: {user_message[:60]}{'...' if len(user_message) > 60 else ''}\n")
        
        # Run 2-3 exchanges to close the conversation
        max_exchanges = 3
        for exchange in range(max_exchanges):
            if verbose:
                print(f"   └─ Exchange {exchange + 1}/{max_exchanges}...")
            
            exchange_messages = []
            conversation_context = "\n".join(debate_history[-10:]) if len(debate_history) > 10 else "\n".join(debate_history)
            
            # Each tagged agent responds in this exchange
            for agent_name, agent in participating_agents.items():
                if verbose:
                    print(f"   ├─ {agent_name} responding...")
                
                # Create debate prompt that encourages closure
                if exchange == 0:
                    # First exchange: respond to the user's request
                    debate_prompt = f"""You are {agent_name} in a focused debate/discussion. The user asked: "{user_message}"

RECENT CONVERSATION:
{conversation_context}

Respond to the user's request. This is exchange 1 of up to 3. Try to make progress toward closing the topic. Be direct and substantive."""
                else:
                    # Subsequent exchanges: respond to each other and try to close
                    debate_prompt = f"""You are {agent_name} in a focused debate/discussion. 

RECENT CONVERSATION:
{conversation_context}

This is exchange {exchange + 1} of up to 3. Respond to what others said. Try to move toward closing the topic - agree, disagree, or propose a resolution. If the topic feels resolved, you can acknowledge that."""
                
                try:
                    response = agent.chat_response(
                        user_message=debate_prompt,
                        conversation_context=conversation_context,
                        agent_name=agent_name
                    )
                    
                    debate_history.append(f"{agent_name}: {response}")
                    exchange_messages.append({
                        "agent": agent_name,
                        "message": response,
                        "timestamp": time.time()
                    })
                    
                    if verbose:
                        print(f"\n   [{agent_name}]")
                        print(f"   {response}\n")
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    if verbose:
                        print(f"\n   [{agent_name}] Error: {error_msg}\n")
            
            debate_messages.extend(exchange_messages)
            
            # Check if conversation is closing (agents acknowledging resolution)
            if exchange_messages:
                last_responses = [msg["message"].lower() for msg in exchange_messages]
                closing_signals = ["agree", "sounds good", "makes sense", "resolved", "i think we're done", "that works"]
                if any(signal in response for response in last_responses for signal in closing_signals):
                    if verbose:
                        print(f"   ✓ Topic appears resolved after {exchange + 1} exchanges\n")
                    break
        
        # Update the original conversation history with debate messages
        for msg in debate_messages:
            conversation_history.append(f"{msg['agent']}: {msg['message']}")
        
        return debate_messages
    
    def run_one_round(self, conversation_history: list, is_first_round: bool = False, verbose: bool = True) -> list:
        """
        Run one round of group chat where agents can choose to respond or not.
        
        Args:
            conversation_history: Current conversation history
            is_first_round: Whether this is the first round (all agents should respond)
            verbose: Whether to print progress updates
            
        Returns:
            List of new messages from this round
        """
        agents = {
            "Elon": self.visionary,
            "Sam": self.strategist,
            "Sheryl": self.operator,
            "Ray": self.risk_analyst
        }
        
        new_messages = []
        conversation_context = "\n".join(conversation_history[-10:]) if len(conversation_history) > 10 else "\n".join(conversation_history)
        
        if verbose:
            if is_first_round:
                print("   └─ Agents responding to your message...")
            else:
                print("   └─ New round: Agents can respond if they have something to say...")
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for agent_name, agent in agents.items():
                if is_first_round:
                    # First round: all agents respond to the latest user message
                    # Find the last "You:" message in conversation history
                    user_messages = [msg for msg in conversation_history if msg.startswith("You:")]
                    prompt = user_messages[-1] if user_messages else (conversation_history[0] if conversation_history else "")
                else:
                    # Subsequent rounds: agents decide if they want to respond
                    prompt = f"The group is discussing:\n\n{conversation_context}\n\nDo you have something to add? Only respond if you have something relevant to say. If you don't have anything to add, respond with just 'SKIP'."
                
                future = executor.submit(
                    agent.chat_response,
                    prompt,
                    conversation_context,
                    agent_name
                )
                futures[agent_name] = future
            
            # Collect responses as they come in
            for agent_name, future in futures.items():
                try:
                    response = future.result(timeout=60)
                    
                    # Check if agent chose to skip
                    if response.strip().upper() == "SKIP" or response.strip().upper().startswith("SKIP"):
                        if verbose:
                            print(f"   • {agent_name} chose not to respond")
                        continue
                    
                    # Agent responded
                    new_messages.append({
                        "agent": agent_name,
                        "message": response,
                        "timestamp": time.time()
                    })
                    conversation_history.append(f"{agent_name}: {response}")
                    
                    if verbose:
                        print(f"\n   [{agent_name}]")
                        print(f"   {response}\n")
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    if verbose:
                        print(f"\n   [{agent_name}] Error: {error_msg}\n")
        
        return new_messages
    
    def run_group_chat(self, user_message: str, verbose: bool = True, chat_rounds: int = 1) -> CouncilState:
        """
        Run a natural WhatsApp-style group chat one round at a time.
        
        Args:
            user_message: The user's message to the group
            verbose: Whether to print progress updates
            chat_rounds: Number of rounds to run (default 1)
            
        Returns:
            Council state with group chat messages
        """
        total_start = time.time()
        
        if verbose:
            print(f"\n💬 Group Chat Started...")
            print(f"   └─ User: {user_message[:80]}{'...' if len(user_message) > 80 else ''}\n")
        
        # Initialize state
        state = CouncilState(
            problem_statement=user_message,
            agent_responses={},
            debate_rounds=[],
            synthesis_output=None,
            final_decision=None,
            current_step=1,
            metadata={},
            messages=[]
        )
        
        # Build conversation history starting with user message
        conversation_history = [f"You: {user_message}"]
        group_chat_messages = []
        
        # Round 1: All agents respond to the user's message
        round1_messages = self.run_one_round(conversation_history, is_first_round=True, verbose=verbose)
        group_chat_messages.extend(round1_messages)
        
        # Additional rounds: Agents can choose to respond or not
        for round_num in range(1, chat_rounds):
            if verbose:
                print(f"\n   └─ Round {round_num + 1}...")
            
            round_messages = self.run_one_round(conversation_history, is_first_round=False, verbose=verbose)
            group_chat_messages.extend(round_messages)
            
            # If no one responded, break early
            if not round_messages and verbose:
                print("   • No agents responded this round")
        
        # Store group chat
        state["group_chat"] = group_chat_messages
        state["conversation_history"] = conversation_history
        
        total_elapsed = time.time() - total_start
        if verbose:
            print(f"\n   ✅ Round complete [{total_elapsed:.1f}s]\n")
        
        return state
    
    def run_council(self, problem: str, verbose: bool = True) -> CouncilState:
        """
        Execute the complete 4-step council protocol (legacy method).
        
        Args:
            problem: Problem statement to analyze
            verbose: Whether to print progress updates
            
        Returns:
            Final council state with complete analysis
        """
        total_start = time.time()
        
        if verbose:
            print("📢 STEP 1: Broadcasting problem to all agents...")
            print(f"   └─ Problem: {problem[:100]}{'...' if len(problem) > 100 else ''}\n")
        
        # STEP 1: Broadcast
        state = self.step_1_broadcast(problem)
        
        if verbose:
            print("   ✓ Problem broadcasted to all 4 agents\n")
        
        # STEP 2: Parallel Responses
        state = self.step_2_parallel_responses(state, verbose=verbose)
        
        # STEP 2.5: Natural Group Chat
        state = self.step_2_5_debate(state, verbose=verbose, rounds=2)
        
        # STEP 3: Synthesis
        state = self.step_3_synthesis(state, verbose=verbose)
        
        # STEP 4: Final Decision
        state = self.step_4_final_decision(state, verbose=verbose)
        
        total_elapsed = time.time() - total_start
        if verbose:
            print("=" * 80)
            print(f"✅ COUNCIL PROTOCOL COMPLETE [Total time: {total_elapsed:.1f}s]")
            print("=" * 80 + "\n")
        
        return state

