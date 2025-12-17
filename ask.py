#!/usr/bin/env python3
"""
Interactive Event Assistant CLI (Rich UI).
"""
import sys
import asyncio
import argparse
from loguru import logger

# Rich Imports
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from rich.text import Text

# Disable aggressive logging for CLI experience
logger.remove()
logger.add(sys.stderr, level="ERROR")

from src.ai.assistant import EventAssistant, CATEGORIES

# Initialize Console
console = Console()


def display_welcome():
    """Display welcome message."""
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]👋 Hi! I'm your Event AI.[/bold cyan]\n"
            "[dim]I can help you find events, plan dates, or discover hidden gems.[/dim]\n\n"
            "[yellow]Type 'exit' to stop.[/yellow]",
            title="EventGraph AI",
            border_style="cyan",
        )
    )
    console.print()


def display_event_card(event: dict, score: float = None, reason: str = None):
    """Display a single event as a card."""
    title = f"[bold white]{event.get('title', 'Unknown Event')}[/bold white]"
    venue = event.get("venue") or "Unknown Venue"
    city = event.get("city") or "Unknown City"
    date = event.get("date") or "Unknown Date"
    price = event.get("price")

    # Format Price
    if price == 0:
        price_str = "[bold green]FREE[/bold green]"
    elif price:
        price_str = f"[bold yellow]{price} TL[/bold yellow]"
    else:
        price_str = "[dim]Price N/A[/dim]"

    # Meta info line
    meta = f"📍 {city}  🏠 {venue}  🗓️  {date}  💰 {price_str}"

    # Content
    content = [meta]

    if reason:
        content.append(f"\n[italic cyan]🏆 {reason}[/italic cyan]")

    if event.get("summary"):
        summary_text = event['summary']
        # Deduplicate if reason is same as summary
        if not reason or (reason and summary_text not in reason and reason not in summary_text):
             content.append(f"\n[dim]{summary_text[:300]}...[/dim]")

    # Footer (Score)
    footer = None
    if score:
        match_percent = int(score * 100)
        color = "green" if match_percent > 80 else "yellow" if match_percent > 50 else "red"
        footer = f"[bold {color}]Match: {match_percent}%[/bold {color}]"

    console.print(
        Panel(
            "\n".join(content),
            title=title,
            subtitle=footer,
            border_style="blue",
            expand=False,
        )
    )


async def main():
    parser = argparse.ArgumentParser(description="Event Assistant")
    parser.add_argument("query", type=str, nargs="?", help="Initial query")
    args = parser.parse_args()

    display_welcome()

    with console.status("[bold green]Initializing AI...[/bold green]"):
        assistant = EventAssistant()

    # If initial query provided, process it first
    initial_query = args.query

    while True:
        try:
            if initial_query:
                query = initial_query
                console.print(f"\n[bold cyan]>> {query}[/bold cyan]")
                initial_query = None
            else:
                query = Prompt.ask("\n[bold cyan]>> What are you looking for?[/bold cyan]")

            query = query.strip()
            if not query:
                continue

            if query.lower() in ["exit", "quit", "q"]:
                console.print("[bold green]👋 Goodbye![/bold green]")
                break

            with console.status("[bold yellow]Thinking...[/bold yellow]", spinner="dots"):
                # 1. Identify Intent
                intent = await assistant.identify_intent(query)

                if intent and intent != "search":
                    # Handle Collection
                    cat_name = CATEGORIES.get(intent, intent)
                    console.print(f"\n[bold magenta]💡 Found a curated collection: {cat_name}[/bold magenta]\n")

                    events = await assistant.get_collection(intent)
                    if not events:
                        console.print("[red]❌ No events found in this collection.[/red]")
                    else:
                        for e in events:
                            display_event_card(e, reason=e.get("reason"))
                else:
                    # Handle Search (Hybrid + RAG)
                    results = await assistant.search(query)
                    answer = await assistant.generate_answer(query, results)

                    # Print Answer as Markdown
                    console.print(Panel(Markdown(answer), title="🤖 AI Response", border_style="green"))

                    if results:
                        console.print("\n[bold white]📚 Source Events:[/bold white]")
                        # Fetch details for display
                        for score, summary in results[:5]:
                            details = await assistant._fetch_event_details(summary.event_uuid)
                            if details:
                                display_event_card(details, score=score)
                    else:
                        console.print("[dim]No specific events found directly matching criteria.[/dim]")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold green]👋 Goodbye![/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            logger.exception(e)


if __name__ == "__main__":
    asyncio.run(main())
