# cdd-configdrift-BaselineDiff
Compares current configuration against a known good baseline, highlighting differences in a readable format (e.g., using `diff` or similar library). - Focused on This category encompasses tools designed to detect changes in configuration files over time. This allows security teams to identify unauthorized modifications, deviations from established baselines, and potential misconfigurations that could introduce security risks. The tools track and highlight differences across versions, aiding in rapid troubleshooting and remediation.

## Install
`git clone https://github.com/ShadowStrikeHQ/cdd-configdrift-baselinediff`

## Usage
`./cdd-configdrift-baselinediff [params]`

## Parameters
- `-h`: Show help message and exit
- `--format`: No description provided
- `--ignore`: List of keys to ignore in the diff
- `--output`: Path to the output file for the diff. If not specified, diff is printed to stdout.
- `--indent`: No description provided
- `--no-color`: Disable color output.

## License
Copyright (c) ShadowStrikeHQ
