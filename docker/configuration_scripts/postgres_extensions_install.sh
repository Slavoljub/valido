#!/bin/bash
# PostgreSQL Extensions Installation Script

echo "Installing PostgreSQL extensions..."

# Install required packages
apt-get update && apt-get install -y \
    postgresql-15-postgis-3 \
    postgresql-15-pgvector \
    postgresql-15-pg-stat-statements \
    postgresql-15-pg-buffercache \
    postgresql-15-pg-similarity \
    postgresql-15-pg-trgm \
    postgresql-15-pg-cron \
    postgresql-15-timescaledb \
    postgresql-15-pg-stat-monitor \
    postgresql-15-pg-repack \
    postgresql-15-pg-partman \
    postgresql-15-pg-qualstats \
    postgresql-15-pg-stat-kcache \
    postgresql-15-pg-wait-sampling \
    postgresql-15-auto-explain \
    postgresql-15-pg-hint-plan \
    postgresql-15-pg-visibility \
    postgresql-15-pg-freespacemap \
    postgresql-15-pg-prewarm

echo "PostgreSQL extensions installed successfully"
