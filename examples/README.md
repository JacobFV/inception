# Inception API Examples

This directory contains example scripts demonstrating how to use the Inception API client library and CLI tool.

## Files Overview

1. `basic_usage.py` - Basic example of using the Python client library
   - Creating a chat
   - Sending messages
   - Getting streaming responses
   - Listing chats

2. `advanced_usage.py` - Advanced features of the Python client library
   - Custom model selection
   - Session management
   - Complex chat interactions
   - Chat cleanup

3. `cli_examples.sh` - Comprehensive CLI usage examples
   - Authentication commands
   - Chat management
   - Interactive chat usage
   - Example workflows

## Running the Examples

### Python Library Examples

1. Make sure you have the Inception API library installed:
```bash
pip install -e .
```

2. Run the basic example:
```bash
python examples/basic_usage.py
```

3. Run the advanced example:
```bash
python examples/advanced_usage.py
```

### CLI Examples

1. View the CLI examples:
```bash
cat examples/cli_examples.sh
```

2. Try the commands individually from your terminal.

## Notes

- The Python examples will open a browser window for authentication
- Replace `<chat_id>` in the CLI examples with actual chat IDs
- All examples include proper error handling and demonstrate best practices
- The examples are designed to be self-contained and easy to understand

## Additional Resources

- Main README.md in the root directory for complete documentation
- API reference for detailed information about available methods
- CLI documentation for all available commands 