#!/usr/bin/env python3
"""
MCP Configuration Validator
This script validates the MCP configuration file and identifies syntax errors.
"""

import json
import sys
import os
from pathlib import Path

# Ensure UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def validate_mcp_config(file_path):
    """Validate MCP configuration file and provide detailed error analysis."""
    
    print(f"🔍 Validating MCP configuration file: {file_path}")
    print("=" * 60)
    
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 File content preview:")
        print("-" * 30)
        lines = content.split('\n')
        for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
            print(f"{i:2d} | {line}")
        print("-" * 30)
        
        # Try to parse JSON
        print("\n🔧 Attempting JSON parsing...")
        config = json.loads(content)
        
        print("✅ JSON parsing successful!")
        print(f"📊 Configuration contains {len(config.get('mcpServers', {}))} MCP servers")
        
        # Validate each server configuration
        servers = config.get('mcpServers', {})
        for server_name, server_config in servers.items():
            print(f"\n🔍 Validating server: {server_name}")
            
            # Check required fields
            if 'command' not in server_config:
                print(f"❌ Missing 'command' field in server: {server_name}")
            else:
                print(f"✅ Command: {server_config['command']}")
            
            if 'args' not in server_config:
                print(f"❌ Missing 'args' field in server: {server_name}")
            else:
                print(f"✅ Args: {server_config['args']}")
            
            # Check for env configuration
            if 'env' in server_config:
                print(f"✅ Environment variables: {len(server_config['env'])} variables")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed!")
        print(f"📍 Error location: Line {e.lineno}, Column {e.colno}")
        print(f"💡 Error message: {e.msg}")
        print(f"📝 Context: {e.doc[e.pos-20:e.pos+20]}")
        
        # Show the problematic line
        if e.lineno > 0 and e.lineno <= len(lines):
            print(f"\n🔴 Problematic line {e.lineno}:")
            print(f"   {lines[e.lineno-1]}")
            
            # Show surrounding lines for context
            start_line = max(1, e.lineno - 3)
            end_line = min(len(lines), e.lineno + 2)
            
            print(f"\n📋 Context (lines {start_line}-{end_line}):")
            for i in range(start_line, end_line + 1):
                marker = "👉" if i == e.lineno else "   "
                print(f"{marker} {i:2d} | {lines[i-1]}")
        
        return False
    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def analyze_syntax_issues(file_path):
    """Analyze common syntax issues in MCP configuration."""
    
    print("\n🔬 Analyzing common syntax issues...")
    print("-" * 40)
    
    issues_found = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check for common issues
        brace_count = 0
        bracket_count = 0
        in_env_block = False
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Count braces
            brace_count += line.count('{') - line.count('}')
            bracket_count += line.count('[') - line.count(']')
            
            # Check for env blocks
            if '"env": {' in line:
                in_env_block = True
                print(f"📍 Found env block start at line {i}")
            elif in_env_block and '}' in line:
                in_env_block = False
                print(f"📍 Found env block end at line {i}")
            elif in_env_block:
                print(f"🔄 Continuing env block at line {i}: {line[:50]}...")
        
        print(f"\n📊 Brace balance: {brace_count} (should be 0)")
        print(f"📊 Bracket balance: {bracket_count} (should be 0)")
        
        if brace_count != 0:
            issues_found.append(f"Unbalanced braces: {brace_count}")
        
        if in_env_block:
            issues_found.append("Unclosed env block")
        
        if issues_found:
            print(f"\n⚠️  Issues found: {', '.join(issues_found)}")
        else:
            print("\n✅ No obvious syntax issues detected")
        
        return issues_found
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return []

if __name__ == "__main__":
    # Get the MCP config file path
    config_path = Path("../../../../../.gemini/antigravity/mcp_config.json")
    
    if not config_path.exists():
        print(f"❌ Configuration file not found at: {config_path}")
        sys.exit(1)
    
    # Validate the configuration
    is_valid = validate_mcp_config(config_path)
    
    # Analyze syntax issues
    issues = analyze_syntax_issues(config_path)
    
    print("\n" + "=" * 60)
    if is_valid:
        print("🎉 MCP Configuration is VALID!")
    else:
        print("💥 MCP Configuration has ERRORS!")
        print("🔧 Suggested fixes:")
        if issues:
            for issue in issues:
                print(f"   • {issue}")
        print("\n📝 Manual inspection recommended for complex issues")
    
    sys.exit(0 if is_valid else 1)