"""
TrustGate v2 Engine — Multi-language verification tests

Tests the tree-sitter based engine across Python, JavaScript,
and edge cases.  Each test validates parsing, graph construction,
rule matching, and the final VerificationReport output.
"""

import pytest
from codeshield.trustgate.engine.executor import verify, VerificationReport
from codeshield.trustgate.engine.parser import parse_source, detect_language, Lang
from codeshield.trustgate.engine.meta_ast import normalise, NodeKind
from codeshield.trustgate.engine.graphs import (
    build_cfg,
    build_dfg,
    build_taint_graph,
    build_call_graph,
)
from codeshield.trustgate.engine.rules import load_builtin_rules, Severity


# ===================================================================
#  Python — PASS cases (clean code, no findings)
# ===================================================================

class TestPythonPass:
    """Python code that should pass verification with score 1.0."""

    def test_simple_function(self):
        code = '''
def greet(name: str) -> str:
    return f"Hello, {name}!"
'''
        r = verify(code, "python")
        assert r.is_valid is True
        assert r.confidence_score == 1.0
        assert len(r.errors) == 0

    def test_class_definition(self):
        code = '''
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, x: int, y: int) -> int:
        self.result = x + y
        return self.result
'''
        r = verify(code, "python")
        assert r.is_valid is True
        assert len(r.errors) == 0

    def test_list_comprehension(self):
        code = "squares = [x ** 2 for x in range(10)]"
        r = verify(code, "python")
        assert r.is_valid is True

    def test_async_function(self):
        code = '''
async def fetch_data(url: str):
    return {"url": url, "status": 200}
'''
        r = verify(code, "python")
        assert r.is_valid is True

    def test_decorator(self):
        code = '''
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
'''
        r = verify(code, "python")
        assert r.is_valid is True

    def test_context_manager(self):
        code = '''
def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()
'''
        r = verify(code, "python")
        assert r.is_valid is True

    def test_empty_code(self):
        r = verify("", "python")
        assert r.is_valid is True
        assert r.confidence_score == 1.0

    def test_comment_only(self):
        code = "# This is a comment\n# Another comment"
        r = verify(code, "python")
        assert r.is_valid is True


# ===================================================================
#  Python — FAIL cases (should produce errors/warnings)
# ===================================================================

class TestPythonFail:
    """Python code that should fail or produce warnings."""

    def test_syntax_error(self):
        code = "def foo(\n    pass"
        r = verify(code, "python")
        assert r.parse_ok is False
        assert r.is_valid is False

    def test_type_mismatch_str_int(self):
        code = 'result = 5 + "hello"'
        r = verify(code, "python")
        assert r.is_valid is False
        assert any(f.rule_id == "type_mismatch" for f in r.findings)

    def test_shell_injection_eval(self):
        code = '''
data = input("Enter expression: ")
result = eval(data)
'''
        r = verify(code, "python")
        assert any(f.rule_id == "shell_injection" for f in r.findings)

    def test_shell_injection_os_system(self):
        code = '''
import os
cmd = input("Command: ")
os.system(cmd)
'''
        r = verify(code, "python")
        assert any(f.rule_id == "shell_injection" for f in r.findings)

    def test_taint_flow_input_to_exec(self):
        code = '''
user_code = input("Enter code: ")
exec(user_code)
'''
        r = verify(code, "python")
        taint = [f for f in r.findings if f.rule_id == "taint_flow"]
        assert len(taint) > 0

    def test_hardcoded_password(self):
        code = 'password = "super_secret_123"'
        r = verify(code, "python")
        assert any(f.rule_id == "hardcoded_secret" for f in r.findings)

    def test_hardcoded_api_key(self):
        code = 'api_key = "sk-1234567890abcdef"'
        r = verify(code, "python")
        assert any(f.rule_id == "hardcoded_secret" for f in r.findings)

    def test_bare_except(self):
        code = '''
try:
    risky()
except:
    pass
'''
        r = verify(code, "python")
        assert any(f.rule_id == "bare_except" for f in r.findings)

    def test_multiple_issues(self):
        """Code with many issues should have low confidence."""
        code = '''
import os
password = "secret123"
x = 5 + "hello"
user_input = input("name: ")
os.system(user_input)
'''
        r = verify(code, "python")
        assert r.is_valid is False
        assert r.confidence_score < 0.5
        assert len(r.findings) >= 3

    def test_subprocess_injection(self):
        code = '''
import subprocess
cmd = input("Command: ")
subprocess.call(cmd, shell=True)
'''
        r = verify(code, "python")
        assert any(f.rule_id == "shell_injection" for f in r.findings)


