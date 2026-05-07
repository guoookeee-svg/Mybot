import ast
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CodeIssue:
    severity: str
    category: str
    message: str
    line: int
    column: int = 0
    fix_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "fix_suggestion": self.fix_suggestion,
        }


@dataclass
class FunctionInfo:
    name: str
    line_start: int
    line_end: int
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    complexity: int = 1
    is_async: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "args": self.args,
            "returns": self.returns,
            "docstring": self.docstring,
            "complexity": self.complexity,
            "is_async": self.is_async,
        }


@dataclass
class ClassInfo:
    name: str
    line_start: int
    line_end: int
    bases: List[str]
    methods: List[FunctionInfo]
    docstring: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "bases": self.bases,
            "methods": [m.to_dict() for m in self.methods],
            "docstring": self.docstring,
        }


@dataclass
class CodeAnalysisResult:
    filepath: str
    language: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[str]
    issues: List[CodeIssue]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filepath": self.filepath,
            "language": self.language,
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "imports": self.imports,
            "issues": [i.to_dict() for i in self.issues],
        }


class CodeAnalyzer:
    def analyze_file(self, filepath: str) -> CodeAnalysisResult:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        language = self._detect_language(filepath)
        if language == "python":
            return self._analyze_python(filepath, source)
        return self._analyze_generic(filepath, source, language)

    def analyze_source(self, source: str, filepath: str = "inline.py") -> CodeAnalysisResult:
        language = self._detect_language(filepath)
        if language == "python":
            return self._analyze_python(filepath, source)
        return self._analyze_generic(filepath, source, language)

    def _detect_language(self, filepath: str) -> str:
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
        }
        _, ext = os.path.splitext(filepath)
        return ext_map.get(ext.lower(), "unknown")

    def _analyze_python(self, filepath: str, source: str) -> CodeAnalysisResult:
        total_lines = source.count("\n") + 1
        code_lines, comment_lines, blank_lines = self._count_lines(source)

        functions = []
        classes = []
        imports = []
        issues = []

        try:
            tree = ast.parse(source)
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            imports = self._extract_imports(tree)
            issues = self._detect_python_issues(tree, source)
        except SyntaxError as e:
            issues.append(CodeIssue(
                severity="error",
                category="syntax",
                message=f"Syntax error: {e.msg}",
                line=e.lineno or 1,
                column=e.offset or 0,
            ))

        return CodeAnalysisResult(
            filepath=filepath,
            language="python",
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            issues=issues,
        )

    def _analyze_generic(self, filepath: str, source: str, language: str) -> CodeAnalysisResult:
        total_lines = source.count("\n") + 1
        code_lines, comment_lines, blank_lines = self._count_lines(source)

        return CodeAnalysisResult(
            filepath=filepath,
            language=language,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=[],
            classes=[],
            imports=[],
            issues=[],
        )

    def _count_lines(self, source: str) -> Tuple[int, int, int]:
        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        in_multiline_string = False

        for line in source.split("\n"):
            stripped = line.strip()

            if not stripped:
                blank_lines += 1
            elif stripped.startswith("#"):
                comment_lines += 1
            elif '"""' in stripped or "'''" in stripped:
                count = stripped.count('"""') + stripped.count("'''")
                if count == 1:
                    in_multiline_string = not in_multiline_string
                    comment_lines += 1
                else:
                    comment_lines += 1
            elif in_multiline_string:
                comment_lines += 1
            else:
                code_lines += 1

        return code_lines, comment_lines, blank_lines

    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args if a.arg != "self"]
                returns = None
                if node.returns:
                    returns = ast.unparse(node.returns) if hasattr(ast, "unparse") else str(node.returns)

                docstring = ast.get_docstring(node)
                complexity = self._calculate_complexity(node)
                is_async = isinstance(node, ast.AsyncFunctionDef)

                end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else node.lineno

                functions.append(FunctionInfo(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=end_line,
                    args=args,
                    returns=returns,
                    docstring=docstring,
                    complexity=complexity,
                    is_async=is_async,
                ))
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(ast.unparse(base) if hasattr(ast, "unparse") else str(base))

                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_args = [a.arg for a in item.args.args if a.arg != "self"]
                        method_returns = None
                        if item.returns:
                            method_returns = ast.unparse(item.returns) if hasattr(ast, "unparse") else str(item.returns)
                        methods.append(FunctionInfo(
                            name=item.name,
                            line_start=item.lineno,
                            line_end=item.end_lineno if hasattr(item, "end_lineno") and item.end_lineno else item.lineno,
                            args=method_args,
                            returns=method_returns,
                            docstring=ast.get_docstring(item),
                            complexity=self._calculate_complexity(item),
                            is_async=isinstance(item, ast.AsyncFunctionDef),
                        ))

                docstring = ast.get_docstring(node)
                end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else node.lineno

                classes.append(ClassInfo(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=end_line,
                    bases=bases,
                    methods=methods,
                    docstring=docstring,
                ))
        return classes

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def _calculate_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                complexity += 1
        return complexity

    def _detect_python_issues(self, tree: ast.AST, source: str) -> List[CodeIssue]:
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    issues.append(CodeIssue(
                        severity="warning",
                        category="documentation",
                        message=f"Function '{node.name}' is missing a docstring",
                        line=node.lineno,
                        fix_suggestion=f'Add a docstring to {node.name}() explaining its purpose, parameters, and return value.',
                    ))

                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    issues.append(CodeIssue(
                        severity="warning",
                        category="complexity",
                        message=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                        line=node.lineno,
                        fix_suggestion=f"Consider breaking down {node.name}() into smaller, more focused functions.",
                    ))

                for arg in node.args.args:
                    if arg.arg != "self" and arg.annotation is None:
                        issues.append(CodeIssue(
                            severity="info",
                            category="typing",
                            message=f"Parameter '{arg.arg}' in '{node.name}' lacks type annotation",
                            line=node.lineno,
                            fix_suggestion=f"Add type annotation: {arg.arg}: <type>",
                        ))

                if node.returns is None and node.name != "__init__":
                    issues.append(CodeIssue(
                        severity="info",
                        category="typing",
                        message=f"Function '{node.name}' is missing return type annotation",
                        line=node.lineno,
                        fix_suggestion=f"Add return type annotation: def {node.name}(...) -> <type>:",
                    ))

                all_args = [a.arg for a in node.args.args]
                if len(all_args) > 5:
                    issues.append(CodeIssue(
                        severity="warning",
                        category="design",
                        message=f"Function '{node.name}' has too many parameters ({len(all_args)})",
                        line=node.lineno,
                        fix_suggestion="Consider using a configuration object or dataclass to group related parameters.",
                    ))

            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    issues.append(CodeIssue(
                        severity="warning",
                        category="documentation",
                        message=f"Class '{node.name}' is missing a docstring",
                        line=node.lineno,
                        fix_suggestion=f"Add a class docstring explaining the purpose and usage of {node.name}.",
                    ))

            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(CodeIssue(
                        severity="error",
                        category="error_handling",
                        message="Bare 'except:' catches all exceptions including KeyboardInterrupt and SystemExit",
                        line=node.lineno,
                        fix_suggestion="Use 'except Exception:' instead of bare 'except:' to avoid catching system exceptions.",
                    ))

            elif isinstance(node, ast.Attribute):
                if isinstance(node.attr, str) and node.attr.startswith("__") and not node.attr.endswith("__"):
                    issues.append(CodeIssue(
                        severity="info",
                        category="naming",
                        message=f"Name mangling: '{node.attr}' is a private attribute with name mangling",
                        line=node.lineno,
                    ))

        lines = source.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            if len(stripped) > 120:
                issues.append(CodeIssue(
                    severity="info",
                    category="style",
                    message=f"Line too long ({len(stripped)} > 120 characters)",
                    line=i,
                    fix_suggestion="Break the line or use parentheses for implicit line continuation.",
                ))

            if re.search(r'eval\s*\(', stripped):
                issues.append(CodeIssue(
                    severity="error",
                    category="security",
                    message="Use of eval() is a security risk",
                    line=i,
                    fix_suggestion="Use ast.literal_eval() for safe evaluation of literal expressions.",
                ))

            if re.search(r'exec\s*\(', stripped):
                issues.append(CodeIssue(
                    severity="error",
                    category="security",
                    message="Use of exec() is a security risk",
                    line=i,
                    fix_suggestion="Avoid exec() entirely; refactor to use safer alternatives.",
                ))

            if re.search(r'except\s*:', stripped):
                pass

            if re.search(r'print\s*\(', stripped) and not stripped.strip().startswith("#"):
                if "test" not in source[:500].lower():
                    issues.append(CodeIssue(
                        severity="info",
                        category="style",
                        message="Use of print() for output — consider using logging module",
                        line=i,
                        fix_suggestion="Replace print() with logging.info() or logging.debug() for production code.",
                    ))

        return issues

    def analyze_directory(self, dirpath: str, exclude: Optional[List[str]] = None) -> List[CodeAnalysisResult]:
        exclude = exclude or ["__pycache__", ".git", "node_modules", ".venv", "venv"]
        results = []

        for root, dirs, files in os.walk(dirpath):
            dirs[:] = [d for d in dirs if d not in exclude]

            for filename in files:
                if filename.endswith(".py"):
                    filepath = os.path.join(root, filename)
                    try:
                        result = self.analyze_file(filepath)
                        results.append(result)
                    except Exception:
                        pass

        return results
