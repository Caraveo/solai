#!/bin/bash
# Install script to set up ! command alias
# This adds a shell function to your ~/.zshrc or ~/.bashrc

SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.zshrc"
fi

# Add function to shell rc file
if ! grep -q "function !" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" << 'EOF'

# x ! command alias
!() {
    x "$@"
}
EOF
    echo "Added ! function to $SHELL_RC"
    echo "Run: source $SHELL_RC"
    echo "Or restart your terminal"
else
    echo "! function already exists in $SHELL_RC"
fi

