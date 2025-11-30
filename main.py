"""
Main CLI interface for the Agentic Council System.
Beautiful command-line interface with rich formatting for problem analysis.

Optimized for production with robust error handling, configuration management,
and efficient resource utilization.
"""

"""
Main CLI interface for the Agentic Council System.
Beautiful command-line interface with rich formatting for problem analysis.
"""

import os
import sys
import re
import traceback
from typing import Optional, Dict, Any, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

try:
    from .council import CouncilOrchestrator
    from .config import Config
except ImportError:
    # For direct execution
    from council import CouncilOrchestrator
    from config import Config

# Initialize rich console
console = Console()

# Agent colors and emojis - using normal names
AGENT_STYLES = {
    "Elon": {"color": "cyan", "emoji": "🚀", "role": "Visionary"},
    "Sam": {"color": "blue", "emoji": "🎯", "role": "Strategist"},
    "Sheryl": {"color": "green", "emoji": "⚙️", "role": "Operator"},
    "Ray": {"color": "yellow", "emoji": "⚠️", "role": "Risk Analyst"}
}


def print_header():
    """Print beautiful welcome header."""
    header_text = Text("AGENTIC COUNCIL SYSTEM", style="bold bright_white")
    header_text.stylize("bold cyan", 0, 7)
    header_text.stylize("bold magenta", 8, 14)
    
    console.print()
    console.print(Panel(
        header_text,
        border_style="bright_blue",
        padding=(1, 2)
    ))
    
    info_table = Table.grid(padding=(0, 2))
    info_table.add_row("💬 Group Chat:", "[cyan]Elon[/cyan] | [blue]Sam[/blue] | [green]Sheryl[/green] | [yellow]Ray[/yellow]")
    info_table.add_row("🔗 Ollama:", f"[dim]{Config.OLLAMA_BASE_URL}[/dim]")
    
    console.print(info_table)
    console.print()


def print_user_message(message: str):
    """Print user message in a WhatsApp-style format."""
    console.print()
    console.print(f"[bold white]You:[/bold white] [white]{message}[/white]")
    console.print()


def print_group_chat(group_chat: List[Dict[str, Any]]):
    """Print group chat messages in a WhatsApp-style format showing each agent's response clearly."""
    if not group_chat:
        return
    
    console.print()
    console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")
    console.print()
    
    for item in group_chat:
        agent_name = item.get("agent", "Unknown")
        message = item.get("message", "")
        
        if agent_name in AGENT_STYLES:
            style = AGENT_STYLES[agent_name]
            agent_display = f"{style['emoji']} {agent_name}"
            
            # WhatsApp-style message format - clear and readable
            console.print(f"[bold {style['color']}]{agent_display}[/bold {style['color']}]")
            console.print(f"[white]{message}[/white]")
            console.print()
        else:
            # Fallback for unknown agents
            console.print(f"[bold]{agent_name}[/bold]")
            console.print(f"[white]{message}[/white]")
            console.print()
    
    console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")


