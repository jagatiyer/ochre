#!/bin/bash

# Create backups folder if not exists
mkdir -p backups

timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
backup_dir="backups/backup_$timestamp"

mkdir "$backup_dir"

echo "Backing up project to $backup_dir ..."

# Copy the entire Django project
rsync -av --exclude="venv" --exclude="backups" ./ "$backup_dir/project"

# Copy SQLite database
cp db.sqlite3 "$backup_dir/db.sqlite3"

echo "Backup completed successfully."
echo "Backup folder: $backup_dir"
