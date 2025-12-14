#!/usr/bin/env python3
"""
Setup script for DocMentor LLM integration.
Run this to install dependencies and download models.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main setup flow."""
    print("=" * 60)
    print("  DocMentor LLM Setup")
    print("  MacBook M4 Optimized")
    print("=" * 60)
    print()

    # Add core to path
    sys.path.insert(0, str(Path(__file__).parent))

    from core.llm.model_downloader import ModelDownloader

    downloader = ModelDownloader(models_dir="./models")

    # Step 1: Install dependencies
    print("📦 Step 1: Installing dependencies...")
    print("-" * 60)
    print("This will install:")
    print("  - llama-cpp-python (LLM inference)")
    print("  - huggingface-hub (model downloads)")
    print()

    response = input("Continue? [Y/n]: ").strip().lower()
    if response and response != 'y':
        print("❌ Setup cancelled")
        return

    if not downloader.install_dependencies():
        print("❌ Failed to install dependencies")
        return

    print()

    # Step 2: Choose model
    print("🤖 Step 2: Choose LLM model")
    print("-" * 60)
    print()

    models = downloader.list_available_models()

    print("Available models:")
    for i, (key, info) in enumerate(models.items(), 1):
        print(f"\n{i}. {info['name']}")
        print(f"   Size: ~{info['size_gb']} GB")
        print(f"   File: {info['file']}")
        print(f"   Description: {info['description']}")

    print()
    print("Recommendation for MacBook M4 16GB: Option 1 (Qwen2.5-7B)")
    print()

    while True:
        choice = input("Choose model [1-3] or 'skip': ").strip()

        if choice.lower() == 'skip':
            print("⏭️  Skipping model download")
            print("   You can download later using: python setup_llm.py")
            break

        try:
            idx = int(choice) - 1
            model_keys = list(models.keys())
            if 0 <= idx < len(model_keys):
                model_key = model_keys[idx]
                break
            else:
                print(f"Please enter 1-{len(models)}")
        except ValueError:
            print("Please enter a number or 'skip'")

    if choice.lower() != 'skip':
        print()
        print(f"📥 Downloading {models[model_key]['name']}...")
        print(f"   This may take 10-30 minutes depending on your internet speed")
        print()

        model_path = downloader.download_model(model_key)

        if model_path:
            print()
            print("✅ Setup complete!")
            print()
            print(f"Model saved to: {model_path}")
            print()
            print("Next steps:")
            print("  1. Test the model: python test_llm.py")
            print("  2. Run DocMentor: streamlit run app/Home.py")
        else:
            print("❌ Model download failed")
            print("   You can try again later with: python setup_llm.py")

    # Step 3: Show local models
    print()
    print("📁 Local models:")
    print("-" * 60)
    local_models = downloader.list_local_models()

    if local_models:
        for model in local_models:
            print(f"  ✓ {model['filename']} ({model['size_mb']} MB)")
    else:
        print("  (none)")

    print()
    print("=" * 60)
    print("Setup finished!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}", exc_info=True)
        sys.exit(1)
