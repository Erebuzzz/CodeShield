/**
 * Docs Page - Clean, Structured Documentation
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Logo } from './Logo';

interface DocsProps {
    onBack: () => void;
}

type DocSection = 'overview' | 'trustgate' | 'styleforge' | 'contextvault' | 'mcp' | 'api';

const CodeBlock: React.FC<{ code: string; title?: string }> = ({ code, title }) => (
    <div className="bg-slate-900/50 border border-slate-800/50 rounded-lg overflow-hidden my-4">
        {title && (
            <div className="px-4 py-2 border-b border-slate-800/50 text-xs text-slate-500 font-mono bg-slate-900/30">
                {title}
            </div>
        )}
        <pre className="p-4 text-sm text-slate-300 font-mono overflow-x-auto leading-relaxed">
            <code>{code}</code>
        </pre>
    </div>
);

const NavItem: React.FC<{ 
    active: boolean; 
    onClick: () => void; 
    icon: React.ReactNode;
    label: string;
}> = ({ active, onClick, icon, label }) => (
    <button
        onClick={onClick}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-colors duration-150 ${
            active 
                ? 'bg-emerald-500/10 text-emerald-400' 
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
        }`}
    >
        <span className={active ? 'text-emerald-400' : 'text-slate-500'}>{icon}</span>
        {label}
    </button>
);

export const Docs: React.FC<DocsProps> = ({ onBack }) => {
    const [activeSection, setActiveSection] = useState<DocSection>('overview');

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="min-h-screen bg-[#030305]"
        >
            {/* Header */}
            <header className="border-b border-slate-800/50 px-6 py-4">
                <div className="max-w-6xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        <Logo size="sm" />
                        <span className="text-slate-600">|</span>
                        <span className="text-sm text-slate-400">Documentation</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <a 
                            href="https://github.com/Erebuzzz/CodeShield"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
                        >
                            <GitHubIcon />
                            GitHub
                        </a>
                        <button
                            onClick={onBack}
                            className="text-sm text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
                        >
                            <ArrowLeftIcon />
                            Back
                        </button>
                    </div>
                </div>
            </header>

            <div className="max-w-6xl mx-auto flex">
                {/* Sidebar Navigation */}
                <aside className="w-56 shrink-0 border-r border-slate-800/50 p-4 sticky top-0 h-screen">
                    <nav className="space-y-1">
                        <NavItem 
                            active={activeSection === 'overview'} 
                            onClick={() => setActiveSection('overview')}
                            icon={<BookIcon />}
                            label="Overview"
                        />
                        <NavItem 
                            active={activeSection === 'trustgate'} 
                            onClick={() => setActiveSection('trustgate')}
                            icon={<ShieldIcon />}
                            label="TrustGate"
                        />
                        <NavItem 
                            active={activeSection === 'styleforge'} 
                            onClick={() => setActiveSection('styleforge')}
                            icon={<SparklesIcon />}
                            label="StyleForge"
                        />
                        <NavItem 
                            active={activeSection === 'contextvault'} 
                            onClick={() => setActiveSection('contextvault')}
                            icon={<FolderIcon />}
                            label="ContextVault"
                        />
                        <NavItem 
                            active={activeSection === 'mcp'} 
                            onClick={() => setActiveSection('mcp')}
                            icon={<PlugIcon />}
                            label="MCP Integration"
                        />
                        <NavItem 
                            active={activeSection === 'api'} 
                            onClick={() => setActiveSection('api')}
                            icon={<CodeIcon />}
                            label="API Reference"
                        />
                    </nav>
                </aside>

                {/* Main Content */}
                <main className="flex-1 p-8 max-w-3xl">
                    {activeSection === 'overview' && <OverviewSection />}
                    {activeSection === 'trustgate' && <TrustGateSection />}
                    {activeSection === 'styleforge' && <StyleForgeSection />}
                    {activeSection === 'contextvault' && <ContextVaultSection />}
                    {activeSection === 'mcp' && <MCPSection />}
                    {activeSection === 'api' && <APISection />}
                </main>
            </div>
        </motion.div>
    );
};

