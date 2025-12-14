#!/usr/bin/env python3
"""
Test script for DocMentor LLM integration.
Verifies that the model works correctly.
"""

import sys
import logging
from pathlib import Path
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.llm import LLMManager, PromptTemplates, RAGPipeline


def test_llm_loading():
    """Test 1: Load model."""
    print("\n" + "=" * 60)
    print("Test 1: Loading LLM Model")
    print("=" * 60)

    # Find GGUF models
    models_dir = Path("./models")
    gguf_files = list(models_dir.glob("*.gguf"))

    if not gguf_files:
        print("❌ No GGUF models found in ./models/")
        print("   Run: python setup_llm.py")
        return None

    print(f"\nFound {len(gguf_files)} model(s):")
    for i, model in enumerate(gguf_files, 1):
        size_mb = model.stat().st_size / (1024 * 1024)
        print(f"  {i}. {model.name} ({size_mb:.1f} MB)")

    # Use first model
    model_path = gguf_files[0]
    print(f"\nUsing: {model_path.name}")
    print("Loading... (this may take 10-30 seconds)")

    llm = LLMManager(
        model_path=str(model_path),
        n_ctx=2048,
        n_threads=8,
        use_metal=True
    )

    start = time.time()
    if llm.load_model():
        elapsed = time.time() - start
        print(f"✅ Model loaded in {elapsed:.1f}s")
        return llm
    else:
        print("❌ Failed to load model")
        return None


def test_simple_generation(llm: LLMManager):
    """Test 2: Simple text generation."""
    print("\n" + "=" * 60)
    print("Test 2: Simple Generation")
    print("=" * 60)

    prompt = "Что такое бронхиальная астма? Ответь кратко в 2-3 предложениях."

    print(f"\nPrompt: {prompt}")
    print("\nGenerating...")

    result = llm.generate(prompt, max_tokens=150, temperature=0.7)

    if result["status"] == "success":
        print(f"\n✅ Generated {result['tokens']} tokens in {result['time_seconds']:.2f}s")
        print(f"   Speed: {result['tokens_per_second']:.1f} tokens/sec")
        print(f"\nResponse:\n{result['text']}")
        return True
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return False


def test_chat_format(llm: LLMManager):
    """Test 3: Chat-style generation."""
    print("\n" + "=" * 60)
    print("Test 3: Chat Format")
    print("=" * 60)

    messages = [
        {"role": "system", "content": "Ты медицинский преподаватель. Отвечай кратко и точно."},
        {"role": "user", "content": "Назови 3 основных симптома острого аппендицита."}
    ]

    print("\nMessages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")

    print("\nGenerating...")

    result = llm.chat(messages, max_tokens=200, temperature=0.6)

    if result["status"] == "success":
        print(f"\n✅ Generated {result['tokens']} tokens in {result['time_seconds']:.2f}s")
        print(f"\nResponse:\n{result['text']}")
        return True
    else:
        print(f"❌ Chat failed: {result.get('error')}")
        return False


def test_prompt_templates(llm: LLMManager):
    """Test 4: Prompt templates."""
    print("\n" + "=" * 60)
    print("Test 4: Prompt Templates")
    print("=" * 60)

    # Test medical term explanation
    print("\nTemplate: explain_term")
    messages = PromptTemplates.explain_term(
        term="Тахикардия",
        context="Тахикардия - учащенное сердцебиение более 100 ударов в минуту в покое."
    )

    print(f"Testing with term: 'Тахикардия'")
    print("Generating...")

    result = llm.chat(messages, max_tokens=250)

    if result["status"] == "success":
        print(f"\n✅ Generated {result['tokens']} tokens")
        print(f"\nExplanation:\n{result['text'][:200]}...")
        return True
    else:
        print(f"❌ Template test failed")
        return False


def test_rag_pipeline(llm: LLMManager):
    """Test 5: RAG Pipeline (without vector store)."""
    print("\n" + "=" * 60)
    print("Test 5: RAG Pipeline")
    print("=" * 60)

    # Create RAG pipeline without vector store (will use direct generation)
    rag = RAGPipeline(llm_manager=llm, vector_store=None)

    question = "Как диагностировать пневмонию?"

    print(f"\nQuestion: {question}")
    print("Generating answer...")

    result = rag.answer_question(
        question=question,
        use_context=False,  # No vector store
        max_tokens=300
    )

    if result["status"] == "success":
        print(f"\n✅ Answer generated in {result['metadata']['time_seconds']:.2f}s")
        print(f"\nAnswer:\n{result['answer'][:300]}...")
        return True
    else:
        print(f"❌ RAG test failed: {result.get('error')}")
        return False


def test_performance(llm: LLMManager):
    """Test 6: Performance benchmarking."""
    print("\n" + "=" * 60)
    print("Test 6: Performance Benchmark")
    print("=" * 60)

    prompts = [
        "Что такое гипертония?",
        "Назови симптомы диабета.",
        "Как лечится бронхит?"
    ]

    print(f"\nRunning {len(prompts)} generations...")

    speeds = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{i}/{len(prompts)}: {prompt}")
        result = llm.generate(prompt, max_tokens=100)

        if result["status"] == "success":
            speed = result["tokens_per_second"]
            speeds.append(speed)
            print(f"   ✓ {speed:.1f} tokens/sec")
        else:
            print(f"   ✗ Failed")

    if speeds:
        avg_speed = sum(speeds) / len(speeds)
        print(f"\n✅ Average speed: {avg_speed:.1f} tokens/sec")

        # Performance assessment
        if avg_speed >= 30:
            print("   🚀 Excellent! Model is running very fast.")
        elif avg_speed >= 20:
            print("   ✅ Good! Model is running at expected speed.")
        elif avg_speed >= 10:
            print("   ⚠️  Acceptable, but could be faster.")
        else:
            print("   ⚠️  Slow. Consider using a smaller model.")

        return True
    else:
        print("❌ Benchmark failed")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  DocMentor LLM Test Suite")
    print("  MacBook M4 Optimization Test")
    print("=" * 70)

    # Test 1: Load model
    llm = test_llm_loading()
    if not llm:
        print("\n❌ Cannot proceed without loaded model")
        return

    # Test 2: Simple generation
    if not test_simple_generation(llm):
        print("\n⚠️  Simple generation failed, but continuing...")

    # Test 3: Chat format
    if not test_chat_format(llm):
        print("\n⚠️  Chat format failed, but continuing...")

    # Test 4: Prompt templates
    if not test_prompt_templates(llm):
        print("\n⚠️  Prompt templates failed, but continuing...")

    # Test 5: RAG pipeline
    if not test_rag_pipeline(llm):
        print("\n⚠️  RAG pipeline failed, but continuing...")

    # Test 6: Performance
    test_performance(llm)

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    stats = llm.get_stats()
    print(f"Total requests: {stats['total_requests']}")
    print(f"Total tokens generated: {stats['total_tokens_generated']}")
    print(f"Average speed: {stats['average_tokens_per_second']:.1f} tokens/sec")

    print("\n✅ All tests completed!")
    print("\nNext step: Integrate into DocMentor UI")
    print("  Run: streamlit run app/Home.py")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        sys.exit(1)
