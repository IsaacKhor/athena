#!/usr/bin/env bash

set -euo pipefail

base_dir="$1"
autograder_zip="$2"
submission_zip="$3"
reports_dir="$4"

# Make and enter the base directory
mkdir -p "$base_dir"
cd "$base_dir"

# Unzip the autograder here
echo "=== Unzipping the autograder ==="
unzip "$autograder_zip" -d "$base_dir"

# Make 'sumbission' subdir and place submission there
echo "=== Unzipping the submission ==="
mkdir -p "submission"
unzip "$submission_zip" -d "submission/"

# Run the run_autograder script that should be in here
mkdir -p 'results'
echo "=== Running autograder ==="
. run_autograder

# Copy results into the submission reports directory
echo "=== Copying results to reports directory ==="
mkdir -p "$reports_dir"
cp -r results/* "$reports_dir"

# Clean up after ourselves

echo "=== Cleaning up ==="
cd ..
rm -rf "$base_dir"