"""
Model Downloader - Download and manage GGUF models from HuggingFace.
"""

import logging
from pathlib import Path
from typing import Optional
import subprocess
import sys

logger = logging.getLogger(__name__)


class ModelDownloader:
    """
    Download GGUF models from HuggingFace Hub.
    """

    # Recommended models
    MODELS = {
        "qwen2.5-7b": {
            "name": "Qwen2.5-7B-Instruct",
            "repo": "Qwen/Qwen2.5-7B-Instruct-GGUF",
            "file": "qwen2.5-7b-instruct-q4_k_m.gguf",
            "size_gb": 4.5,
            "description": "Recommended: Best balance for M4 16GB. Excellent Russian support."
        },
        "qwen2.5-3b": {
            "name": "Qwen2.5-3B-Instruct",
            "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
            "file": "qwen2.5-3b-instruct-q4_k_m.gguf",
            "size_gb": 2.0,
            "description": "Lighter version. Very fast, good quality."
        },
        "openbio-8b": {
            "name": "OpenBioLLM-8B",
            "repo": "aaditya/OpenBioLLM-Llama3-8B-GGUF",
            "file": "openbiollm-llama3-8b.Q4_K_M.gguf",
            "size_gb": 5.0,
            "description": "Medical specialist. Better for English, weaker Russian."
        }
    }

    def __init__(self, models_dir: str = "./models"):
        """
        Initialize downloader.

        Args:
            models_dir: Directory to store models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def list_available_models(self) -> dict:
        """List all available models to download."""
        return self.MODELS

    def download_model(self, model_key: str) -> Optional[Path]:
        """
        Download model from HuggingFace.

        Args:
            model_key: Key from MODELS dict (e.g., "qwen2.5-7b")

        Returns:
            Path to downloaded model or None if failed
        """
        if model_key not in self.MODELS:
            logger.error(f"Unknown model: {model_key}")
            logger.info(f"Available models: {list(self.MODELS.keys())}")
            return None

        model_info = self.MODELS[model_key]
        repo = model_info["repo"]
        filename = model_info["file"]

        # Check if already downloaded
        local_path = self.models_dir / filename
        if local_path.exists():
            logger.info(f"✅ Model already downloaded: {local_path}")
            return local_path

        logger.info(f"📥 Downloading {model_info['name']}...")
        logger.info(f"   Size: ~{model_info['size_gb']} GB")
        logger.info(f"   From: {repo}")
        logger.info(f"   This may take a while...")

        try:
            # Check if huggingface-cli is installed
            result = subprocess.run(
                ["huggingface-cli", "--version"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error("huggingface-cli not found")
                logger.info("Install with: pip install huggingface-hub[cli]")
                return None

            # Download using huggingface-cli
            cmd = [
                "huggingface-cli",
                "download",
                repo,
                filename,
                "--local-dir",
                str(self.models_dir),
                "--local-dir-use-symlinks", "False"
            ]

            logger.info(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            if local_path.exists():
                logger.info(f"✅ Successfully downloaded to {local_path}")
                return local_path
            else:
                logger.error("Download completed but file not found")
                return None

        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed: {e}")
            logger.error(f"stderr: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    def get_model_path(self, model_key: str) -> Optional[Path]:
        """
        Get path to model if it exists locally.

        Args:
            model_key: Model key

        Returns:
            Path if exists, None otherwise
        """
        if model_key not in self.MODELS:
            return None

        filename = self.MODELS[model_key]["file"]
        local_path = self.models_dir / filename

        return local_path if local_path.exists() else None

    def list_local_models(self) -> list:
        """List all GGUF models in models directory."""
        gguf_files = list(self.models_dir.glob("*.gguf"))
        return [
            {
                "filename": f.name,
                "path": str(f),
                "size_mb": round(f.stat().st_size / (1024 * 1024), 2)
            }
            for f in gguf_files
        ]

    def install_dependencies(self) -> bool:
        """
        Install required dependencies for LLM.

        Returns:
            True if successful
        """
        logger.info("Installing LLM dependencies...")

        packages = [
            "llama-cpp-python",
            "huggingface-hub[cli]"
        ]

        try:
            for package in packages:
                logger.info(f"Installing {package}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True
                )

            logger.info("✅ All dependencies installed!")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Installation failed: {e}")
            return False