def print_synthesis(synthesis_output: Dict[str, Any]):
    """Print synthesis analysis with beautiful formatting."""
    console.print()
    console.print(Panel(
        "[bold]STEP 3: Synthesis Analysis[/bold]",
        border_style="bright_magenta",
        padding=(0, 1)
    ))
    console.print()
    
    # Summary
    summary = synthesis_output.get('summary', 'N/A')
    console.print(Panel(
        Markdown(summary),
        title="[bold magenta]📋 Summary[/bold magenta]",
        border_style="magenta",
        padding=(1, 2)
    ))
    console.print()
    
    # Agreements
    agreements = synthesis_output.get('agreements', [])
    if agreements:
        table = Table(title="[bold green]✅ Key Agreements[/bold green]", border_style="green", show_header=False)
        for i, agreement in enumerate(agreements, 1):
            table.add_row(f"[green]{i}.[/green]", Markdown(agreement))
        console.print(table)
        console.print()
    
    # Conflicts
    conflicts = synthesis_output.get('conflicts', [])
    if conflicts:
        table = Table(title="[bold red]⚔️  Key Conflicts[/bold red]", border_style="red", show_header=False)
        for i, conflict in enumerate(conflicts, 1):
            table.add_row(f"[red]{i}.[/red]", Markdown(conflict))
        console.print(table)
        console.print()
    
    # Blind Spots
    blind_spots = synthesis_output.get('blind_spots', [])
    if blind_spots:
        table = Table(title="[bold yellow]⚠️  Identified Blind Spots[/bold yellow]", border_style="yellow", show_header=False)
        for i, blind_spot in enumerate(blind_spots, 1):
            table.add_row(f"[yellow]{i}.[/yellow]", Markdown(blind_spot))
        console.print(table)
        console.print()
    
    # Final Options
    options = synthesis_output.get('final_options', [])
    if options:
        table = Table(title="[bold cyan]🎯 Final Options (2-3 Paths Forward)[/bold cyan]", border_style="cyan", show_header=False)
        for i, option in enumerate(options, 1):
            table.add_row(f"[cyan]{i}.[/cyan]", Markdown(option))
        console.print(table)
        console.print()


def print_final_decision(final_decision: Dict[str, Any]):
    """Print final decision with beautiful formatting."""
    console.print()
    console.print(Panel(
        "[bold]STEP 4: Final Weighted Recommendation[/bold]",
        border_style="bright_green",
        padding=(0, 1)
    ))
    console.print()
    
    method = final_decision.get('method', 'unknown')
    console.print(f"[dim]Decision Method:[/dim] [bold]{method.upper()}[/bold]\n")
    
    # Agent Weights Table
    if method == "weighted_model":
        weights = final_decision.get('weights_used', {})
        weights_table = Table(title="[bold]⚖️  Agent Weights[/bold]", border_style="blue")
        weights_table.add_column("Agent", style="cyan", no_wrap=True)
        weights_table.add_column("Weight", justify="right", style="green")
        weights_table.add_column("Percentage", justify="right", style="yellow")
        
        for agent, weight in weights.items():
            style = AGENT_STYLES.get(agent, {})
            agent_display = f"{style.get('emoji', '🤖')} {style.get('name', agent)}"
            weights_table.add_row(
                agent_display,
                f"{weight:.2f}",
                f"{weight*100:.0f}%"
            )
        console.print(weights_table)
        console.print()
    
    # Recommended Options
    options = final_decision.get('recommended_options', [])
    if options:
        table = Table(title="[bold green]🏆 Recommended Path Forward[/bold green]", border_style="green", show_header=False)
        for i, option in enumerate(options, 1):
            table.add_row(f"[green]{i}.[/green]", Markdown(option))
        console.print(table)
        console.print()
    
    # Key Agreements
    agreements = final_decision.get('key_agreements', [])
    if agreements:
        table = Table(title="[bold]✅ Key Agreements[/bold]", border_style="green", show_header=False)
        for i, agreement in enumerate(agreements, 1):
            table.add_row(f"[green]{i}.[/green]", Markdown(agreement))
        console.print(table)
        console.print()
    
    # Key Conflicts
    conflicts = final_decision.get('key_conflicts', [])
    if conflicts:
        table = Table(title="[bold]⚔️  Key Conflicts[/bold]", border_style="red", show_header=False)
        for i, conflict in enumerate(conflicts, 1):
            table.add_row(f"[red]{i}.[/red]", Markdown(conflict))
        console.print(table)
        console.print()
    
    # Blind Spots
    blind_spots = final_decision.get('identified_blind_spots', [])
    if blind_spots:
        table = Table(title="[bold]⚠️  Identified Blind Spots[/bold]", border_style="yellow", show_header=False)
        for i, blind_spot in enumerate(blind_spots, 1):
            table.add_row(f"[yellow]{i}.[/yellow]", Markdown(blind_spot))
        console.print(table)
        console.print()


