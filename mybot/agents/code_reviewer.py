from typing import Any, Dict, List, Optional

from mybot.agent import Agent
from mybot.code_analyzer import CodeAnalyzer, CodeAnalysisResult, CodeIssue
from mybot.llm import LLMClient, MockLLMClient


REVIEW_SYSTEM_PROMPT = """You are CodeReviewer, an expert code review assistant. Your job is to:
1. Analyze code for quality issues, anti-patterns, and best practice violations
2. Check for readability, maintainability, and consistency
3. Suggest concrete improvements with code examples
4. Rate the overall code quality on a scale of 1-10

Always be constructive and specific in your feedback. Format your review as:
- **Summary**: Brief overview of the code
- **Issues Found**: List of issues with severity levels
- **Suggestions**: Concrete improvement recommendations
- **Quality Score**: X/10 with justification"""


class CodeReviewer(Agent):
    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(
            name="CodeReviewer",
            description="Reviews code for quality, style, and best practices",
            system_prompt=REVIEW_SYSTEM_PROMPT,
            llm_client=llm_client or MockLLMClient(),
        )
        self.analyzer = CodeAnalyzer()

    def review_file(self, filepath: str) -> Dict[str, Any]:
        analysis = self.analyzer.analyze_file(filepath)
        review_prompt = self._build_review_prompt(analysis)
        result = self.run(review_prompt, use_tools=False)
        return {
            "filepath": filepath,
            "analysis": analysis.to_dict(),
            "review": result["response"],
            "issues_count": len(analysis.issues),
            "quality_score": self._estimate_quality_score(analysis),
        }

    def review_source(self, source: str, filepath: str = "inline.py") -> Dict[str, Any]:
        analysis = self.analyzer.analyze_source(source, filepath)
        review_prompt = self._build_review_prompt(analysis)
        result = self.run(review_prompt, use_tools=False)
        return {
            "filepath": filepath,
            "analysis": analysis.to_dict(),
            "review": result["response"],
            "issues_count": len(analysis.issues),
            "quality_score": self._estimate_quality_score(analysis),
        }

    def review_directory(self, dirpath: str, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        analyses = self.analyzer.analyze_directory(dirpath, exclude=exclude)
        all_issues = []
        total_score = 0

        for analysis in analyses:
            all_issues.extend(analysis.issues)
            total_score += self._estimate_quality_score(analysis)

        avg_score = total_score / len(analyses) if analyses else 0

        summary_prompt = self._build_directory_summary_prompt(analyses, all_issues, avg_score)
        result = self.run(summary_prompt, use_tools=False)

        return {
            "directory": dirpath,
            "files_analyzed": len(analyses),
            "total_issues": len(all_issues),
            "average_quality_score": round(avg_score, 1),
            "review": result["response"],
            "file_results": [a.to_dict() for a in analyses],
        }

    def _build_review_prompt(self, analysis: CodeAnalysisResult) -> str:
        prompt = f"Please review the following Python code analysis results:\n\n"
        prompt += f"File: {analysis.filepath}\n"
        prompt += f"Total lines: {analysis.total_lines} (Code: {analysis.code_lines}, Comments: {analysis.comment_lines}, Blank: {analysis.blank_lines})\n\n"

        if analysis.functions:
            prompt += "Functions:\n"
            for func in analysis.functions:
                prompt += f"  - {func.name}({', '.join(func.args)}) -> {func.returns or 'None'} [complexity: {func.complexity}, docstring: {'yes' if func.docstring else 'NO'}]\n"
            prompt += "\n"

        if analysis.classes:
            prompt += "Classes:\n"
            for cls in analysis.classes:
                prompt += f"  - {cls.name}({', '.join(cls.bases)}) [methods: {len(cls.methods)}, docstring: {'yes' if cls.docstring else 'NO'}]\n"
            prompt += "\n"

        if analysis.issues:
            prompt += f"Issues found ({len(analysis.issues)}):\n"
            for issue in analysis.issues:
                prompt += f"  - [{issue.severity.upper()}] Line {issue.line}: {issue.message}\n"
                if issue.fix_suggestion:
                    prompt += f"    Fix: {issue.fix_suggestion}\n"
            prompt += "\n"
        else:
            prompt += "No issues detected.\n\n"

        prompt += "Please provide a comprehensive code review."
        return prompt

    def _build_directory_summary_prompt(
        self, analyses: List[CodeAnalysisResult], issues: List[CodeIssue], avg_score: float
    ) -> str:
        prompt = f"Please provide a project-level code review summary:\n\n"
        prompt += f"Files analyzed: {len(analyses)}\n"
        prompt += f"Total issues: {len(issues)}\n"
        prompt += f"Average quality score: {avg_score:.1f}/10\n\n"

        severity_counts = {"error": 0, "warning": 0, "info": 0}
        category_counts: Dict[str, int] = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        prompt += "Issue severity breakdown:\n"
        for sev, count in severity_counts.items():
            prompt += f"  - {sev.upper()}: {count}\n"
        prompt += "\n"

        prompt += "Issue category breakdown:\n"
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            prompt += f"  - {cat}: {count}\n"
        prompt += "\n"

        prompt += "Please provide: 1) Overall assessment 2) Top priorities to fix 3) Best practices recommendations"
        return prompt

    def _estimate_quality_score(self, analysis: CodeAnalysisResult) -> float:
        score = 10.0

        for issue in analysis.issues:
            if issue.severity == "error":
                score -= 1.5
            elif issue.severity == "warning":
                score -= 0.5
            elif issue.severity == "info":
                score -= 0.1

        if analysis.total_lines > 0:
            doc_ratio = analysis.comment_lines / analysis.total_lines
            if doc_ratio < 0.05:
                score -= 1.0
            elif doc_ratio < 0.1:
                score -= 0.5

        return max(1.0, min(10.0, score))
