#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./restore.sh <backup_folder>"
  echo "Example: ./restore.sh backups/backup_2025-12-09_13-20-00"
  exit 1
fi

backup_folder="$1"

if [ ! -d "$backup_folder" ]; then
    echo "Backup folder does not exist: $backup_folder"
    exit 1
fi

echo "Restoring backup from $backup_folder ..."

# Restore project files
rsync -av --delete "$backup_folder/project/" ./

# Restore DB
cp "$backup_folder/db.sqlite3" ./db.sqlite3

echo "Restore complete."
echo "Run: python manage.py runserver"