def get_problem_input() -> str:
    """
    Get problem statement from user via stdin or command line argument.
    
    Supports:
    - Command line argument: python main.py "problem statement"
    - Piped input: echo "problem" | python main.py
    - Interactive input: python main.py (then type problem)
    """
    # Check for command line argument
    if len(sys.argv) > 1:
        problem = " ".join(sys.argv[1:]).strip()
        if problem:
            return problem
    
    # Check for piped input
    if not sys.stdin.isatty():
        problem = sys.stdin.read().strip()
        if problem:
            return problem
    
    # Interactive input
    console.print("[bold cyan]Enter your problem statement:[/bold cyan]")
    console.print("[dim](Press Enter twice or Ctrl+D to finish)[/dim]")
    console.print()
    
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "" and lines and lines[-1].strip() == "":
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    
    problem = "\n".join(lines).strip()
    
    if not problem:
        console.print()
        console.print(Panel(
            "[bold red]❌ Error: Problem statement cannot be empty.[/bold red]\n\n"
            "[dim]Usage:[/dim]\n"
            "  [cyan]python main.py \"your problem statement\"[/cyan]\n"
            "  [cyan]echo \"your problem\" | python main.py[/cyan]\n"
            "  [cyan]python main.py[/cyan] (interactive mode)",
            border_style="red",
            title="[bold]Usage Information[/bold]"
        ))
        sys.exit(1)
    
    return problem


