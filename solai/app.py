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
from . import __version__

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

def list_available_models(base_url, api_key=None):
    """List available models from local AI server"""
    try:
        # Create a temporary client to fetch models
        if api_key and api_key != 'not-needed':
            temp_client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            temp_client = OpenAI(base_url=base_url, api_key="dummy-key-not-needed")
        
        # Try to fetch models list
        models_response = temp_client.models.list()
        models = [model.id for model in models_response.data]
        
        if models:
            console.print("\n[green]Available models:[/green]")
            for i, model_name in enumerate(models, 1):
                console.print(f"  {i}. {model_name}")
            console.print()  # Empty line for spacing
            return models
        else:
            console.print("\n[yellow]No models found or models endpoint not available[/yellow]")
            return []
    except Exception as e:
        # If listing fails, just return empty list - user can still type model name
        console.print(f"\n[yellow]Could not fetch model list: {str(e)}[/yellow]")
        console.print("[dim]You can still enter a model name manually[/dim]\n")
        return []

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
        # Try to list available models
        console.print("\n[cyan]Fetching available models from server...[/cyan]")
        available_models = list_available_models(base_url, api_key)
        
        if available_models:
            console.print("[cyan]You can:[/cyan]")
            console.print("  • Type a number from the list above")
            console.print("  • Type the full model name")
            model_input = Prompt.ask("Enter model name or number", default="mistral")
            
            # Check if user entered a number
            try:
                model_index = int(model_input) - 1
                if 0 <= model_index < len(available_models):
                    model = available_models[model_index]
                    console.print(f"[green]Selected: {model}[/green]")
                else:
                    model = model_input
            except ValueError:
                # Not a number, use as model name
                model = model_input
        else:
            model = Prompt.ask("Enter model name", default="mistral")
        
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
        # Try to list available models
        console.print("\n[cyan]Fetching available models from server...[/cyan]")
        available_models = list_available_models(base_url, api_key)
        
        if available_models:
            console.print("[cyan]You can:[/cyan]")
            console.print("  • Type a number from the list above")
            console.print("  • Type the full model name")
            model_input = Prompt.ask("Enter model name or number", default="mlx-community/Qwen2.5-0.5B-Instruct-4bit")
            
            # Check if user entered a number
            try:
                model_index = int(model_input) - 1
                if 0 <= model_index < len(available_models):
                    model = available_models[model_index]
                    console.print(f"[green]Selected: {model}[/green]")
                else:
                    model = model_input
            except ValueError:
                # Not a number, use as model name
                model = model_input
        else:
            model = Prompt.ask("Enter model name", default="mlx-community/Qwen2.5-0.5B-Instruct-4bit")
        
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
            # Try to list available models
            console.print("\n[cyan]Fetching available models from server...[/cyan]")
            available_models = list_available_models(base_url, api_key)
            
            if available_models:
                console.print("[cyan]You can:[/cyan]")
                console.print("  • Type a number from the list above")
                console.print("  • Type the full model name")
                model_input = Prompt.ask("Enter model name or number", default="mistral")
                
                # Check if user entered a number
                try:
                    model_index = int(model_input) - 1
                    if 0 <= model_index < len(available_models):
                        model = available_models[model_index]
                        console.print(f"[green]Selected: {model}[/green]")
                    else:
                        model = model_input
                except ValueError:
                    # Not a number, use as model name
                    model = model_input
            else:
                model = Prompt.ask("Enter model name", default="mistral")
            
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
            # Try to list available models
            console.print("\n[cyan]Fetching available models from server...[/cyan]")
            available_models = list_available_models(base_url, api_key)
            
            if available_models:
                console.print("[cyan]You can:[/cyan]")
                console.print("  • Type a number from the list above")
                console.print("  • Type the full model name")
                model_input = Prompt.ask("Enter model name or number", default="mlx-community/Qwen2.5-0.5B-Instruct-4bit")
                
                # Check if user entered a number
                try:
                    model_index = int(model_input) - 1
                    if 0 <= model_index < len(available_models):
                        model = available_models[model_index]
                        console.print(f"[green]Selected: {model}[/green]")
                    else:
                        model = model_input
                except ValueError:
                    # Not a number, use as model name
                    model = model_input
            else:
                model = Prompt.ask("Enter model name", default="mlx-community/Qwen2.5-0.5B-Instruct-4bit")
            
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
            # Try to list available models
            console.print("\n[cyan]Fetching available models from server...[/cyan]")
            available_models = list_available_models(base_url, api_key)
            
            if available_models:
                console.print("[cyan]You can:[/cyan]")
                console.print("  • Type a number from the list above")
                console.print("  • Type the full model name")
                model_input = Prompt.ask("Enter model name or number", default=current_model if current_provider == 'local' else "mistral")
                
                # Check if user entered a number
                try:
                    model_index = int(model_input) - 1
                    if 0 <= model_index < len(available_models):
                        model = available_models[model_index]
                        console.print(f"[green]Selected: {model}[/green]")
                    else:
                        model = model_input
                except ValueError:
                    # Not a number, use as model name
                    model = model_input
            else:
                model = Prompt.ask("Enter model name", default=current_model if current_provider == 'local' else "mistral")
            
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
            # Try to list available models
            console.print("\n[cyan]Fetching available models from server...[/cyan]")
            available_models = list_available_models(base_url, api_key)
            
            if available_models:
                console.print("[cyan]You can:[/cyan]")
                console.print("  • Type a number from the list above")
                console.print("  • Type the full model name")
                model_input = Prompt.ask("Enter model name or number", default=current_model if current_provider == 'mlx' else "mlx-community/Qwen2.5-0.5B-Instruct-4bit")
                
                # Check if user entered a number
                try:
                    model_index = int(model_input) - 1
                    if 0 <= model_index < len(available_models):
                        model = available_models[model_index]
                        console.print(f"[green]Selected: {model}[/green]")
                    else:
                        model = model_input
                except ValueError:
                    # Not a number, use as model name
                    model = model_input
            else:
                model = Prompt.ask("Enter model name", default=current_model if current_provider == 'mlx' else "mlx-community/Qwen2.5-0.5B-Instruct-4bit")
            
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
        if current_provider in ['local', 'mlx']:
            # For local providers, try to list available models
            console.print("\n[cyan]Fetching available models from server...[/cyan]")
            available_models = list_available_models(current_base_url, current_api_key)
            
            if available_models:
                console.print("[cyan]You can:[/cyan]")
                console.print("  • Type a number from the list above")
                console.print("  • Type the full model name")
                console.print("  • Press Enter to keep current model")
                model_input = Prompt.ask("Enter model name or number", default=current_model)
                
                # Check if user entered a number
                try:
                    model_index = int(model_input) - 1
                    if 0 <= model_index < len(available_models):
                        new_model = available_models[model_index]
                        console.print(f"[green]Selected: {new_model}[/green]")
                    else:
                        new_model = model_input
                except ValueError:
                    # Not a number, use as model name
                    new_model = model_input
            else:
                new_model = Prompt.ask("Enter new model name", default=current_model)
        else:
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

