"""JEE Bench Benchmarking Script for Math Routing Agent."""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from src.routing_agent import routing_agent
from src.feedback_system import feedback_system

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""
    question: str
    expected_answer: str
    predicted_answer: str
    is_correct: bool
    confidence: float
    routing_decision: str
    response_time: float
    error_message: Optional[str] = None


class JEEBenchmark:
    """JEE Bench benchmarking system for Math Routing Agent."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.jee_dataset = self._load_jee_dataset()
    
    def _load_jee_dataset(self) -> List[Dict[str, Any]]:
        """Load JEE benchmark dataset."""
        # This is a sample JEE dataset - in production, you'd load from actual JEE data
        jee_questions = [
            {
                "question": "Find the value of ∫₀^π/2 sin²(x) cos²(x) dx",
                "expected_answer": "π/16",
                "solution_steps": [
                    "Use the identity sin²(x) cos²(x) = (1/4)sin²(2x)",
                    "Substitute: ∫₀^π/2 (1/4)sin²(2x) dx",
                    "Use sin²(2x) = (1 - cos(4x))/2",
                    "Integrate: (1/8)∫₀^π/2 (1 - cos(4x)) dx",
                    "Evaluate: (1/8)[x - sin(4x)/4]₀^π/2 = π/16"
                ],
                "topic": "Calculus",
                "difficulty": "Hard",
                "year": 2023
            },
            {
                "question": "If the roots of x² - 3x + 2 = 0 are α and β, find α² + β²",
                "expected_answer": "5",
                "solution_steps": [
                    "For quadratic ax² + bx + c = 0, sum of roots = -b/a = 3",
                    "Product of roots = c/a = 2",
                    "Use identity: α² + β² = (α + β)² - 2αβ",
                    "Substitute: α² + β² = 3² - 2(2) = 9 - 4 = 5"
                ],
                "topic": "Algebra",
                "difficulty": "Medium",
                "year": 2023
            },
            {
                "question": "Find the number of ways to arrange 5 boys and 3 girls in a row such that no two girls are adjacent",
                "expected_answer": "14400",
                "solution_steps": [
                    "First arrange 5 boys: 5! = 120 ways",
                    "Create 6 gaps: _B_B_B_B_B_",
                    "Choose 3 gaps from 6 for girls: C(6,3) = 20",
                    "Arrange 3 girls in chosen gaps: 3! = 6",
                    "Total ways: 120 × 20 × 6 = 14400"
                ],
                "topic": "Permutations and Combinations",
                "difficulty": "Hard",
                "year": 2022
            },
            {
                "question": "If tan(A + B) = 1 and tan(A - B) = 1/3, find tan(2A)",
                "expected_answer": "2",
                "solution_steps": [
                    "Use tan(2A) = tan((A+B) + (A-B))",
                    "Apply tan addition formula: tan(2A) = (tan(A+B) + tan(A-B))/(1 - tan(A+B)tan(A-B))",
                    "Substitute: tan(2A) = (1 + 1/3)/(1 - 1×1/3)",
                    "Simplify: tan(2A) = (4/3)/(2/3) = 2"
                ],
                "topic": "Trigonometry",
                "difficulty": "Medium",
                "year": 2022
            },
            {
                "question": "Find the area bounded by the curves y = x² and y = 2x - x²",
                "expected_answer": "1/3",
                "solution_steps": [
                    "Find intersection points: x² = 2x - x²",
                    "Solve: 2x² - 2x = 0, so x = 0 or x = 1",
                    "For 0 ≤ x ≤ 1: 2x - x² ≥ x²",
                    "Area = ∫₀¹ (2x - x² - x²) dx = ∫₀¹ (2x - 2x²) dx",
                    "Integrate: [x² - 2x³/3]₀¹ = 1 - 2/3 = 1/3"
                ],
                "topic": "Calculus",
                "difficulty": "Hard",
                "year": 2021
            },
            {
                "question": "If z₁ and z₂ are complex numbers such that |z₁| = |z₂| = 1 and z₁ + z₂ = 1, find |z₁ - z₂|",
                "expected_answer": "√3",
                "solution_steps": [
                    "Let z₁ = e^(iθ₁) and z₂ = e^(iθ₂)",
                    "Given: e^(iθ₁) + e^(iθ₂) = 1",
                    "Use Euler's formula: cos(θ₁) + cos(θ₂) + i(sin(θ₁) + sin(θ₂)) = 1",
                    "Equate real parts: cos(θ₁) + cos(θ₂) = 1",
                    "Equate imaginary parts: sin(θ₁) + sin(θ₂) = 0",
                    "Solve to get θ₁ = π/3, θ₂ = -π/3",
                    "Calculate |z₁ - z₂| = |e^(iπ/3) - e^(-iπ/3)| = |2i sin(π/3)| = √3"
                ],
                "topic": "Complex Numbers",
                "difficulty": "Hard",
                "year": 2021
            },
            {
                "question": "Find the number of solutions of the equation sin(x) = x/10 in the interval [0, 10π]",
                "expected_answer": "31",
                "solution_steps": [
                    "Plot y = sin(x) and y = x/10",
                    "For x ∈ [0, 10π], sin(x) oscillates between -1 and 1",
                    "y = x/10 increases from 0 to π",
                    "Since π > 1, the line y = x/10 intersects y = sin(x) multiple times",
                    "Count intersections: approximately 31 solutions"
                ],
                "topic": "Trigonometry",
                "difficulty": "Hard",
                "year": 2020
            },
            {
                "question": "If the sum of the first n terms of an AP is 3n² + 5n, find the 20th term",
                "expected_answer": "122",
                "solution_steps": [
                    "Given: S_n = 3n² + 5n",
                    "Find a_n = S_n - S_(n-1)",
                    "S_(n-1) = 3(n-1)² + 5(n-1) = 3n² - 6n + 3 + 5n - 5 = 3n² - n - 2",
                    "a_n = (3n² + 5n) - (3n² - n - 2) = 6n + 2",
                    "20th term: a_20 = 6(20) + 2 = 122"
                ],
                "topic": "Arithmetic Progression",
                "difficulty": "Medium",
                "year": 2020
            },
            {
                "question": "Find the value of lim(x→0) (sin(x) - x)/x³",
                "expected_answer": "-1/6",
                "solution_steps": [
                    "Use L'Hôpital's rule (0/0 form)",
                    "Differentiate numerator: cos(x) - 1",
                    "Differentiate denominator: 3x²",
                    "Still 0/0, apply L'Hôpital's again",
                    "Differentiate: -sin(x)/6x",
                    "Apply L'Hôpital's once more: -cos(x)/6",
                    "Evaluate at x = 0: -1/6"
                ],
                "topic": "Limits",
                "difficulty": "Hard",
                "year": 2019
            },
            {
                "question": "If A and B are two events such that P(A) = 0.3, P(B) = 0.4, and P(A ∩ B) = 0.1, find P(A ∪ B)",
                "expected_answer": "0.6",
                "solution_steps": [
                    "Use the formula: P(A ∪ B) = P(A) + P(B) - P(A ∩ B)",
                    "Substitute: P(A ∪ B) = 0.3 + 0.4 - 0.1",
                    "Calculate: P(A ∪ B) = 0.6"
                ],
                "topic": "Probability",
                "difficulty": "Easy",
                "year": 2019
            }
        ]
        
        return jee_questions
    
    async def run_benchmark(self, num_questions: int = None) -> List[BenchmarkResult]:
        """Run the JEE benchmark."""
        logger.info("Starting JEE benchmark...")
        
        questions_to_test = self.jee_dataset[:num_questions] if num_questions else self.jee_dataset
        
        for i, question_data in enumerate(questions_to_test):
            logger.info(f"Testing question {i+1}/{len(questions_to_test)}: {question_data['question'][:50]}...")
            
            start_time = time.time()
            
            try:
                # Process question through routing agent
                result = await routing_agent.process_query(question_data['question'])
                
                response_time = time.time() - start_time
                
                if result['success']:
                    # Evaluate correctness
                    is_correct = self._evaluate_correctness(
                        question_data['expected_answer'],
                        result['response']['solution']
                    )
                    
                    benchmark_result = BenchmarkResult(
                        question=question_data['question'],
                        expected_answer=question_data['expected_answer'],
                        predicted_answer=result['response']['solution'],
                        is_correct=is_correct,
                        confidence=result.get('confidence', 0.0),
                        routing_decision=result.get('routing_decision', 'unknown'),
                        response_time=response_time
                    )
                else:
                    benchmark_result = BenchmarkResult(
                        question=question_data['question'],
                        expected_answer=question_data['expected_answer'],
                        predicted_answer="",
                        is_correct=False,
                        confidence=0.0,
                        routing_decision='error',
                        response_time=response_time,
                        error_message=result.get('error', 'Unknown error')
                    )
                
                self.results.append(benchmark_result)
                
            except Exception as e:
                logger.error(f"Error processing question {i+1}: {str(e)}")
                response_time = time.time() - start_time
                
                benchmark_result = BenchmarkResult(
                    question=question_data['question'],
                    expected_answer=question_data['expected_answer'],
                    predicted_answer="",
                    is_correct=False,
                    confidence=0.0,
                    routing_decision='error',
                    response_time=response_time,
                    error_message=str(e)
                )
                self.results.append(benchmark_result)
        
        logger.info(f"Benchmark completed. Processed {len(self.results)} questions.")
        return self.results
    
    def _evaluate_correctness(self, expected: str, predicted: str) -> bool:
        """Evaluate if the predicted answer is correct."""
        # Simple evaluation - in production, use more sophisticated math evaluation
        expected_clean = expected.lower().strip()
        predicted_clean = predicted.lower().strip()
        
        # Check for exact match
        if expected_clean in predicted_clean:
            return True
        
        # Check for numerical equivalence
        try:
            expected_num = float(expected_clean)
            # Extract numbers from predicted answer
            import re
            numbers = re.findall(r'-?\d+\.?\d*', predicted_clean)
            for num_str in numbers:
                if abs(float(num_str) - expected_num) < 1e-6:
                    return True
        except:
            pass
        
        # Check for common mathematical expressions
        math_expressions = [
            'π/16', 'π/4', 'π/2', 'π', '2π',
            '1/3', '1/2', '2/3', '3/4',
            '√2', '√3', '√5',
            'e', 'ln(2)', 'log(2)'
        ]
        
        for expr in math_expressions:
            if expr in expected_clean and expr in predicted_clean:
                return True
        
        return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.results:
            return {"error": "No benchmark results available"}
        
        # Calculate metrics
        total_questions = len(self.results)
        correct_answers = sum(1 for r in self.results if r.is_correct)
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        avg_response_time = np.mean([r.response_time for r in self.results])
        avg_confidence = np.mean([r.confidence for r in self.results])
        
        # Routing decisions
        routing_stats = {}
        for result in self.results:
            routing = result.routing_decision
            routing_stats[routing] = routing_stats.get(routing, 0) + 1
        
        # Accuracy by routing decision
        accuracy_by_routing = {}
        for routing in routing_stats.keys():
            routing_results = [r for r in self.results if r.routing_decision == routing]
            if routing_results:
                routing_correct = sum(1 for r in routing_results if r.is_correct)
                accuracy_by_routing[routing] = routing_correct / len(routing_results)
        
        # Error analysis
        errors = [r for r in self.results if r.error_message]
        error_rate = len(errors) / total_questions if total_questions > 0 else 0
        
        report = {
            "summary": {
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "accuracy": round(accuracy, 4),
                "average_response_time": round(avg_response_time, 4),
                "average_confidence": round(avg_confidence, 4),
                "error_rate": round(error_rate, 4)
            },
            "routing_analysis": {
                "routing_distribution": routing_stats,
                "accuracy_by_routing": accuracy_by_routing
            },
            "performance_metrics": {
                "fastest_response": min([r.response_time for r in self.results]),
                "slowest_response": max([r.response_time for r in self.results]),
                "median_response_time": np.median([r.response_time for r in self.results])
            },
            "detailed_results": [
                {
                    "question": r.question,
                    "expected": r.expected_answer,
                    "predicted": r.predicted_answer,
                    "correct": r.is_correct,
                    "confidence": r.confidence,
                    "routing": r.routing_decision,
                    "response_time": r.response_time,
                    "error": r.error_message
                }
                for r in self.results
            ]
        }
        
        return report
    
    def save_report(self, filename: str = None) -> str:
        """Save benchmark report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jee_benchmark_report_{timestamp}.json"
        
        report = self.generate_report()
        
        # Save JSON report
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save CSV results
        csv_filename = filename.replace('.json', '.csv')
        df = pd.DataFrame([
            {
                "question": r.question,
                "expected_answer": r.expected_answer,
                "predicted_answer": r.predicted_answer,
                "is_correct": r.is_correct,
                "confidence": r.confidence,
                "routing_decision": r.routing_decision,
                "response_time": r.response_time,
                "error_message": r.error_message
            }
            for r in self.results
        ])
        df.to_csv(csv_filename, index=False)
        
        logger.info(f"Benchmark report saved to {filename}")
        logger.info(f"Detailed results saved to {csv_filename}")
        
        return filename
    
    def plot_results(self, save_path: str = None) -> str:
        """Generate visualization plots for benchmark results."""
        if not self.results:
            logger.warning("No results to plot")
            return None
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('JEE Benchmark Results Analysis', fontsize=16, fontweight='bold')
        
        # 1. Accuracy by routing decision
        routing_accuracy = {}
        for routing in set(r.routing_decision for r in self.results):
            routing_results = [r for r in self.results if r.routing_decision == routing]
            if routing_results:
                accuracy = sum(1 for r in routing_results if r.is_correct) / len(routing_results)
                routing_accuracy[routing] = accuracy
        
        axes[0, 0].bar(routing_accuracy.keys(), routing_accuracy.values())
        axes[0, 0].set_title('Accuracy by Routing Decision')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Response time distribution
        response_times = [r.response_time for r in self.results]
        axes[0, 1].hist(response_times, bins=20, alpha=0.7, color='skyblue')
        axes[0, 1].set_title('Response Time Distribution')
        axes[0, 1].set_xlabel('Response Time (seconds)')
        axes[0, 1].set_ylabel('Frequency')
        
        # 3. Confidence vs Accuracy scatter plot
        correct_results = [r for r in self.results if r.is_correct]
        incorrect_results = [r for r in self.results if not r.is_correct]
        
        axes[1, 0].scatter([r.confidence for r in correct_results], 
                          [r.response_time for r in correct_results], 
                          alpha=0.6, label='Correct', color='green')
        axes[1, 0].scatter([r.confidence for r in incorrect_results], 
                          [r.response_time for r in incorrect_results], 
                          alpha=0.6, label='Incorrect', color='red')
        axes[1, 0].set_title('Confidence vs Response Time')
        axes[1, 0].set_xlabel('Confidence')
        axes[1, 0].set_ylabel('Response Time (seconds)')
        axes[1, 0].legend()
        
        # 4. Overall performance metrics
        metrics = ['Accuracy', 'Avg Response Time', 'Avg Confidence']
        values = [
            sum(1 for r in self.results if r.is_correct) / len(self.results),
            np.mean([r.response_time for r in self.results]),
            np.mean([r.confidence for r in self.results])
        ]
        
        bars = axes[1, 1].bar(metrics, values, color=['green', 'blue', 'orange'])
        axes[1, 1].set_title('Overall Performance Metrics')
        axes[1, 1].set_ylabel('Value')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plots saved to {save_path}")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"jee_benchmark_plots_{timestamp}.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plots saved to {save_path}")
        
        plt.show()
        return save_path