def main():
    """Main entry point."""
    print_header()
    
    # Get problem input
    problem = get_problem_input()
    
    try:
        # Initialize council with progress indicator
        with console.status("[bold cyan]Initializing Council...", spinner="dots"):
            council = CouncilOrchestrator()
        
        console.print()
        console.print(Panel(
            f"[green]✓[/green] Council initialized with 4 agents + synthesis agent\n"
            f"[dim]Base URL:[/dim] {Config.OLLAMA_BASE_URL}\n"
            f"[dim]Weighted Model:[/dim] {Config.USE_WEIGHTED_MODEL}",
            border_style="green",
            title="[bold green]✅ Initialization Complete[/bold green]"
        ))
        console.print()
        
        console.print("[bold cyan]💬 Starting group chat...[/bold cyan]")
        console.print("[dim]⏳ Agents are typing...[/dim]\n")
        
        # Initialize conversation
        conversation_history = [f"You: {problem}"]
        all_messages = []
        
        # First round: All agents respond
        console.print("[bold cyan]Round 1:[/bold cyan]")
        round_messages = council.run_one_round(conversation_history, is_first_round=True, verbose=True)
        all_messages.extend(round_messages)
        
        # Display the conversation
        print_user_message(problem)
        if all_messages:
            print_group_chat(all_messages)
        
        # Interactive loop for additional rounds
        round_num = 2
        while True:
            console.print()
            console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")
            console.print()
            console.print("[bold cyan]Type your message (or press Enter for another round, 'exit' to quit):[/bold cyan]")
            console.print("[dim]Tip: Tag agents with @Elon @Sam @Sheryl @Ray to start a debate[/dim]")
            
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    # Empty input - just run another round with existing conversation
                    console.print()
                    console.print(f"[bold cyan]Round {round_num}:[/bold cyan]")
                    round_messages = council.run_one_round(conversation_history, is_first_round=False, verbose=True)
                    
                    if round_messages:
                        all_messages.extend(round_messages)
                        print_group_chat(round_messages)
                    else:
                        console.print("[dim]No agents responded this round.[/dim]")
                    
                    round_num += 1
                elif user_input.lower() == 'exit' or user_input.lower() == 'quit' or user_input.lower() == 'q':
                    break
                else:
                    # Check for @mentions
                    mentions = re.findall(r'@(\w+)', user_input)
                    
                    if mentions:
                        # User tagged specific agents - run a debate between them
                        tagged_agents = [name for name in mentions if name in ["Elon", "Sam", "Sheryl", "Ray"]]
                        
                        if tagged_agents:
                            # Remove @ symbols for display
                            display_message = re.sub(r'@(\w+)', r'\1', user_input)
                            conversation_history.append(f"You: {display_message}")
                            print_user_message(display_message)
                            
                            console.print()
                            console.print(f"[bold cyan]💬 Tagged Debate: {', '.join(tagged_agents)}[/bold cyan]")
                            
                            debate_messages = council.run_tagged_debate(
                                tagged_agents=tagged_agents,
                                user_message=display_message,
                                conversation_history=conversation_history,
                                verbose=True
                            )
                            
                            if debate_messages:
                                all_messages.extend(debate_messages)
                                print_group_chat(debate_messages)
                        else:
                            # Invalid tags - treat as normal message
                            conversation_history.append(f"You: {user_input}")
                            print_user_message(user_input)
                            
                            console.print()
                            console.print(f"[bold cyan]Round {round_num}:[/bold cyan]")
                            round_messages = council.run_one_round(conversation_history, is_first_round=True, verbose=True)
                            
                            if round_messages:
                                all_messages.extend(round_messages)
                                print_group_chat(round_messages)
                            
                            round_num += 1
                    else:
                        # User typed a new message - add it to conversation and have agents respond
                        conversation_history.append(f"You: {user_input}")
                        print_user_message(user_input)
                        
                        console.print()
                        console.print(f"[bold cyan]Round {round_num}:[/bold cyan]")
                        # Treat user's new message like first round - all agents should respond
                        round_messages = council.run_one_round(conversation_history, is_first_round=True, verbose=True)
                        
                        if round_messages:
                            all_messages.extend(round_messages)
                            print_group_chat(round_messages)
                        
                        round_num += 1
                
            except (EOFError, KeyboardInterrupt):
                console.print()
                break
        
        console.print()
        console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")
        console.print()
        
    except KeyboardInterrupt:
        console.print()
        console.print(Panel(
            "[bold yellow]⚠️  Analysis interrupted by user.[/bold yellow]",
            border_style="yellow"
        ))
        sys.exit(130)
    except ConnectionError as e:
        console.print()
        console.print(Panel(
            f"[bold red]❌ Connection Error[/bold red]\n\n{str(e)}\n\n"
            "[dim]Please ensure:[/dim]\n"
            f"  1. Ollama is running at [cyan]{Config.OLLAMA_BASE_URL}[/cyan]\n"
            "  2. Start Ollama with: [cyan]ollama serve[/cyan]",
            border_style="red",
            title="[bold]Connection Error[/bold]"
        ))
        sys.exit(1)
    except Exception as e:
        console.print()
        error_panel_content = f"[bold red]❌ Error:[/bold red] {str(e)}\n\n"
        
                    if Config.DEBUG:
            error_panel_content += f"[dim]Full traceback:[/dim]\n"
            error_panel_content += f"[red]{traceback.format_exc()}[/red]\n\n"
        
        error_panel_content += (
            "[dim]Please ensure:[/dim]\n"
            f"  1. Ollama is running at [cyan]{Config.OLLAMA_BASE_URL}[/cyan]\n"
            "  2. Required models are pulled:\n"
            "     [cyan]- ollama pull gpt-oss:120b-cloud[/cyan]\n"
            "     [cyan]- ollama pull glm-4.6:cloud[/cyan]\n"
            "     [cyan]- ollama pull kimi-k2-thinking:cloud[/cyan]\n"
            "     [cyan]- ollama pull deepseek-v3.1:671b-cloud[/cyan]\n\n"
            "[dim]Set DEBUG=true for detailed error information.[/dim]"
        )
        
        console.print(Panel(
            error_panel_content,
            border_style="red",
            title="[bold]Error[/bold]"
        ))
        sys.exit(1)


if __name__ == "__main__":
    main()
