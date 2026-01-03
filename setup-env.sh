#!/usr/bin/env bash

# Get absolute directory of this script (works with source)
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PATH="$script_dir/bin:$PATH"

echo "✅ cerrfix command enabled"
echo "   Added to PATH: $script_dir/bin"


