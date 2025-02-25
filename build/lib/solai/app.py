"""
solai - Your CLI Assistant
"""
import os
import sys
import click
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def get_openai_key():
    """Get OpenAI key from user and save it"""
    console.print("[yellow]First time setup: OpenAI API Key required[/yellow]")
    api_key = click.prompt("Please enter your OpenAI API key", type=str)
    
    with open(os.path.expanduser('~/.solai.env'), 'w') as f:
        f.write(f"OPENAI_API_KEY={api_key}")
    
    return api_key

def load_config():
    """Load configuration"""
    config_path = os.path.expanduser('~/.solai.env')
    if not os.path.exists(config_path):
        return get_openai_key()
    
    load_dotenv(config_path)
    return os.getenv('OPENAI_API_KEY')

def get_command_suggestion(client, query):
    """Get command suggestion from OpenAI"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a CLI assistant. Provide only the exact command to run, nothing else."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content.strip()

@click.command()
@click.argument('query', nargs=-1)
def main(query):
    """CLI Assistant - Get command suggestions for your queries"""
    if not query:
        console.print("[red]Please provide a query[/red]")
        sys.exit(1)

    # Initialize OpenAI
    api_key = load_config()
    client = OpenAI(api_key=api_key)

    # Get the full query
    full_query = ' '.join(query)
    
    try:
        # Get command suggestion
        suggested_command = get_command_suggestion(client, full_query)
        
        # Display suggestion
        console.print("\n[green]Suggested command:[/green]")
        console.print(f"[yellow]{suggested_command}[/yellow]\n")
        
        # Ask for confirmation
        if Confirm.ask("Do you want to execute this command?"):
            os.system(suggested_command)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    main()
