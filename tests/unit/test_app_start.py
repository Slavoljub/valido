#!/usr/bin/env python3
"""
Test script to start the ValidoAI Flask application and diagnose any issues
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✅ App imported successfully")

    # Print some basic info
    print(f"📊 Available routes: {len(list(app.url_map.iter_rules()))}")
    print("🔧 App configuration:")
    print(f"   - Debug mode: {app.config.get('DEBUG', 'Not set')}")
    print(f"   - Host: {app.config.get('HOST', 'Not set')}")
    print(f"   - Port: {app.config.get('PORT', 'Not set')}")

    # List some routes
    print("📋 Sample routes:")
    for i, rule in enumerate(app.url_map.iter_rules()):
        if rule.endpoint != 'static' and i < 10:  # Show first 10 non-static routes
            methods = ','.join(rule.methods)
            print(f"   • {rule.rule} [{methods}] -> {rule.endpoint}")

    print("\n🚀 Starting Flask development server...")

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

except Exception as e:
    print(f"❌ Error starting application: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
