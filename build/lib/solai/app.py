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
    console.print("2. MLX - Apple Silicon optimized local AI")
    console.print("3. OpenAI - Hyper Speed Most Efficient (Fastest)")
    
    choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"], default="1")
    
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
    elif choice == "2":
        # MLX setup
        console.print("\n[blue]Setting up MLX (Apple Silicon optimized)[/blue]")
        console.print("[dim]Make sure your MLX server is running locally[/dim]")
        
        base_url = Prompt.ask(
            "Enter MLX API base URL", 
            default="http://localhost:11973/v1"
        )
        api_key = Prompt.ask(
            "Enter API key (or press Enter for 'not-needed')", 
            default="not-needed"
        )
        model = Prompt.ask(
            "Enter model name", 
            default="mlx-community/Qwen2.5-0.5B-Instruct-4bit"
        )
        
        config_lines.append(f"AI_PROVIDER=mlx")
        config_lines.append(f"API_BASE_URL={base_url}")
        config_lines.append(f"API_KEY={api_key}")
        config_lines.append(f"MODEL={model}")
    else:
        # OpenAI Cloud setup
        console.print("\n[blue]Setting up OpenAI - Hyper Speed Most Efficient (Fastest)[/blue]")
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
        console.print("[cyan]Would you like to use OpenAI - Hyper Speed Most Efficient (Fastest) (your existing key) or switch to a local AI provider?[/cyan]")
        console.print("1. Keep OpenAI - Hyper Speed Most Efficient (Fastest) (use existing API key)")
        console.print("2. Switch to Local AI (Msty Studio)")
        console.print("3. Switch to MLX (Apple Silicon optimized)")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            # Migrate to new OpenAI format
            with open(config_path, 'w') as f:
                f.write(f"AI_PROVIDER=openai\n")
                f.write(f"API_KEY={old_api_key}\n")
                f.write(f"MODEL=gpt-3.5-turbo\n")
            console.print("[green]Configuration migrated to OpenAI - Hyper Speed Most Efficient (Fastest) format[/green]")
        elif choice == "2":
            # Switch to local AI (Msty Studio)
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
        else:
            # Switch to MLX
            console.print("\n[blue]Setting up MLX (Apple Silicon optimized)[/blue]")
            console.print("[dim]Make sure your MLX server is running locally[/dim]")
            
            base_url = Prompt.ask(
                "Enter MLX API base URL", 
                default="http://localhost:11973/v1"
            )
            api_key = Prompt.ask(
                "Enter API key (or press Enter for 'not-needed')", 
                default="not-needed"
            )
            model = Prompt.ask(
                "Enter model name", 
                default="mlx-community/Qwen2.5-0.5B-Instruct-4bit"
            )
            
            with open(config_path, 'w') as f:
                f.write(f"AI_PROVIDER=mlx\n")
                f.write(f"API_BASE_URL={base_url}\n")
                f.write(f"API_KEY={api_key}\n")
                f.write(f"MODEL={model}\n")
            console.print("[green]Configuration set to MLX[/green]")

