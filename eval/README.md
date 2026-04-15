# RAG Evaluation with Ragas 📊

This folder contains evaluation scripts for the Clinical Intelligence RAG system using the **Ragas framework**.

## What is Ragas?

Ragas (Retrieval-Augmented Generation Assessment) provides a suite of metrics for evaluating RAG systems:

- **Faithfulness** - Is the generated answer factually grounded in retrieved context?
- **Answer Relevancy** - Does the answer directly address the question?
- **Context Precision** - Is the retrieved context relevant to the question?
- **Context Recall** - Does the retrieved context cover all relevant information?

## Quick Start

### 1. Install Dependencies
```bash
pip install -r ../requirements.txt
```

### 2. Run Evaluation
```bash
python evaluate_rag.py
```

**Expected Output:**
```
📊 Initializing RAG Evaluator...
🧪 Running evaluation on 3 test cases...

📈 Preparing dataset for Ragas evaluation...
🔍 Evaluating with Ragas metrics...

============================================================
📊 RAG EVALUATION RESULTS
============================================================

✅ Faithfulness:       0.92/1.00
   (Is answer grounded in retrieved context?)

✅ Answer Relevancy:   0.88/1.00
   (Does answer address the question?)

✅ Context Precision:  0.95/1.00
   (Are retrieved docs relevant?)

✅ Context Recall:     0.85/1.00
   (Coverage of all relevant info?)

🎯 Overall Score:      0.90/1.00
============================================================
```

## Understanding the Metrics

### Faithfulness (0-1)
- Measures if the generated answer is grounded in the retrieved context
- High score = Answer closely follows context, avoiding hallucinations
- **Target: > 0.85**

### Answer Relevancy (0-1)
- Measures if the answer addresses the user's question
- High score = Answer is on-topic and relevant
- **Target: > 0.80**

### Context Precision (0-1)
- Measures if retrieved documents are relevant to the question
- High score = Vector search finds relevant documents
- **Target: > 0.90**

### Context Recall (0-1)
- Measures if all relevant information was captured in retrieval
- High score = Comprehensive context retrieval
- **Target: > 0.85**

## How to Create Your Own Test Set

Edit `evaluate_rag.py` and modify the `run_evaluation()` function:

```python
def run_evaluation():
    test_questions = [
        "Your question 1?",
        "Your question 2?",
    ]

    ground_truths = [
        "Expected answer 1...",
        "Expected answer 2...",
    ]

    evaluator = RAGEvaluator()
    result = evaluator.run_evaluation(test_questions, ground_truths)
    if result:
        evaluator.print_results(result)
```

## Score Interpretation

| Score Range | Interpretation |
|-------------|---|
| 0.9-1.0 | Excellent 🟢 |
| 0.7-0.9 | Good 🟡 |
| 0.5-0.7 | Fair 🟠 |
| 0.0-0.5 | Poor 🔴 |

## Improving RAG Quality

If scores are low, try:

1. **Low Faithfulness?**
   - Improve context retrieval (Context Precision)
   - Use stricter prompts (no hallucinations)
   - Verify ground truth answers

2. **Low Answer Relevancy?**
   - Refine your questions
   - Improve prompt design
   - Use clarifying instructions

3. **Low Context Precision?**
   - Improve document chunking strategy
   - Add better metadata to documents
   - Use semantic search optimization

4. **Low Context Recall?**
   - Increase k (number of retrieved docs)
   - Improve document preprocessing
   - Use multi-step retrieval strategies

## References

- [Ragas Documentation](https://docs.ragas.io)
- [RAG Evaluation Paper](https://arxiv.org/abs/2309.15217)
- [LangChain RAG Evaluation](https://python.langchain.com/docs/use_cases/evaluation)