def extract_commands_from_response(result, trigger_words=None):
    """Extract commands from AI response using trigger words and code blocks"""
    if trigger_words is None:
        trigger_words = ['```bash', '```sh', '```shell', '```', 'COMMAND:', 'EXECUTE:', 'RUN:']
    
    commands = []
    
    # First, prioritize code blocks - they're the cleanest format
    if '```' in result:
        parts = result.split('```')
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Odd indices are code blocks
                lines = part.strip().split('\n')
                # Skip language identifier (bash, sh, shell)
                if lines and lines[0].lower() in ['bash', 'sh', 'shell']:
                    lines = lines[1:]
                # Collect all non-empty lines as commands
                code_block_commands = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('//'):
                        code_block_commands.append(line)
                
                if code_block_commands:
                    # If multiple lines, treat each as separate command
                    # If single line, treat as one command
                    if len(code_block_commands) == 1:
                        commands.append(code_block_commands[0])
                    else:
                        # Multiple commands in one block - split by newlines
                        commands.extend(code_block_commands)
        
        # If we found commands in code blocks, return them
        if commands:
            return commands
    
    # Fallback to trigger word extraction if no code blocks found
    lines = result.split('\n')
    in_command_section = False
    current_command = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if we hit a trigger word
        for trigger in trigger_words:
            line_upper = line.upper()
            trigger_upper = trigger.upper()
            if trigger_upper in line_upper:
                in_command_section = True
                # Extract command from the same line if present (case-insensitive)
                # Find the trigger word position (case-insensitive)
                trigger_index = line_upper.find(trigger_upper)
                if trigger_index != -1:
                    # Extract everything after the trigger word
                    after_trigger = line[trigger_index + len(trigger):].strip()
                    if after_trigger:
                        current_command.append(after_trigger)
                break
        
        if in_command_section:
            # Skip markdown code block markers
            if line_stripped in ['```', '```bash', '```sh', '```shell']:
                # If we hit closing code block, end command collection
                if current_command:
                    cmd = '\n'.join(current_command).strip()
                    if cmd:
                        commands.append(cmd)
                    current_command = []
                in_command_section = False
                continue
            
            # Stop collecting if we hit another section marker
            if (line_stripped.startswith('**') or 
                line_stripped.startswith('[') or 
                line_stripped.startswith('---') or
                'Reasoning' in line_stripped or 
                'Answer' in line_stripped or
                line_stripped.upper().startswith('COMMAND:') or
                line_stripped.upper().startswith('EXECUTE:') or
                line_stripped.upper().startswith('RUN:')):
                if current_command:
                    cmd = '\n'.join(current_command).strip()
                    if cmd:
                        commands.append(cmd)
                    current_command = []
                # If it's a new trigger, start new command section
                if not (line_stripped.upper().startswith('COMMAND:') or
                        line_stripped.upper().startswith('EXECUTE:') or
                        line_stripped.upper().startswith('RUN:')):
                    in_command_section = False
                continue
            
            # Skip lines that are clearly not commands (too long, contain reasoning words)
            if len(line_stripped) > 200 or any(word in line_stripped.lower() for word in ['reasoning', 'explanation', 'this will', 'note:', 'tip:']):
                if current_command:
                    # End current command if we hit explanatory text
                    cmd = '\n'.join(current_command).strip()
                    if cmd:
                        commands.append(cmd)
                    current_command = []
                in_command_section = False
                continue
            
            # Collect command lines
            if line_stripped:
                # Clean up markdown formatting
                cleaned = line.replace('`', '').replace('**', '').strip()
                if cleaned:
                    current_command.append(cleaned)
            elif current_command:
                # Empty line after commands - end this command
                cmd = '\n'.join(current_command).strip()
                if cmd:
                    commands.append(cmd)
                current_command = []
                in_command_section = False
    
    # Add last command if any
    if current_command:
        cmd = '\n'.join(current_command).strip()
        if cmd:
            commands.append(cmd)
    
    # If no trigger found, try to find commands in code blocks or after separators
    if not commands:
        # Look for code blocks
        if '```' in result:
            parts = result.split('```')
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are code blocks
                    lines = part.strip().split('\n')
                    # Skip language identifier
                    if lines and lines[0] in ['bash', 'sh', 'shell']:
                        lines = lines[1:]
                    cmd = '\n'.join(lines).strip()
                    if cmd:
                        commands.append(cmd)
        
        # Fallback: look for lines with || separator (old format)
        all_lines = result.split('\n')
        for line in all_lines:
            if '||' in line:
                cmd = line.split('||')[0].strip()
                if cmd:
                    commands.append(cmd)
                    break
    
    return commands

