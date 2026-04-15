"""
RAG Evaluation Script using Ragas Framework

Evaluates the Clinical Intelligence RAG system against a golden test set
using Ragas quality metrics:
- Faithfulness: Checks if generated answer is grounded in context
- Answer Relevancy: Checks if answer addresses the question
- Context Precision: Checks if retrieved context is relevant
- Context Recall: Checks if all relevant context was retrieved

Note: Ragas evaluation requires an LLM for evaluation metrics.
Configure OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env
"""

import os
import sys
from typing import List, Dict, Any
import warnings

# Enable UTF-8 output for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)

from datasets import Dataset
from core.orchestrator import ClinicalRAGOrchestrator
from services.vector_db import VectorStoreManager
from core.config import settings

# Import Ragas with new API (v0.1+)
try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
except ImportError:
    # Fallback to new API structure
    from ragas.evaluation import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )

# Configure LLM for Ragas evaluation
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


class RAGEvaluator:
    def __init__(self):
        """Initialize the RAG evaluator with orchestrator and vector DB."""
        print("📊 Initializing RAG Evaluator...")
        self.orchestrator = ClinicalRAGOrchestrator()
        self.vector_db = VectorStoreManager()

    def run_evaluation(
        self,
        test_questions: List[str],
        ground_truths: List[str],
        num_contexts: int = 3,
        skip_metrics: bool = False,
    ) -> Dict[str, Any]:
        """
        Run evaluation on the RAG system.

        Args:
            test_questions: List of test questions
            ground_truths: List of expected ground truth answers
            num_contexts: Number of documents to retrieve (default: 3)
            skip_metrics: If True, only collect data without scoring (default: False)

        Returns:
            Dictionary with evaluation scores or collected data
        """
        if len(test_questions) != len(ground_truths):
            raise ValueError(
                "test_questions and ground_truths must have same length"
            )

        print(f"\n🧪 Running evaluation on {len(test_questions)} test cases...\n")

        answers = []
        contexts = []

        for i, question in enumerate(test_questions):
            print(f"  [{i+1}/{len(test_questions)}] Processing: {question}")

            # Retrieve context from Pinecone
            try:
                docs = self.vector_db.similarity_search(question, k=num_contexts)
                context_str = [doc.page_content for doc in docs]
            except Exception as e:
                print(f"    ⚠️ Context retrieval failed: {e}")
                context_str = []

            # Generate answer using RAG
            try:
                answer = self.orchestrator.query(question, " ".join(context_str))
            except Exception as e:
                print(f"    ⚠️ Answer generation failed: {e}")
                answer = "Error generating answer"

            answers.append(answer)
            contexts.append(context_str)

        # Prepare dataset for Ragas evaluation
        print("\n📈 Preparing dataset for evaluation...")
        data = {
            "question": test_questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
        dataset = Dataset.from_dict(data)

        if skip_metrics:
            print("⏭️  Skipping metric evaluation (inference cost)\n")
            print("=" * 60)
            print("📊 RAG EVALUATION DATA")
            print("=" * 60)
            for i, q in enumerate(test_questions):
                print(f"\nQuestion {i+1}: {q}")
                print(f"Generated Answer: {answers[i]}")
                print(f"Ground Truth: {ground_truths[i]}")
                print(f"Retrieved Context: {len(contexts[i])} docs")
            print("=" * 60)
            return data

        # Run scoring with Ragas metrics
        print("🔍 Evaluating with Ragas metrics...")
        print("   - Faithfulness (grounded in context)")
        print("   - Answer Relevancy (addresses question)")
        print("   - Context Precision (relevant docs retrieved)")
        print("   - Context Recall (coverage of relevant info)\n")

        try:
            # Configure LLM for ragas evaluation metrics
            if settings.LLM_PROVIDER == "ANTHROPIC":
                llm = ChatAnthropic(model="claude-opus-4-1-20250805")
            else:
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            # Set LLM for all metrics that need it
            for metric in [faithfulness, answer_relevancy, context_precision, context_recall]:
                if hasattr(metric, 'llm'):
                    metric.llm = llm
            
            result = evaluate(
                dataset,
                metrics=[
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall,
                ],
                llm=llm,
            )
            return result
        except Exception as e:
            print(f"⚠️  Metric evaluation failed: {e}")
            print("   Falling back to data-only view\n")
            return data

    def print_results(self, result: Dict[str, Any]) -> None:
        """
        Pretty print evaluation results.

        Args:
            result: Evaluation results from Ragas or data dict
        """
        if result is None:
            return

        # Check if this is metric scores or just data
        # Handle both dict and Ragas EvaluationResult object
        is_ragas_result = hasattr(result, 'scores') or (isinstance(result, dict) and "scores" in result)
        
        if is_ragas_result:
            # Ragas evaluation results with metrics
            try:
                # Try to get scores from Ragas result object
                if hasattr(result, 'scores'):
                    scores_obj = result.scores
                else:
                    scores_obj = result.get("scores", {})
                
                # Handle different score formats
                if isinstance(scores_obj, dict):
                    scores_dict = scores_obj
                elif hasattr(scores_obj, '__dict__'):
                    scores_dict = vars(scores_obj)
                elif isinstance(scores_obj, list) and len(scores_obj) > 0:
                    scores_dict = scores_obj[0] if isinstance(scores_obj[0], dict) else {}
                else:
                    scores_dict = {}
                
                print("\n" + "=" * 60)
                print("📊 RAG EVALUATION RESULTS")
                print("=" * 60)

                # Extract metric values with flexibility
                def get_score(name):
                    if isinstance(scores_dict, dict):
                        return scores_dict.get(name, None)
                    elif hasattr(scores_dict, name):
                        return getattr(scores_dict, name, None)
                    return None

                faithfulness = get_score('faithfulness')
                answer_relevancy = get_score('answer_relevancy')
                context_precision = get_score('context_precision')
                context_recall = get_score('context_recall')

                def format_score(value):
                    """Format score, handling None and NaN values."""
                    if value is None:
                        return "N/A"
                    try:
                        f_val = float(value)
                        if f_val != f_val:  # NaN check
                            return "N/A (insufficient data)"
                        return f"{f_val:.2f}"
                    except:
                        return "N/A"

                faithfulness_str = format_score(faithfulness)
                answer_relevancy_str = format_score(answer_relevancy)
                context_precision_str = format_score(context_precision)
                context_recall_str = format_score(context_recall)

                if faithfulness_str != "N/A":
                    print(f"\n✅ Faithfulness:       {faithfulness_str}/1.00")
                    print(f"   (Is answer grounded in retrieved context?)")
                if answer_relevancy_str != "N/A":
                    print(f"\n✅ Answer Relevancy:   {answer_relevancy_str}/1.00")
                    print(f"   (Does answer address the question?)")
                else:
                    print(f"\n⚠️  Answer Relevancy:   {answer_relevancy_str}")
                    print(f"   (Requires full LLM evaluation)")
                if context_precision_str != "N/A":
                    print(f"\n✅ Context Precision:  {context_precision_str}/1.00")
                    print(f"   (Are retrieved docs relevant?)")
                if context_recall_str != "N/A":
                    print(f"\n✅ Context Recall:     {context_recall_str}/1.00")
                    print(f"   (Coverage of all relevant info?)")

                # Calculate overall score (excluding N/A values)
                metric_values = []
                for v in [faithfulness, answer_relevancy, context_precision, context_recall]:
                    if v is not None:
                        try:
                            f_val = float(v)
                            if f_val == f_val:  # Not NaN
                                metric_values.append(f_val)
                        except:
                            pass

                if metric_values:
                    overall = sum(metric_values) / len(metric_values)
                    print(f"\n🎯 Overall Score:      {overall:.2f}/1.00 (based on {len(metric_values)} metrics)")

                print("\n" + "=" * 60)
                print("📌 Score Interpretation:")
                print("   0.9-1.0: Excellent    | 0.7-0.9: Good")
                print("   0.5-0.7: Fair         | 0.0-0.5: Poor")
                print("=" * 60 + "\n")
            except Exception as e:
                print(f"⚠️ Error parsing results: {e}")
                print("\n💡 TIP: To run full metric evaluation, ensure you have:")
                print("   - Valid OPENAI_API_KEY in your .env")
                print("   - Or set LLM_PROVIDER=ANTHROPIC with ANTHROPIC_API_KEY")
                print("=" * 60 + "\n")
        else:
            # Data-only view or dict format
            try:
                if isinstance(result, dict) and "question" in result:
                    print("\n" + "=" * 60)
                    print("📊 RAG EVALUATION DATA")
                    print("=" * 60)
                    print("\n✅ Data collected successfully!")
                    print(f"   Questions: {len(result.get('question', []))}")
                    print(f"   Answers: {len(result.get('answer', []))}")
                    print(f"   Contexts Retrieved: {len(result.get('contexts', []))}")
                    
                    print("\n📋 Evaluation Summary:")
                    for i, q in enumerate(result.get('question', [])):
                        print(f"\n   [{i+1}] Question: {q[:50]}...")
                        print(f"       Answer: {result['answer'][i][:60]}...")
                        print(f"       Expected: {result.get('ground_truth', ['N/A'])[i][:60]}...")
                    
                    print("\n💡 TIP: To run full metric evaluation, ensure you have:")
                    print("   - Valid OPENAI_API_KEY in your .env")
                    print("   - Or set LLM_PROVIDER=ANTHROPIC with ANTHROPIC_API_KEY")
                    print("=" * 60 + "\n")
                else:
                    print(f"\n✅ Evaluation complete")
            except Exception as e:
                print(f"\n✅ Evaluation complete (parsing error: {e})")


def run_evaluation():
    """Main evaluation runner with default test set."""

    # Define Golden Test Set (from indexed documents)
    test_questions = [
        "What is the patient's oxygen saturation and doctor's plan for oxygen?",
        "What diagnosis is suspected based on the clinical presentation?",
        "What medications are being prescribed for this patient?",
    ]

    ground_truths = [
        "The patient's oxygen saturation is 89% on room air. The doctor's plan is to start supplemental oxygen at 2L via nasal cannula with a target saturation of 88-92%.",
        "Acute COPD exacerbation is suspected based on the clinical presentation.",
        "The patient is prescribed medications for acute COPD exacerbation treatment as ordered by Dr. Chen.",
    ]

    # Run evaluation (skip_metrics=False to enable full metric scoring)
    evaluator = RAGEvaluator()
    result = evaluator.run_evaluation(
        test_questions, ground_truths, skip_metrics=False
    )

    # Print results
    if result:
        evaluator.print_results(result)


if __name__ == "__main__":
    run_evaluation()