async def main():
    """Main function to run the JEE benchmark."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create benchmark instance
    benchmark = JEEBenchmark()
    
    # Run benchmark
    print("Starting JEE Benchmark...")
    results = await benchmark.run_benchmark(num_questions=10)  # Test with 10 questions
    
    # Generate and save report
    print("Generating report...")
    report_filename = benchmark.save_report()
    
    # Generate plots
    print("Generating visualizations...")
    plot_filename = benchmark.plot_results()
    
    # Print summary
    report = benchmark.generate_report()
    print("\n" + "="*50)
    print("JEE BENCHMARK SUMMARY")
    print("="*50)
    print(f"Total Questions: {report['summary']['total_questions']}")
    print(f"Correct Answers: {report['summary']['correct_answers']}")
    print(f"Accuracy: {report['summary']['accuracy']:.2%}")
    print(f"Average Response Time: {report['summary']['average_response_time']:.2f}s")
    print(f"Average Confidence: {report['summary']['average_confidence']:.2f}")
    print(f"Error Rate: {report['summary']['error_rate']:.2%}")
    print("\nRouting Analysis:")
    for routing, count in report['routing_analysis']['routing_distribution'].items():
        accuracy = report['routing_analysis']['accuracy_by_routing'].get(routing, 0)
        print(f"  {routing}: {count} questions, {accuracy:.2%} accuracy")
    
    print(f"\nReport saved to: {report_filename}")
    if plot_filename:
        print(f"Plots saved to: {plot_filename}")


if __name__ == "__main__":
    asyncio.run(main())