// Section Components
const OverviewSection = () => (
    <div>
        <h1 className="text-2xl font-semibold text-white mb-2">Getting Started</h1>
        <p className="text-slate-400 mb-8">Complete guide to using CodeShield for AI code verification.</p>
        
        <div className="space-y-8">
            <div>
                <h2 className="text-lg font-medium text-white mb-3">Installation</h2>
                <CodeBlock code="pip install -e ." title="Terminal" />
            </div>

            <div>
                <h2 className="text-lg font-medium text-white mb-3">Quick Example</h2>
                <CodeBlock 
                    title="example.py"
                    code={`from codeshield.trustgate.checker import verify_code

result = verify_code('''
def fetch():
    return requests.get(url)
''')

print(f"Valid: {result.is_valid}")
print(f"Issues: {[i.message for i in result.issues]}")
print(f"Fixed: {result.fixed_code}")`}
                />
            </div>

            <div>
                <h2 className="text-lg font-medium text-white mb-3">The Three Pillars</h2>
                <div className="grid gap-3">
                    <FeatureRow 
                        title="TrustGate"
                        description="Verifies AI-generated code before you use it"
                    />
                    <FeatureRow 
                        title="StyleForge"
                        description="Enforces your codebase naming conventions"
                    />
                    <FeatureRow 
                        title="ContextVault"
                        description="Saves and restores your coding session state"
                    />
                </div>
            </div>
        </div>
    </div>
);

const TrustGateSection = () => (
    <div>
        <h1 className="text-2xl font-semibold text-white mb-2">TrustGate</h1>
        <p className="text-slate-400 mb-8">Verification layer for AI-generated code.</p>
        
        <div className="space-y-8">
            <div>
                <h2 className="text-lg font-medium text-white mb-3">Static Analysis</h2>
                <p className="text-slate-400 text-sm mb-3">Quick verification without code execution.</p>
                <CodeBlock 
                    title="Static check"
                    code={`from codeshield.trustgate.checker import verify_code

result = verify_code(code, auto_fix=True)

print(f"Valid: {result.is_valid}")
print(f"Confidence: {result.confidence_score:.0%}")
print(f"Fixed Code: {result.fixed_code}")`}
                />
            </div>

            <div>
                <h2 className="text-lg font-medium text-white mb-3">Sandbox Verification</h2>
                <p className="text-slate-400 text-sm mb-3">Full verification with isolated code execution.</p>
                <CodeBlock 
                    title="Full sandbox check"
                    code={`from codeshield.trustgate.sandbox import full_verification

report = full_verification(code)

print(f"Overall Valid: {report['overall_valid']}")
print(f"Sandbox Output: {report['sandbox_execution']['output']}")`}
                />
            </div>

            <div>
                <h2 className="text-lg font-medium text-white mb-3">What It Catches</h2>
                <ul className="space-y-2 text-sm text-slate-400">
                    <li className="flex items-start gap-2">
                        <CheckIcon />
                        <span>Missing imports (requests, json, etc.)</span>
                    </li>
                    <li className="flex items-start gap-2">
                        <CheckIcon />
                        <span>Syntax errors with exact line numbers</span>
                    </li>
                    <li className="flex items-start gap-2">
                        <CheckIcon />
                        <span>Runtime errors via sandbox execution</span>
                    </li>
                    <li className="flex items-start gap-2">
                        <CheckIcon />
                        <span>Undefined variables and typos</span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
);

const StyleForgeSection = () => (
    <div>
        <h1 className="text-2xl font-semibold text-white mb-2">StyleForge</h1>
        <p className="text-slate-400 mb-8">Convention enforcement for consistent code style.</p>
        
        <div className="space-y-8">
            <div>
                <h2 className="text-lg font-medium text-white mb-3">Usage</h2>
                <CodeBlock 
                    title="Check style"
                    code={`from codeshield.styleforge.corrector import check_style

result = check_style(code, codebase_path="./src")

print(f"Matches Convention: {result.matches_convention}")
for issue in result.issues:
    print(f"  {issue.original} → {issue.suggested}")`}
                />
            </div>

            <div>
                <h2 className="text-lg font-medium text-white mb-3">Supported Conversions</h2>
                <ul className="space-y-2 text-sm text-slate-400">
                    <li className="flex items-start gap-2">
                        <CheckIcon />
                        <span><code className="text-white">camelCase</code> → <code className="text-emerald-400">snake_case</code></span>
                    </li>
                    <li className="flex items-start gap-2">
                        <CheckIcon />
                        <span><code className="text-white">PascalCase</code> → <code className="text-emerald-400">snake_case</code></span>
                    </li>
                    <li className="flex items-start gap-2">
                        <CheckIcon />
                        <span>Detects codebase patterns automatically</span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
);