def get_command_suggestion(client, model, query):
    """Get command suggestion from AI with reasoning support"""
    os_type = get_system_info()
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a CLI assistant for {os_type}. Provide your reasoning first, explaining what the command(s) will do and why. Then put all commands to execute in a code block. Format: Provide reasoning (explaining what the commands do), then use ```bash followed by the command(s) to execute, one per line, ending with ```. You can provide multiple commands for complex tasks. Ensure all commands are compatible with {os_type}."
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
        
        # Extract commands using trigger words
        commands = extract_commands_from_response(result)
        
        # Return full response and extracted commands
        return result, commands
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
@click.option('--configure', '-c', is_flag=True, help='Configure x settings')
@click.option('--admin', '-a', is_flag=True, help='Run commands with sudo (administrative privileges)')
@click.option('--version', '-v', is_flag=True, help='Show version information')
def main(query, configure, admin, version):
    """CLI Assistant - Get command suggestions for your queries
    
    Examples:
        x find large files
        x --configure
        x --admin install package
        x --version
    """
    if version:
        console.print(f"[cyan]x (xcli-ai) version {__version__}[/cyan]")
        console.print(f"[dim]Install via: pip install xcli-ai[/dim]")
        console.print(f"[dim]GitHub: https://github.com/caraveo/solai[/dim]")
        return
    
    if configure:
        reconfigure()
        return
    
    if not query:
        console.print("[red]Please provide a query[/red]")
        console.print("[dim]Use 'x --configure' to configure settings[/dim]")
        console.print("[dim]Use 'x --help' for more information[/dim]")
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
        # Get full response and commands
        full_response, commands = get_command_suggestion(client, model, full_query)
        
        # Extract reasoning (everything before code blocks or trigger words)
        reasoning = full_response
        # Find the earliest code block or trigger word position
        earliest_pos = len(reasoning)
        
        # Check for code blocks first (most common format)
        if '```' in reasoning:
            pos = reasoning.find('```')
            if pos < earliest_pos:
                earliest_pos = pos
        
        # Check for trigger words
        for trigger in ['COMMAND:', 'EXECUTE:', 'RUN:']:
            trigger_upper = trigger.upper()
            reasoning_upper = reasoning.upper()
            if trigger_upper in reasoning_upper:
                pos = reasoning_upper.find(trigger_upper)
                if pos < earliest_pos:
                    earliest_pos = pos
        
        if earliest_pos < len(reasoning):
            reasoning = reasoning[:earliest_pos].strip()
        
        # Clean up reasoning - remove markdown headers and formatting
        reasoning_lines = reasoning.split('\n')
        cleaned_reasoning = []
        for line in reasoning_lines:
            line_stripped = line.strip()
            # Skip markdown headers like **[Reasoning]**, [Reasoning], **Answer**, etc.
            if (line_stripped.startswith('**') and line_stripped.endswith('**') and 
                ('Reasoning' in line_stripped or 'Answer' in line_stripped or 'Command' in line_stripped)):
                continue
            if (line_stripped.startswith('[') and line_stripped.endswith(']') and 
                ('Reasoning' in line_stripped or 'Answer' in line_stripped)):
                continue
            # Skip separator lines
            if line_stripped.startswith('---') or line_stripped == '---':
                continue
            cleaned_reasoning.append(line)
        
        reasoning = '\n'.join(cleaned_reasoning).strip()
        
        # Display reasoning
        if reasoning:
            console.print("\n[cyan]Command Reasoning:[/cyan]")
            console.print(reasoning)
            console.print()
        
        if not commands:
            console.print("[yellow]No commands found in response. The AI may have only provided reasoning.[/yellow]")
            return
        
        # Display commands to be executed
        if admin:
            console.print(f"[green]Commands to Execute ({len(commands)}) [with sudo]:[/green]")
        else:
            console.print(f"[green]Commands to Execute ({len(commands)}):[/green]")
        for i, cmd in enumerate(commands, 1):
            if admin:
                # Show sudo prefix in display
                display_cmd = f"sudo {cmd}" if not cmd.strip().startswith('sudo') else cmd
                console.print(f"[yellow]{display_cmd}[/yellow]")
            else:
                console.print(f"[yellow]{cmd}[/yellow]")
        console.print()
        
        # Ask for confirmation
        if admin:
            console.print("[yellow]⚠️  Warning: Commands will run with sudo (administrative privileges)[/yellow]")
        if Confirm.ask("Do you want to execute these command(s)?"):
            for i, command in enumerate(commands, 1):
                if len(commands) > 1:
                    console.print(f"\n[cyan]Executing command {i}/{len(commands)}:[/cyan]")
                else:
                    console.print(f"\n[cyan]Executing:[/cyan]")
                
                # Prepend sudo if admin flag is set and command doesn't already have it
                if admin:
                    command_stripped = command.strip()
                    if not command_stripped.startswith('sudo'):
                        command = f"sudo {command}"
                    console.print(f"[dim]{command}[/dim]")
                else:
                    console.print(f"[dim]{command}[/dim]")
                
                # Execute the command
                exit_code = os.system(command)
                
                if exit_code != 0:
                    console.print(f"[yellow]Command exited with code {exit_code}[/yellow]")
                    if len(commands) > 1:
                        if not Confirm.ask("Continue with remaining commands?"):
                            break
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
