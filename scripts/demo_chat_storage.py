#!/usr/bin/env python3
"""
Demo script for Chat Artifact Storage System
Demonstrates the artifact-based chat storage functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.ai_local_models.chat_storage import ChatArtifactStorage, ChatArtifact


def demo_chat_storage():
    """Demonstrate the chat storage system"""
    print("🤖 Chat Artifact Storage Demo")
    print("=" * 50)

    # Initialize storage
    storage = ChatArtifactStorage()

    # Create a chat session
    print("\n1. Creating chat session...")
    session_id = storage.create_session(
        session_id="demo_session_1",
        user_id="demo_user",
        title="AI Assistant Demo",
        model_name="llama2-7b"
    )
    print(f"✅ Created session: {session_id}")

    # Save some chat messages
    print("\n2. Saving chat messages...")
    messages = [
        ("user", "Hello! Can you help me understand Python decorators?"),
        ("assistant", "Of course! Python decorators are a powerful feature that allows you to modify the behavior of functions or classes. They work by taking a function as input and returning a modified version of that function."),
        ("user", "That sounds interesting. Can you show me a simple example?"),
        ("assistant", "Here's a simple example of a decorator that times function execution:\n\n```python\nimport time\n\ndef timing_decorator(func):\n    def wrapper(*args, **kwargs):\n        start_time = time.time()\n        result = func(*args, **kwargs)\n        end_time = time.time()\n        print(f\"Function {func.__name__} took {end_time - start_time:.2f} seconds\")\n        return result\n    return wrapper\n\n@timing_decorator\ndef slow_function():\n    time.sleep(1)\n    return \"Done!\"\n\nslow_function()\n```")
    ]

    for role, content in messages:
        message_id = storage.save_message(
            session_id=session_id,
            role=role,
            content=content,
            metadata={"demo": True}
        )
        print(f"✅ Saved {role} message: {message_id}")

    # Create an artifact from the conversation
    print("\n3. Creating conversation artifact...")
    artifact = storage.create_artifact(
        session_id=session_id,
        title="Python Decorators Tutorial",
        content="A conversation about Python decorators with examples and explanations.",
        artifact_type="tutorial",
        metadata={
            "topic": "Python decorators",
            "difficulty": "beginner",
            "tags": ["python", "decorators", "tutorial"]
        }
    )
    print(f"✅ Created artifact: {artifact.artifact_id}")
    print(f"   Title: {artifact.title}")
    print(f"   Type: {artifact.artifact_type}")

    # Get chat history
    print("\n4. Retrieving chat history...")
    history = storage.get_chat_history(session_id)
    print(f"✅ Retrieved {len(history)} messages")
    for msg in history[-2:]:  # Show last 2 messages
        print(f"   {msg['role']}: {msg['content'][:50]}...")

    # Search for artifacts
    print("\n5. Searching artifacts...")
    search_results = storage.search_artifacts("Python")
    print(f"✅ Found {len(search_results)} artifacts containing 'Python'")
    for artifact in search_results:
        print(f"   - {artifact.title} (Type: {artifact.artifact_type})")

    # Update the artifact
    print("\n6. Updating artifact...")
    updated_artifact = storage.update_artifact(
        artifact_id=artifact.artifact_id,
        content="An updated conversation about Python decorators with additional examples and advanced concepts.",
        title="Python Decorators Tutorial (Updated)",
        metadata={
            "topic": "Python decorators",
            "difficulty": "intermediate",
            "tags": ["python", "decorators", "tutorial", "advanced"],
            "last_updated": "demo_script"
        }
    )
    print(f"✅ Updated artifact to version {updated_artifact.version}")
    print(f"   New title: {updated_artifact.title}")

    # Get all sessions
    print("\n7. Listing all sessions...")
    sessions = storage.get_sessions()
    print(f"✅ Found {len(sessions)} chat sessions")
    for session in sessions:
        print(f"   - {session['title']} ({session['model_name']}) - {session['message_count']} messages")

    # Get session artifacts
    print("\n8. Getting session artifacts...")
    session_artifacts = storage.get_session_artifacts(session_id)
    print(f"✅ Found {len(session_artifacts)} artifacts in session")
    for art in session_artifacts:
        print(f"   - {art.title} (v{art.version})")

    # Create another session and artifact for testing
    print("\n9. Creating additional content...")
    session_2 = storage.create_session(
        session_id="demo_session_2",
        title="Advanced AI Topics",
        model_name="gpt-3.5-turbo"
    )

    artifact_2 = storage.create_artifact(
        session_id=session_2,
        title="Machine Learning Basics",
        content="Introduction to machine learning concepts and algorithms.",
        artifact_type="educational",
        metadata={"topic": "machine learning", "level": "beginner"}
    )

    print(f"✅ Created additional session and artifact")

    # Search across all artifacts
    print("\n10. Searching all artifacts...")
    all_artifacts = storage.search_artifacts("", limit=10)  # Get all
    print(f"✅ Total artifacts in system: {len(all_artifacts)}")
    for art in all_artifacts:
        print(f"   - {art.title} ({art.artifact_type})")

    print("\n🎉 Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("✅ Session management")
    print("✅ Message storage and retrieval")
    print("✅ Artifact creation and versioning")
    print("✅ Search functionality")
    print("✅ Metadata support")
    print("✅ Multi-session support")

    print(f"\n📊 Storage Summary:")
    sessions = storage.get_sessions()
    total_messages = sum(s['message_count'] for s in sessions)
    print(f"   Sessions: {len(sessions)}")
    print(f"   Messages: {total_messages}")
    print(f"   Artifacts: {len(all_artifacts)}")
    print(f"   Database: data/sqlite/app.db")


if __name__ == "__main__":
    try:
        demo_chat_storage()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
