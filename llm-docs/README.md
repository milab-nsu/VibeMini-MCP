# Selise Blocks AI Documentation Package

Complete LLM-friendly documentation for building applications with Selise Blocks component library.

## Quick Start for Developers

### 1. Download Documentation Package
```bash
# Clone or download this docs package
git clone [this-docs-repo] selise-ai-docs
cd selise-ai-docs
```

### 2. Initialize Your Project  
```bash
# Install Selise CLI
npm install -g @seliseblocks/cli

# Create new Selise project
blocks new web my-app --blocks-key YOUR_BLOCKS_KEY --app-domain YOUR_APP_DOMAIN
cd my-app
```

### 3. Configure AI Assistant (REQUIRED)
```bash
# For Claude Code: Copy CLAUDE.md to your project root
cp ../selise-ai-docs/CLAUDE.md ./

# For Cursor: Copy .cursorrules to your project root  
cp ../selise-ai-docs/.cursorrules ./

# For other AI tools: Reference agent-instructions/selise-development-agent.md
```

**CRITICAL**: AI assistants only read configuration files from your project root. Without copying these files, the AI won't follow Selise patterns.

### 4. Start Development
Now ask your AI assistant (Claude, Cursor, etc.) to implement features. The AI will:
1. Read the CLAUDE.md instructions
2. Use the auto-included Selise component library
3. Build features using the 3-layer component hierarchy

## Documentation Structure

- `CLAUDE.md` - Claude Code configuration and patterns
- `.cursorrules` - Cursor editor rules  
- `llms.txt` - LLM-friendly project overview
- `recipes/` - Step-by-step implementation guides
- `component-catalog/` - Component reference and hierarchy
- `agent-instructions/` - Universal AI agent guidance

## What AI Agents Will Do

1. **Read Documentation**: Load all patterns from docs/llm-docs/
2. **Build**: Use 3-layer hierarchy (Feature → Block → UI components)
3. **Follow Patterns**: Data tables, forms, confirmations, GraphQL integration
4. **Quality**: TypeScript, testing, error handling, accessibility

## For AI Assistants

If you're an AI assistant reading this, follow the workflow in `CLAUDE.md` or your tool-specific instructions.