#!/bin/bash
# Frappe & ERPNext Smart Starter Script

echo "🧹 Checking and freeing up ports (8005, 9000, 11000, 13000)..."
kill -9 $(lsof -ti :8005 -ti :9000 -ti :11000 -ti :13000) 2>/dev/null || true
rm -f config/pids/* 2>/dev/null || true

echo "🚀 Starting ERPNext on http://localhost:8005 ..."
bench start