def reconfigure():
    """Reconfigure existing settings"""
    config_path = os.path.expanduser('~/.solai.env')
    
    if not os.path.exists(config_path):
        console.print("[yellow]No existing configuration found. Running initial setup...[/yellow]")
        setup_config()
        return
    
    # Load existing configuration
    load_dotenv(config_path)
    current_provider = os.getenv('AI_PROVIDER', 'local').lower()
    current_api_key = os.getenv('API_KEY') or os.getenv('OPENAI_API_KEY', 'not-needed')
    
    # Set default model based on provider
    if current_provider == 'mlx':
        default_model = 'mlx-community/Qwen2.5-0.5B-Instruct-4bit'
        default_base_url = 'http://localhost:11973/v1'
    elif current_provider == 'local':
        default_model = 'mistral'
        default_base_url = 'http://localhost:1234/v1'
    else:
        default_model = 'gpt-3.5-turbo'
        default_base_url = 'http://localhost:1234/v1'
    
    current_model = os.getenv('MODEL', default_model)
    current_base_url = os.getenv('API_BASE_URL', default_base_url)
    
    console.print("[cyan]Current Configuration:[/cyan]")
    console.print(f"  Provider: {current_provider}")
    if current_provider in ['local', 'mlx']:
        console.print(f"  API Base URL: {current_base_url}")
    console.print(f"  Model: {current_model}")
    console.print(f"  API Key: {'*' * 20 if current_api_key != 'not-needed' else 'not-needed'}")
    
    console.print("\n[cyan]What would you like to configure?[/cyan]")
    console.print("1. Change AI Provider (Local AI ↔ MLX ↔ OpenAI - Hyper Speed Most Efficient (Fastest))")
    console.print("2. Update Model")
    if current_provider in ['local', 'mlx']:
        console.print("3. Update API Base URL")
        console.print("4. Update API Key")
        console.print("5. Reset all configuration (start fresh)")
        valid_choices = ["1", "2", "3", "4", "5"]
    else:
        console.print("3. Update API Key")
        console.print("4. Reset all configuration (start fresh)")
        valid_choices = ["1", "2", "3", "4"]
    
    choice = Prompt.ask("Enter your choice", choices=valid_choices, default="2")
    
    config_lines = []
    
    if choice == "1":
        # Switch provider
        console.print("\n[cyan]Choose your AI provider:[/cyan]")
        console.print("1. Local AI (Msty Studio) - Recommended for privacy")
        console.print("2. MLX - Apple Silicon optimized local AI")
        console.print("3. OpenAI - Hyper Speed Most Efficient (Fastest)")
        
        provider_choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"], default="1")
        
        if provider_choice == "1":
            # Switch to Local AI
            console.print("\n[blue]Configuring Local AI (Msty Studio)[/blue]")
            base_url = Prompt.ask(
                "Enter Msty Studio API base URL", 
                default=current_base_url if current_provider == 'local' else "http://localhost:1234/v1"
            )
            api_key = Prompt.ask(
                "Enter API key (or press Enter for 'not-needed')", 
                default="not-needed"
            )
            model = Prompt.ask(
                "Enter model name", 
                default=current_model if current_provider == 'local' else "mistral"
            )
            
            config_lines.append(f"AI_PROVIDER=local")
            config_lines.append(f"API_BASE_URL={base_url}")
            config_lines.append(f"API_KEY={api_key}")
            config_lines.append(f"MODEL={model}")
        elif provider_choice == "2":
            # Switch to MLX
            console.print("\n[blue]Configuring MLX (Apple Silicon optimized)[/blue]")
            base_url = Prompt.ask(
                "Enter MLX API base URL", 
                default=current_base_url if current_provider == 'mlx' else "http://localhost:11973/v1"
            )
            api_key = Prompt.ask(
                "Enter API key (or press Enter for 'not-needed')", 
                default="not-needed"
            )
            model = Prompt.ask(
                "Enter model name", 
                default=current_model if current_provider == 'mlx' else "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
            )
            
            config_lines.append(f"AI_PROVIDER=mlx")
            config_lines.append(f"API_BASE_URL={base_url}")
            config_lines.append(f"API_KEY={api_key}")
            config_lines.append(f"MODEL={model}")
        else:
            # Switch to OpenAI Cloud
            console.print("\n[blue]Configuring OpenAI - Hyper Speed Most Efficient (Fastest)[/blue]")
            console.print("[dim]Get your API key from: https://platform.openai.com/api-keys[/dim]")
            
            api_key = Prompt.ask("Enter your OpenAI API key", default=current_api_key if current_api_key != 'not-needed' else "")
            model = Prompt.ask("Enter model name", default=current_model if current_provider == 'openai' else "gpt-3.5-turbo")
            
            config_lines.append(f"AI_PROVIDER=openai")
            config_lines.append(f"API_KEY={api_key}")
            config_lines.append(f"MODEL={model}")
    
    elif choice == "2":
        # Update model only
        new_model = Prompt.ask("Enter new model name", default=current_model)
        
        config_lines.append(f"AI_PROVIDER={current_provider}")
        if current_provider in ['local', 'mlx']:
            config_lines.append(f"API_BASE_URL={current_base_url}")
            config_lines.append(f"API_KEY={current_api_key}")
        config_lines.append(f"MODEL={new_model}")
    
    elif choice == "3" and current_provider in ['local', 'mlx']:
        # Update API Base URL (local/MLX only)
        new_base_url = Prompt.ask("Enter new API base URL", default=current_base_url)
        
        config_lines.append(f"AI_PROVIDER={current_provider}")
        config_lines.append(f"API_BASE_URL={new_base_url}")
        config_lines.append(f"API_KEY={current_api_key}")
        config_lines.append(f"MODEL={current_model}")
    
    elif choice == "3" and current_provider == 'openai':
        # Update API Key (OpenAI)
        new_api_key = Prompt.ask("Enter new API key", default=current_api_key if current_api_key != 'not-needed' else "")
        
        config_lines.append(f"AI_PROVIDER=openai")
        config_lines.append(f"API_KEY={new_api_key}")
        config_lines.append(f"MODEL={current_model}")
    
    elif choice == "4" and current_provider in ['local', 'mlx']:
        # Update API Key (local/MLX)
        new_api_key = Prompt.ask("Enter new API key (or press Enter for 'not-needed')", default=current_api_key)
        
        config_lines.append(f"AI_PROVIDER={current_provider}")
        config_lines.append(f"API_BASE_URL={current_base_url}")
        config_lines.append(f"API_KEY={new_api_key}")
        config_lines.append(f"MODEL={current_model}")
    
    elif choice == "4" and current_provider == 'openai':
        # Reset all (for OpenAI, option 4 is reset)
        if Confirm.ask("[yellow]Are you sure you want to reset all configuration?[/yellow]"):
            os.remove(config_path)
            console.print("[green]Configuration reset. Running initial setup...[/green]")
            setup_config()
            return
        else:
            console.print("[yellow]Configuration reset cancelled.[/yellow]")
            return
    
    elif choice == "5":
        # Reset all (for local, option 5 is reset)
        if Confirm.ask("[yellow]Are you sure you want to reset all configuration?[/yellow]"):
            os.remove(config_path)
            console.print("[green]Configuration reset. Running initial setup...[/green]")
            setup_config()
            return
        else:
            console.print("[yellow]Configuration reset cancelled.[/yellow]")
            return
    
    # Write updated configuration
    with open(config_path, 'w') as f:
        f.write('\n'.join(config_lines) + '\n')
    
    console.print(f"\n[green]Configuration updated successfully![/green]")
    console.print(f"[dim]Saved to {config_path}[/dim]")

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
    
    # Set defaults based on provider
    if provider == 'mlx':
        default_model = 'mlx-community/Qwen2.5-0.5B-Instruct-4bit'
        default_base_url = 'http://localhost:11973/v1'
    elif provider == 'local':
        default_model = 'mistral'
        default_base_url = 'http://localhost:1234/v1'
    else:
        default_model = 'gpt-3.5-turbo'
        default_base_url = 'http://localhost:1234/v1'
    
    model = os.getenv('MODEL', default_model)
    base_url = os.getenv('API_BASE_URL', default_base_url)
    
    # Initialize client based on provider
    if provider in ['local', 'mlx']:
        # Local AI (Msty Studio) or MLX
        # OpenAI client requires api_key parameter even for local servers
        # Use a dummy value if not provided
        if api_key and api_key != 'not-needed':
            client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )
        else:
            # Use dummy key for local servers that don't require authentication
            client = OpenAI(
                base_url=base_url,
                api_key="dummy-key-not-needed"
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
        if not response.choices or not response.choices[0].message:
            raise Exception("Empty response from AI server")
        
        result = response.choices[0].message.content
        if not result:
            raise Exception("AI server returned empty content")
        
        result = result.strip()
        
        # Split command and explanation
        if '||' in result:
            command, explanation = result.split('||', 1)
            return command.strip(), explanation.strip()
        return result.strip(), ""
    except Exception as e:
        # If local AI fails, provide helpful error message
        error_str = str(e).lower()
        error_type = type(e).__name__
        
        # Check for model not found errors
        if "model" in error_str and ("not found" in error_str or "not available" in error_str or "does not exist" in error_str):
            console.print("\n[red]Error: Model not found[/red]")
            console.print("[yellow]The model you specified is not available in your AI server.[/yellow]")
            console.print(f"\n[dim]Error details: {str(e)}[/dim]")
            console.print("\n[cyan]Common solutions:[/cyan]")
            console.print("  1. Check that the model is loaded in Msty Studio")
            console.print("  2. Verify the model name matches exactly (case-sensitive)")
            console.print("  3. Use 'sol --configure' to update the model name")
            console.print("\n[dim]Common model names: llama, mistral, codellama, phi, gemma, etc.[/dim]")
            
            try:
                if Confirm.ask("\nWould you like to reconfigure the model now?"):
                    reconfigure()
            except (KeyboardInterrupt, EOFError):
                pass
        
        # Check for connection-related errors
        elif any(keyword in error_str for keyword in ["connection", "refused", "connect", "timeout", "unreachable"]):
            console.print("\n[red]Error: Could not connect to AI server[/red]")
            console.print("[yellow]This might be because:[/yellow]")
            console.print("  • Msty Studio is not running (for local AI)")
            console.print("  • The API endpoint URL is incorrect")
            console.print("  • There's a network connectivity issue")
            console.print(f"\n[dim]Error type: {error_type}[/dim]")
            console.print(f"[dim]Error details: {str(e)}[/dim]")
            
            try:
                if Confirm.ask("\nWould you like to reconfigure solai?"):
                    config_path = os.path.expanduser('~/.solai.env')
                    if os.path.exists(config_path):
                        os.remove(config_path)
                        console.print("[green]Configuration reset. Please run sol again to reconfigure.[/green]")
            except (KeyboardInterrupt, EOFError):
                pass
        else:
            # Other types of errors
            console.print(f"\n[red]Error: {error_type}[/red]")
            console.print(f"[yellow]{str(e)}[/yellow]")
            console.print(f"\n[dim]Full error: {repr(e)}[/dim]")
        raise

@click.command()
@click.argument('query', nargs=-1, required=False)
@click.option('--configure', '-c', is_flag=True, help='Configure solai settings')
def main(query, configure):
    """CLI Assistant - Get command suggestions for your queries"""
    if configure:
        reconfigure()
        return
    
    if not query:
        console.print("[red]Please provide a query[/red]")
        console.print("[dim]Use 'sol --configure' to configure settings[/dim]")
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
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        # If error wasn't already displayed in get_command_suggestion, show it here
        # (This handles cases where get_command_suggestion didn't catch it)
        error_str = str(e).lower()
        if "connection" not in error_str and "refused" not in error_str and "connect" not in error_str:
            console.print(f"\n[red]Unexpected error: {type(e).__name__}[/red]")
            console.print(f"[yellow]{str(e)}[/yellow]")
        sys.exit(1)

if __name__ == "__main__":
    main()
