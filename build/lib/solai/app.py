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

def migrate_old_config(config_path):
    """Migrate old config format to new format"""
    load_dotenv(config_path)
    old_api_key = os.getenv('OPENAI_API_KEY')
    
    if old_api_key:
        console.print("[yellow]Detected old configuration format. Migrating...[/yellow]")
        console.print("[cyan]Would you like to use OpenAI Cloud (your existing key) or switch to Local AI (Msty Studio)?[/cyan]")
        console.print("1. Keep OpenAI Cloud (use existing API key)")
        console.print("2. Switch to Local AI (Msty Studio)")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2"], default="1")
        
        if choice == "1":
            # Migrate to new OpenAI format
            with open(config_path, 'w') as f:
                f.write(f"AI_PROVIDER=openai\n")
                f.write(f"API_KEY={old_api_key}\n")
                f.write(f"MODEL=gpt-3.5-turbo\n")
            console.print("[green]Configuration migrated to OpenAI Cloud format[/green]")
        else:
            # Switch to local AI
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
            
            with open(config_path, 'w') as f:
                f.write(f"AI_PROVIDER=local\n")
                f.write(f"API_BASE_URL={base_url}\n")
                f.write(f"API_KEY={api_key}\n")
                f.write(f"MODEL={model}\n")
            console.print("[green]Configuration set to Local AI[/green]")

def load_config():
    """Load configuration and return client, model"""
    config_path = os.path.expanduser('~/.solai.env')
    if not os.path.exists(config_path):
        setup_config()
    
    load_dotenv(config_path)
    
    # Check if old config format (has OPENAI_API_KEY but no AI_PROVIDER)
    if os.getenv('OPENAI_API_KEY') and not os.getenv('AI_PROVIDER'):
        migrate_old_config(config_path)
        load_dotenv(config_path)  # Reload after migration
    
    provider = os.getenv('AI_PROVIDER', 'local').lower()
    api_key = os.getenv('API_KEY') or os.getenv('OPENAI_API_KEY', 'not-needed')
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
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str or "connect" in error_str:
            console.print("\n[red]Error: Could not connect to AI server[/red]")
            console.print("[yellow]This might be because:[/yellow]")
            console.print("  • Msty Studio is not running (for local AI)")
            console.print("  • The API endpoint URL is incorrect")
            console.print("  • There's a network connectivity issue")
            console.print(f"\n[dim]Error details: {str(e)}[/dim]")
            
            if Confirm.ask("\nWould you like to reconfigure solai?"):
                config_path = os.path.expanduser('~/.solai.env')
                if os.path.exists(config_path):
                    os.remove(config_path)
                    console.print("[green]Configuration reset. Please run sol again to reconfigure.[/green]")
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
        # Error handling is done in get_command_suggestion
        sys.exit(1)

if __name__ == "__main__":
    main()
