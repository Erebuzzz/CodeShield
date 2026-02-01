import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Logo } from './Logo';

interface DocsProps {
    onBack?: () => void;
}

type DocSection = 'overview' | 'trustgate' | 'styleforge' | 'contextvault' | 'mcp' | 'api';

// Icons
const BookIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
);
const ShieldIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
);
const WandIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 4V2"/><path d="M15 16v-2"/><path d="M8 9h2"/><path d="M20 9h2"/><path d="M17.8 11.8 19 13"/><path d="M15 9h0"/><path d="M17.8 6.2 19 5"/><path d="M3 21l9-9"/><path d="M12.2 6.2 11 5"/></svg>
);
const DatabaseIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
);
const ServerIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
);
const ApiIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
);
const GitHubIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
);
const ArrowLeftIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
);

const CodeBlock: React.FC<{ code: string; title?: string }> = ({ code, title }) => (
    <div className="bg-slate-900/50 border border-brand-500/10 rounded-lg overflow-hidden my-6 shadow-lg shadow-black/20">
        {title && (
            <div className="px-4 py-2 border-b border-white/5 text-xs text-brand-300 font-mono bg-white/5">
                {title}
            </div>
        )}
        <pre className="p-4 text-sm text-slate-300 font-mono overflow-x-auto leading-relaxed custom-scrollbar bg-black/20">
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
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-all duration-200 ${
            active 
                ? 'bg-brand-500/10 text-brand-400 font-medium shadow-[0_0_15px_-3px_rgba(99,102,241,0.2)]' 
                : 'text-slate-400 hover:text-white hover:bg-white/5'
        }`}
    >
        <span className={`transition-colors duration-200 ${active ? 'text-brand-400' : 'text-slate-500 group-hover:text-slate-300'}`}>{icon}</span>
        {label}
    </button>
);

export const Docs: React.FC<DocsProps> = ({ onBack }) => {
    const [activeSection, setActiveSection] = useState<DocSection>('overview');

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-50 bg-[#030305] overflow-y-auto"
        >
            <div className="min-h-screen flex flex-col">
                {/* Header */}
                <header className="border-b border-white/5 px-6 py-4 bg-slate-900/50 backdrop-blur-md sticky top-0 z-20">
                    <div className="max-w-7xl mx-auto flex items-center justify-between">
                        <div className="flex items-center gap-6">
                            <Logo size="sm" />
                            <span className="text-slate-600 font-light">|</span>
                            <span className="text-sm text-slate-400 font-medium tracking-wide uppercas">Documentation</span>
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
                            {onBack && (
                                <button
                                    onClick={onBack}
                                    className="px-4 py-1.5 rounded-full border border-white/10 text-sm text-slate-400 hover:text-white hover:bg-white/5 transition-all flex items-center gap-1.5"
                                >
                                    <ArrowLeftIcon />
                                    Back to App
                                </button>
                            )}
                        </div>
                    </div>
                </header>

                <div className="max-w-7xl mx-auto flex flex-1 w-full relative">
                    {/* Sidebar Navigation */}
                    <aside className="w-64 shrink-0 border-r border-white/5 p-6 sticky top-[73px] h-[calc(100vh-73px)] hidden md:block overflow-y-auto custom-scrollbar">
                        <div className="mb-6 px-3 text-xs font-bold text-slate-500 uppercase tracking-widest">Guide</div>
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
                                icon={<WandIcon />}
                                label="StyleForge"
                            />
                            <NavItem 
                                active={activeSection === 'contextvault'} 
                                onClick={() => setActiveSection('contextvault')}
                                icon={<DatabaseIcon />}
                                label="ContextVault"
                            />
                        </nav>
                        
                        <div className="mt-8 mb-6 px-3 text-xs font-bold text-slate-500 uppercase tracking-widest">Developers</div>
                        <nav className="space-y-1">
                            <NavItem 
                                active={activeSection === 'mcp'} 
                                onClick={() => setActiveSection('mcp')}
                                icon={<ServerIcon />}
                                label="MCP Server"
                            />
                            <NavItem 
                                active={activeSection === 'api'} 
                                onClick={() => setActiveSection('api')}
                                icon={<ApiIcon />}
                                label="API Reference"
                            />
                        </nav>
                    </aside>

                    {/* Main Content */}
                    <main className="flex-1 p-8 md:p-12 max-w-4xl">
                        <motion.div
                            key={activeSection}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            {activeSection === 'overview' && (
                                <div className="space-y-8">
                                    <div>
                                        <h1 className="text-4xl font-display font-light text-white mb-4">Introduction to CodeShield</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            CodeShield is a secure, intelligent coding assistant designed to protect your codebase from malicious patterns and poor practices. It acts as a firewall for your code generation workflow.
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                        {[
                                            { title: 'TrustGate', desc: 'Secure Sandbox Execution', icon: <ShieldIcon /> },
                                            { title: 'StyleForge', desc: 'Auto-formatting & Linting', icon: <WandIcon /> },
                                            { title: 'ContextVault', desc: 'Privacy-first Memory', icon: <DatabaseIcon /> },
                                        ].map((feature, i) => (
                                            <div key={i} className="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-brand-500/30 transition-colors">
                                                <div className="mb-4 text-brand-400">{feature.icon}</div>
                                                <h3 className="text-lg font-medium text-white mb-2">{feature.title}</h3>
                                                <p className="text-sm text-slate-400">{feature.desc}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {activeSection === 'trustgate' && (
                                <div className="space-y-8">
                                    <div>
                                        <h1 className="text-4xl font-display font-light text-white mb-4">TrustGate</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed">
                                            TrustGate validates generated code in a secure, isolated sandbox environment. It detects potential security vulnerabilities, infinite loops, and malicious imports before they touch your production environment.
                                        </p>
                                    </div>

                                    <div className="space-y-4">
                                        <h2 className="text-2xl font-display font-light text-white">How it works</h2>
                                        <ul className="space-y-3 text-slate-400 list-disc pl-5">
                                            <li>Parses Abstract Syntax Tree (AST) to detect dangerous imports (e.g., `os`, `subprocess`).</li>
                                            <li>Analyzes resource usage to prevent denial of service vectors.</li>
                                            <li>Executes code in a restricted container with network isolation.</li>
                                        </ul>
                                    </div>
                                    
                                    <CodeBlock 
                                        title="Example Detection"
                                        code={`# Dangerous code detected by TrustGate
import os
import subprocess

# This will trigger an error
def delete_files():
    subprocess.run("rm -rf /", shell=True)`}
                                    />
                                </div>
                            )}

                            {activeSection === 'mcp' && (
                                <div className="space-y-8">
                                    <div>
                                        <h1 className="text-4xl font-display font-light text-white mb-4">MCP Server Integration</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed">
                                            CodeShield exposes functionality via the Model Context Protocol (MCP), allowing AI models to leverage secure execution and validation capabilities directly.
                                        </p>
                                    </div>

                                    <CodeBlock 
                                        title="MCP Tool Definition"
                                        code={`{
  "name": "verify_code",
  "description": "Verify code security and correctness",
  "inputSchema": {
    "type": "object",
    "properties": {
      "code": { "type": "string" }
    },
    "required": ["code"]
  }
}`}
                                    />
                                </div>
                            )}
                            
                            {(activeSection === 'styleforge') && (
                                <div className="space-y-8">
                                    <div>
                                        <h1 className="text-4xl font-display font-light text-white mb-4">StyleForge</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            StyleForge ensures your generated code feels like home. It analyzes your existing codebase to detect naming conventions and coding patterns, then automatically adapts new code to match.
                                        </p>
                                    </div>

                                    <div className="space-y-4">
                                        <h2 className="text-2xl font-display font-light text-white">Features</h2>
                                        <ul className="space-y-3 text-slate-400 list-disc pl-5">
                                            <li><strong className="text-brand-400">Universal Pattern Detection:</strong> Automatically identifies if your project uses snake_case, camelCase, PascalCase, or SCREAMING_SNAKE.</li>
                                            <li><strong className="text-brand-400">Intelligent Auto-Correction:</strong> Rewrites variable and function names in generated code to match your project's style.</li>
                                            <li><strong className="text-brand-400">Conflict Prevention:</strong> Ensures new identifiers don't clash with existing ones.</li>
                                        </ul>
                                    </div>

                                    <div className="bg-slate-900/50 border border-brand-500/10 rounded-lg p-6">
                                        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Before vs After</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="p-4 bg-red-500/5 border border-red-500/10 rounded-lg">
                                                <div className="text-xs text-red-400 font-mono mb-2">Raw LLM Output</div>
                                                <pre className="text-sm text-slate-400 font-mono"><code>def CalculateTotal(Users_List):
    TotalValue = 0
    for U in Users_List:
        TotalValue += U.price
    return TotalValue</code></pre>
                                            </div>
                                            <div className="p-4 bg-emerald-500/5 border border-emerald-500/10 rounded-lg">
                                                <div className="text-xs text-emerald-400 font-mono mb-2">StyleForge Adjusted (snake_case)</div>
                                                <pre className="text-sm text-slate-300 font-mono"><code>def calculate_total(users_list):
    total_value = 0
    for user in users_list:
        total_value += user.price
    return total_value</code></pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {(activeSection === 'contextvault') && (
                                <div className="space-y-8">
                                    <div>
                                        <h1 className="text-4xl font-display font-light text-white mb-4">ContextVault</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            ContextVault acts like a "Save Game" for your development workflow. It captures your entire mental state—open files, cursor positions, and notes—so you can switch tasks without losing focus.
                                        </p>
                                    </div>

                                    <div className="space-y-4">
                                        <h2 className="text-2xl font-display font-light text-white">Capabilities</h2>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                                                <div className="text-brand-400 mb-2"><DatabaseIcon /></div>
                                                <h3 className="text-white font-medium mb-1">State Persistence</h3>
                                                <p className="text-sm text-slate-400">Saves open files, active tabs, and exact cursor locations to a local SQLite database.</p>
                                            </div>
                                            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                                                <div className="text-brand-400 mb-2"><WandIcon /></div>
                                                <h3 className="text-white font-medium mb-1">Instant Restore</h3>
                                                <p className="text-sm text-slate-400">One-click restoration brings your IDE back to the exact moment you left off.</p>
                                            </div>
                                        </div>
                                    </div>

                                    <CodeBlock 
                                        title="Context Structure (JSON)"
                                        code={`{
  "name": "refactoring-auth-module",
  "created_at": "2023-10-27T10:30:00Z",
  "files": [
    "src/auth/login.py",
    "src/auth/user.py"
  ],
  "cursor": {
    "file": "src/auth/login.py",
    "line": 42,
    "column": 15
  },
  "notes": "Remember to fix the token expiration logic."
}`}
                                    />
                                </div>
                            )}

                            {(activeSection === 'api') && (
                                <div className="space-y-8">
                                    <div>
                                        <h1 className="text-4xl font-display font-light text-white mb-4">API Reference</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            The CodeShield API allows you to integrate security scanning and style enforcement directly into your CI/CD pipelines or custom tools.
                                        </p>
                                    </div>

                                    <div className="space-y-6">
                                        <div className="border border-white/5 rounded-xl overflow-hidden">
                                            <div className="bg-white/5 px-4 py-3 flex items-center gap-3 border-b border-white/5">
                                                <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">POST</span>
                                                <code className="text-sm text-slate-300">/api/verify</code>
                                            </div>
                                            <div className="p-4">
                                                <p className="text-sm text-slate-400 mb-4">Analyzes code for security vulnerabilities and dangerous patterns.</p>
                                                <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Request Body</h4>
                                                <pre className="bg-black/30 p-3 rounded text-xs font-mono text-slate-300"><code>{`{
  "code": "print('hello')",
  "auto_fix": true,
  "use_sandbox": false
}`}</code></pre>
                                            </div>
                                        </div>

                                        <div className="border border-white/5 rounded-xl overflow-hidden">
                                            <div className="bg-white/5 px-4 py-3 flex items-center gap-3 border-b border-white/5">
                                                <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">POST</span>
                                                <code className="text-sm text-slate-300">/api/style</code>
                                            </div>
                                            <div className="p-4">
                                                <p className="text-sm text-slate-400 mb-4">Checks code against the project's detected style conventions.</p>
                                                <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Request Body</h4>
                                                <pre className="bg-black/30 p-3 rounded text-xs font-mono text-slate-300"><code>{`{
  "code": "def MyFunction(): pass",
  "codebase_path": "./src"
}`}</code></pre>
                                            </div>
                                        </div>
                                        
                                        <div className="border border-white/5 rounded-xl overflow-hidden">
                                            <div className="bg-white/5 px-4 py-3 flex items-center gap-3 border-b border-white/5">
                                                <span className="px-2 py-0.5 rounded text-xs font-bold bg-blue-500/20 text-blue-400">GET</span>
                                                <code className="text-sm text-slate-300">/api/health</code>
                                            </div>
                                            <div className="p-4">
                                                <p className="text-sm text-slate-400">Checks if the API server is online and modules are loaded.</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    </main>
                </div>
            </div>
        </motion.div>
    );
};

export default Docs;
