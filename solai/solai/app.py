"""
solai - Your CLI Assistant
"""
import os
import sys
import click
import openai
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

def get_command_suggestion(query):
    """Get command suggestion from OpenAI"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a CLI assistant. For single commands, return the command followed by '||' and a one-sentence explanation. For multiple commands, each command should be on a new line with '||' and its explanation. If multiple commands, end with two sentences explaining the overall outcome."},
            {"role": "user", "content": query}
        ]
    )
    suggestion = response.choices[0].message.content.strip()
    
    # Parse and format the response
    lines = suggestion.split('\n')
    commands = []
    summary = None
    
    for line in lines:
        if '||' in line:
            cmd, explanation = line.split('||')
            commands.append((cmd.strip(), explanation.strip()))
        elif line.strip():  # Non-empty line without || is considered summary
            summary = line.strip()
    
    return {
        'commands': commands,
        'summary': summary
    }

@click.command()
@click.argument('query', nargs=-1)
def main(query):
    """CLI Assistant - Get command suggestions for your queries"""
    if not query:
        console.print("[red]Please provide a query[/red]")
        sys.exit(1)

    # Initialize OpenAI
    api_key = load_config()
    openai.api_key = api_key

    # Get the full query
    full_query = ' '.join(query)
    
    try:
        # Get command suggestion
        result = get_command_suggestion(full_query)
        
        # Display suggestion(s)
        console.print("\n[green]Suggested command(s):[/green]")
        
        # Display commands with numbering handled by Python
        for i, (cmd, explanation) in enumerate(result['commands'], 1):
            console.print(f"\n[yellow]{i}. {cmd}[/yellow]")
            console.print(f"[blue]→ {explanation}[/blue]")
        
        if result['summary']:
            console.print(f"\n[green]Summary:[/green]")
            console.print(f"[blue]{result['summary']}[/blue]\n")
        
        # Ask for confirmation
        if len(result['commands']) == 1:
            if Confirm.ask("Do you want to execute this command?"):
                os.system(result['commands'][0][0])
        else:
            for i, (cmd, _) in enumerate(result['commands'], 1):
                if Confirm.ask(f"Do you want to execute command {i}?"):
                    os.system(cmd)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    main()
