"""
solai - Your CLI Assistant
"""
import os
import sys
import click
import platform
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

def get_system_info():
    """Get system information"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macOS'
    elif system == 'linux':
        return 'Linux'
    elif system == 'windows':
        return 'Windows'
    return system

def setup_config():
    """Initial setup for configuration"""
    console.print("[yellow]First time setup: AI Configuration[/yellow]")
    console.print("\n[cyan]Choose your AI provider:[/cyan]")
    console.print("1. Local AI (Msty Studio) - Recommended for privacy")
    console.print("2. OpenAI Cloud")
    
    choice = Prompt.ask("Enter your choice", choices=["1", "2"], default="1")
    
    config_path = os.path.expanduser('~/.solai.env')
    config_lines = []
    
    if choice == "1":
        # Local AI setup (Msty Studio)
        console.print("\n[blue]Setting up local AI with Msty Studio[/blue]")
        console.print("[dim]Make sure Msty Studio is running locally[/dim]")
        
        base_url = Prompt.ask(
            "Enter Msty Studio API base URL", 
            default="http://localhost:1234/v1"
        )
        api_key = Prompt.ask(
            "Enter API key (or press Enter for 'not-needed')", 
            default="not-needed"
        )
        model = Prompt.ask(
            "Enter model name", 
            default="mistral"
        )
        
        config_lines.append(f"AI_PROVIDER=local")
        config_lines.append(f"API_BASE_URL={base_url}")
        config_lines.append(f"API_KEY={api_key}")
        config_lines.append(f"MODEL={model}")
    else:
        # OpenAI Cloud setup
        console.print("\n[blue]Setting up OpenAI Cloud[/blue]")
        console.print("[dim]Get your API key from: https://platform.openai.com/api-keys[/dim]")
        
        api_key = Prompt.ask("Enter your OpenAI API key", type=str)
        model = Prompt.ask("Enter model name", default="gpt-3.5-turbo")
        
        config_lines.append(f"AI_PROVIDER=openai")
        config_lines.append(f"API_KEY={api_key}")
        config_lines.append(f"MODEL={model}")
    
    with open(config_path, 'w') as f:
        f.write('\n'.join(config_lines) + '\n')
    
    console.print(f"\n[green]Configuration saved to {config_path}[/green]")
    return config_lines

def load_config():
    """Load configuration and return client, model"""
    config_path = os.path.expanduser('~/.solai.env')
    if not os.path.exists(config_path):
        setup_config()
    
    load_dotenv(config_path)
    
    provider = os.getenv('AI_PROVIDER', 'local').lower()
    api_key = os.getenv('API_KEY', 'not-needed')
    model = os.getenv('MODEL', 'mistral' if provider == 'local' else 'gpt-3.5-turbo')
    base_url = os.getenv('API_BASE_URL', 'http://localhost:1234/v1')
    
    # Initialize client based on provider
    if provider == 'local':
        # Local AI (Msty Studio)
        client = OpenAI(
            base_url=base_url,
            api_key=api_key if api_key != 'not-needed' else None
        )
    else:
        # OpenAI Cloud
        client = OpenAI(api_key=api_key)
    
    return client, model

def get_command_suggestion(client, model, query):
    """Get command suggestion from AI"""
    os_type = get_system_info()
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a CLI assistant for {os_type}. Return the command followed by '||' and a brief explanation of what it does. Format: 'command || explanation'. Ensure all commands are compatible with {os_type}."
                },
                {"role": "user", "content": query}
            ]
        )
        result = response.choices[0].message.content.strip()
        
        # Split command and explanation
        if '||' in result:
            command, explanation = result.split('||', 1)
            return command.strip(), explanation.strip()
        return result.strip(), ""
    except Exception as e:
        # If local AI fails, provide helpful error message
        if "Connection" in str(e) or "refused" in str(e).lower():
            console.print("\n[red]Error: Could not connect to local AI server[/red]")
            console.print("[yellow]Make sure Msty Studio is running and accessible at the configured URL[/yellow]")
            console.print(f"[dim]Error details: {str(e)}[/dim]")
        raise

@click.command()
@click.argument('query', nargs=-1)
def main(query):
    """CLI Assistant - Get command suggestions for your queries"""
    if not query:
        console.print("[red]Please provide a query[/red]")
        sys.exit(1)

    # Load configuration and initialize client
    try:
        client, model = load_config()
    except Exception as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)

    # Get the full query
    full_query = ' '.join(query)
    
    try:
        # Get command suggestion
        command, explanation = get_command_suggestion(client, model, full_query)
        
        # Display suggestion with explanation
        console.print("\n[green]Suggested command:[/green]")
        console.print(f"[yellow]{command}[/yellow]")
        if explanation:
            console.print(f"[blue]→ {explanation}[/blue]\n")
        
        # Ask for confirmation
        if Confirm.ask("Do you want to execute this command?"):
            os.system(command)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
