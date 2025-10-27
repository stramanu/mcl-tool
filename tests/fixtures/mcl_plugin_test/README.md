# mcl-plugin-test

Test fixture plugin for mcl integration testing.

## Usage

This plugin is installed during testing to verify plugin discovery and execution.

```bash
mcl test-plugin arg1 arg2          # Normal execution
mcl test-plugin --fail             # Return exit code 1
mcl test-plugin --echo hello world # Echo arguments
```