# ===================================================================
#  JavaScript — PASS cases
# ===================================================================

class TestJavaScriptPass:
    """JavaScript code that should pass verification."""

    def test_simple_function(self):
        code = '''
function greet(name) {
    return "Hello, " + name;
}
'''
        r = verify(code, "javascript")
        assert r.is_valid is True
        assert r.language == "javascript"

    def test_arrow_function(self):
        code = "const add = (a, b) => a + b;"
        r = verify(code, "javascript")
        assert r.is_valid is True

    def test_class(self):
        code = '''
class Animal {
    constructor(name) {
        this.name = name;
    }
    speak() {
        return this.name + " makes a sound";
    }
}
'''
        r = verify(code, "javascript")
        assert r.is_valid is True

    def test_async_await(self):
        code = '''
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}
'''
        r = verify(code, "javascript")
        assert r.is_valid is True

    def test_destructuring(self):
        code = "const { name, age } = person;"
        r = verify(code, "javascript")
        assert r.is_valid is True

    def test_template_literal(self):
        code = 'const msg = `Hello, ${name}!`;'
        r = verify(code, "javascript")
        assert r.is_valid is True


# ===================================================================
#  JavaScript — FAIL cases
# ===================================================================

class TestJavaScriptFail:
    """JavaScript code that should produce findings."""

    def test_eval_injection(self):
        code = 'const result = eval(userInput);'
        r = verify(code, "javascript")
        assert any(f.rule_id == "shell_injection" for f in r.findings)

    def test_syntax_error(self):
        code = "function foo( {"
        r = verify(code, "javascript")
        assert r.parse_ok is False
        assert r.is_valid is False

    def test_hardcoded_token(self):
        code = 'const auth_token = "eyJhbGciOiJIUzI1NiJ9.secret";'
        r = verify(code, "javascript")
        assert any(f.rule_id == "hardcoded_secret" for f in r.findings)


# ===================================================================
#  Parser layer tests
# ===================================================================

class TestParser:
    """Low-level parsing tests."""

    def test_parse_python(self):
        result = parse_source("x = 1", "python")
        assert result.language == Lang.PYTHON
        assert result.has_errors is False
        assert result.root.type == "module"

    def test_parse_javascript(self):
        result = parse_source("const x = 1;", "javascript")
        assert result.language == Lang.JAVASCRIPT
        assert result.has_errors is False

    def test_detect_language_py(self):
        assert detect_language("app.py") == Lang.PYTHON

    def test_detect_language_js(self):
        assert detect_language("index.js") == Lang.JAVASCRIPT

    def test_detect_language_jsx(self):
        assert detect_language("App.jsx") == Lang.JAVASCRIPT

    def test_detect_language_unknown(self):
        assert detect_language("style.css") is None

    def test_error_detection(self):
        result = parse_source("def (:", "python")
        assert result.has_errors is True


# ===================================================================
#  MetaAST normalization tests
# ===================================================================

class TestMetaAST:
    """MetaAST normalization tests."""

    def test_function_extraction(self):
        code = '''
def hello():
    pass

def world():
    pass
'''
        pr = parse_source(code, "python")
        meta = normalise(pr)
        fns = meta.all_functions
        assert len(fns) == 2

    def test_call_extraction(self):
        code = "print(len([1, 2, 3]))"
        pr = parse_source(code, "python")
        meta = normalise(pr)
        calls = meta.all_calls
        assert any(c.name == "print" for c in calls)

    def test_node_kind_mapping(self):
        code = '''
import os

x = 10
if x > 5:
    print("big")
'''
        pr = parse_source(code, "python")
        meta = normalise(pr)
        imports = meta.root.find_all(NodeKind.IMPORT)
        assert len(imports) >= 1
        conditionals = meta.root.find_all(NodeKind.CONDITIONAL)
        assert len(conditionals) >= 1


# ===================================================================
#  Graph construction tests
# ===================================================================