const ContextVaultSection = () => (
    <div>
        <h1 className="text-2xl font-semibold text-white mb-2">ContextVault</h1>
        <p className="text-slate-400 mb-8">Save and restore your coding session state.</p>
        
        <div className="space-y-8">
            <div>
                <h2 className="text-lg font-medium text-white mb-3">Save Context</h2>
                <CodeBlock 
                    title="Save session"
                    code={`from codeshield.contextvault.capture import save_context

save_context(
    name="debugging-auth",
    files=["src/auth.py", "src/users.py"],
    cursor={"file": "src/auth.py", "line": 42},
    notes="Working on login flow"
)`}
                />
            </div>

            <div>
                <h2 className="text-lg font-medium text-white mb-3">Restore Context</h2>
                <CodeBlock 
                    title="Restore session"
                    code={`from codeshield.contextvault.restore import restore_context

result = restore_context("debugging-auth")
print(result["briefing"])
# "You were working on the auth module around line 42..."`}
                />
            </div>
        </div>
    </div>
);

const MCPSection = () => (
    <div>
        <h1 className="text-2xl font-semibold text-white mb-2">MCP Integration</h1>
        <p className="text-slate-400 mb-8">Use CodeShield with Claude, Cursor, and other AI assistants.</p>
        
        <div className="space-y-8">
            <div>
                <h2 className="text-lg font-medium text-white mb-3">Configuration</h2>
                <CodeBlock 
                    title="mcp_config.json"
                    code={`{
  "mcpServers": {
    "codeshield": {
      "command": "python",
      "args": ["-m", "codeshield.mcp.server"]
    }
  }
}`}
                />
            </div>

            <div>
                <h2 className="text-lg font-medium text-white mb-3">Available Tools</h2>
                <div className="space-y-2">
                    <ToolRow name="verify_code" description="Static code verification" />
                    <ToolRow name="full_verify" description="Verification + sandbox execution" />
                    <ToolRow name="check_style" description="Convention enforcement" />
                    <ToolRow name="save_context" description="Save session state" />
                    <ToolRow name="restore_context" description="Restore with AI briefing" />
                    <ToolRow name="list_contexts" description="List saved sessions" />
                </div>
            </div>
        </div>
    </div>
);

const APISection = () => (
    <div>
        <h1 className="text-2xl font-semibold text-white mb-2">API Reference</h1>
        <p className="text-slate-400 mb-8">HTTP endpoints for frontend integration.</p>
        
        <div className="space-y-4">
            <APIEndpoint method="POST" path="/api/verify" description="Verify code for issues" />
            <APIEndpoint method="POST" path="/api/style" description="Check naming conventions" />
            <APIEndpoint method="POST" path="/api/context/save" description="Save coding context" />
            <APIEndpoint method="POST" path="/api/context/restore" description="Restore context with briefing" />
        </div>
    </div>
);

// Helper Components
const FeatureRow: React.FC<{ title: string; description: string }> = ({ title, description }) => (
    <div className="p-4 bg-slate-800/30 border border-slate-700/40 rounded-lg">
        <h3 className="text-sm font-medium text-white mb-1">{title}</h3>
        <p className="text-sm text-slate-400">{description}</p>
    </div>
);

const ToolRow: React.FC<{ name: string; description: string }> = ({ name, description }) => (
    <div className="flex items-center gap-4 p-3 bg-slate-800/30 border border-slate-700/40 rounded-lg">
        <code className="text-sm text-emerald-400 font-mono">{name}</code>
        <span className="text-sm text-slate-400">{description}</span>
    </div>
);

const APIEndpoint: React.FC<{ method: string; path: string; description: string }> = ({ method, path, description }) => (
    <div className="flex items-center gap-4 p-4 bg-slate-800/30 border border-slate-700/40 rounded-lg">
        <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono rounded">{method}</span>
        <code className="text-sm text-white font-mono">{path}</code>
        <span className="text-sm text-slate-500">{description}</span>
    </div>
);

const CheckIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-emerald-400 mt-0.5 shrink-0">
        <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
);

// Navigation Icons
const GitHubIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
    </svg>
);

const ArrowLeftIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
    </svg>
);

const BookIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
    </svg>
);

const ShieldIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
    </svg>
);

const SparklesIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"/>
        <circle cx="12" cy="12" r="4"/>
    </svg>
);

const FolderIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2v11z"/>
    </svg>
);

const PlugIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22v-5M9 8V2m6 6V2m-9 6h12a1 1 0 011 1v3a6 6 0 01-12 0V9a1 1 0 011-1z"/>
    </svg>
);

const CodeIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/>
    </svg>
);

export default Docs;