class TestGraphs:
    """Program graph construction tests."""

    def test_cfg_has_entry_exit(self):
        code = '''
def foo():
    x = 1
    return x
'''
        pr = parse_source(code, "python")
        meta = normalise(pr)
        cfg = build_cfg(meta)
        assert cfg.entry is not None
        assert cfg.exit is not None
        assert len(cfg.nodes) >= 3

    def test_dfg_defs_and_uses(self):
        code = '''
x = 10
y = x + 5
print(y)
'''
        pr = parse_source(code, "python")
        meta = normalise(pr)
        dfg = build_dfg(meta)
        assert len(dfg.nodes) > 0
        assert len(dfg.edges) > 0

    def test_taint_graph_sources_sinks(self):
        code = '''
data = input("Enter: ")
eval(data)
'''
        pr = parse_source(code, "python")
        meta = normalise(pr)
        tfg = build_taint_graph(meta)
        assert len(tfg.nodes) >= 2
        assert len(tfg.edges) >= 1

    def test_call_graph(self):
        code = '''
def a():
    b()

def b():
    pass
'''
        pr = parse_source(code, "python")
        meta = normalise(pr)
        cg = build_call_graph(meta)
        # Should have nodes for both functions
        assert len(cg.nodes) >= 2

    def test_cfg_reachability(self):
        code = '''
x = 1
y = 2
z = x + y
'''
        pr = parse_source(code, "python")
        meta = normalise(pr)
        cfg = build_cfg(meta)
        reachable = cfg.reachable_from(cfg.entry)
        assert cfg.exit in reachable


# ===================================================================
#  Rule engine tests
# ===================================================================

class TestRules:
    """Verification rule tests."""

    def test_builtin_rules_loaded(self):
        rs = load_builtin_rules()
        assert len(rs.rules) >= 7

    def test_rules_have_ids(self):
        rs = load_builtin_rules()
        ids = {r.id for r in rs.rules}
        assert "shell_injection" in ids
        assert "taint_flow" in ids
        assert "type_mismatch" in ids
        assert "hardcoded_secret" in ids

    def test_python_only_rules_filtered(self):
        rs = load_builtin_rules()
        py_rules = rs.enabled_rules("python")
        js_rules = rs.enabled_rules("javascript")
        # bare_except is Python-only
        assert any(r.id == "bare_except" for r in py_rules)
        assert not any(r.id == "bare_except" for r in js_rules)


# ===================================================================
#  Executor / Report tests
# ===================================================================

class TestExecutor:
    """Full pipeline executor tests."""

    def test_report_structure(self):
        r = verify("x = 1", "python")
        assert isinstance(r, VerificationReport)
        d = r.to_dict()
        assert "is_valid" in d
        assert "confidence_score" in d
        assert "findings" in d
        assert "language" in d
        assert "elapsed_ms" in d

    def test_caching(self):
        code = "x = 42"
        r1 = verify(code, "python")
        r2 = verify(code, "python")
        assert r1.code_hash == r2.code_hash
        # Second call should be faster (cached)
        assert r2.elapsed_ms <= r1.elapsed_ms + 1

    def test_language_detection_from_filename(self):
        r = verify("const x = 1;", "python", filename="app.js")
        assert r.language == "javascript"

    def test_issues_array_in_dict(self):
        code = 'secret_key = "abc123"'
        r = verify(code, "python")
        d = r.to_dict()
        assert "issues" in d
        for issue in d["issues"]:
            assert "severity" in issue
            assert "line" in issue
            assert "message" in issue


# ===================================================================
#  Edge cases
# ===================================================================

class TestEdgeCases:
    """Edge cases and robustness tests."""

    def test_very_long_code(self):
        code = "\n".join(f"x_{i} = {i}" for i in range(500))
        r = verify(code, "python")
        assert r.is_valid is True

    def test_unicode_code(self):
        code = '名前 = "太郎"\nprint(名前)'
        r = verify(code, "python")
        assert r.parse_ok is True

    def test_mixed_indentation(self):
        code = "def foo():\n\tx = 1\n\treturn x"
        r = verify(code, "python")
        assert r.parse_ok is True

    def test_nested_functions(self):
        code = '''
def outer():
    def inner():
        return 42
    return inner()
'''
        r = verify(code, "python")
        assert r.is_valid is True

    def test_deeply_nested_code(self):
        code = '''
def f():
    for i in range(10):
        if i > 5:
            for j in range(3):
                if j == 1:
                    print(i + j)
'''
        r = verify(code, "python")
        assert r.is_valid is True
