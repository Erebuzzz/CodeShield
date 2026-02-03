import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Logo } from './Logo';

interface DocsProps {
    onBack?: () => void;
}

type DocSection = 'overview' | 'trustgate' | 'styleforge' | 'contextvault' | 'metrics' | 'tokens' | 'mcp' | 'api' | 'faq' | 'troubleshooting';

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
const QuestionIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
);
const WrenchIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
);
const ChartIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
);
const ZapIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
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
                            <NavItem 
                                active={activeSection === 'metrics'} 
                                onClick={() => setActiveSection('metrics')}
                                icon={<ChartIcon />}
                                label="Metrics"
                            />
                            <NavItem 
                                active={activeSection === 'tokens'} 
                                onClick={() => setActiveSection('tokens')}
                                icon={<ZapIcon />}
                                label="Token Efficiency"
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
                        
                        <div className="mb-6 px-3 text-[10px] font-bold text-slate-600 uppercase tracking-widest mt-8">Help</div>
                        <nav className="space-y-1">
                            <NavItem 
                                active={activeSection === 'faq'} 
                                onClick={() => setActiveSection('faq')}
                                icon={<QuestionIcon />}
                                label="FAQ"
                            />
                            <NavItem 
                                active={activeSection === 'troubleshooting'} 
                                onClick={() => setActiveSection('troubleshooting')}
                                icon={<WrenchIcon />}
                                label="Troubleshooting"
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

                                    {/* Installation */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">Quick Installation</h2>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="p-6 rounded-2xl bg-gradient-to-br from-red-500/10 to-transparent border border-red-500/20">
                                                <div className="flex items-center gap-3 mb-4">
                                                    <span className="text-2xl">📦</span>
                                                    <h3 className="text-lg font-medium text-white">npm (MCP Server)</h3>
                                                    <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Recommended</span>
                                                </div>
                                                <code className="block bg-black/30 rounded-lg p-3 text-sm text-slate-300 font-mono mb-3">npm install -g codeshield-mcp</code>
                                                <p className="text-sm text-slate-400">For Claude Desktop, Cursor, and other MCP clients</p>
                                            </div>
                                            <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20">
                                                <div className="flex items-center gap-3 mb-4">
                                                    <span className="text-2xl">🐍</span>
                                                    <h3 className="text-lg font-medium text-white">pip (Python Library)</h3>
                                                </div>
                                                <code className="block bg-black/30 rounded-lg p-3 text-sm text-slate-300 font-mono mb-3">pip install codeshield-ai</code>
                                                <p className="text-sm text-slate-400">For Python projects and API integration</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Features Grid */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                        {[
                                            { title: 'TrustGate', desc: 'Security validation & sandbox execution', icon: <ShieldIcon /> },
                                            { title: 'StyleForge', desc: 'Convention detection & auto-formatting', icon: <WandIcon /> },
                                            { title: 'ContextVault', desc: 'State persistence & AI-powered restore', icon: <DatabaseIcon /> },
                                            { title: 'Metrics', desc: 'Real-time statistics & observability', icon: <ChartIcon /> },
                                            { title: 'Token Efficiency', desc: 'Up to 90% token savings', icon: <ZapIcon /> },
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
                                            TrustGate validates generated code in a secure, isolated sandbox environment. It detects potential security vulnerabilities, missing imports, syntax errors, and undefined variables before they touch your production environment.
                                        </p>
                                    </div>

                                    <div className="space-y-6">
                                        <h2 className="text-2xl font-display font-medium text-white">Core Capabilities</h2>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {[
                                                { title: "Syntax Validation", desc: "AST parsing catches syntax errors, missing colons, unmatched brackets before execution" },
                                                { title: "Import Detection", desc: "Identifies missing imports from stdlib (os, json, re) and third-party packages (requests, numpy)" },
                                                { title: "Auto-Fix", desc: "Automatically adds missing imports to your code with 0 LLM tokens for common fixes" },
                                                { title: "Undefined Names", desc: "Detects potentially undefined variables and references" },
                                                { title: "Sandbox Execution", desc: "Runs code in Daytona's isolated environment to catch runtime issues" },
                                                { title: "Confidence Scoring", desc: "0-100% confidence score based on issue severity and count" }
                                            ].map((item, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                                                    <strong className="text-emerald-400 block mb-1">{item.title}</strong>
                                                    <span className="text-slate-400 text-sm">{item.desc}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Example: Missing Import Detection</h2>
                                        <CodeBlock 
                                            title="auto_fix_example.py"
                                            code={`# Original code with missing import
def fetch_data(url):
    return requests.get(url).json()

# TrustGate output:
# - is_valid: False
# - issues: ["Missing import: requests"]
# - confidence_score: 80%
# - fixed_code:
import requests

def fetch_data(url):
    return requests.get(url).json()`}
                                        />
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Python API Usage</h2>
                                        <CodeBlock 
                                            title="trustgate_example.py"
                                            code={`from codeshield.trustgate.checker import verify_code
from codeshield.trustgate.sandbox import full_verification

# Quick static analysis
result = verify_code(code, auto_fix=True)
print(f"Valid: {result.is_valid}")
print(f"Issues: {result.issues}")
print(f"Confidence: {result.confidence_score:.0%}")
print(result.fixed_code)

# Full sandbox verification (includes runtime check)
result = full_verification(code)
print(f"Sandbox passed: {result['sandbox_result']['passed']}")`}
                                        />
                                    </div>
                                </div>
                            )}

                            {activeSection === 'styleforge' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">StyleForge</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            StyleForge ensures your generated code feels like home. It analyzes up to 50 files from your existing codebase to detect naming conventions, then automatically adapts new code to match your project's style.
                                        </p>
                                    </div>

                                    <div className="space-y-6">
                                        <h2 className="text-2xl font-display font-medium text-white">Supported Conventions</h2>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {[
                                                { title: "snake_case", desc: "Python standard (PEP 8) - get_user_data, total_value", example: "def get_user_data():" },
                                                { title: "camelCase", desc: "JavaScript/Java style - getUserData, totalValue", example: "function getUserData()" },
                                                { title: "PascalCase", desc: "Class names - UserData, TotalValue", example: "class UserData:" },
                                                { title: "SCREAMING_SNAKE", desc: "Constants - MAX_VALUE, API_KEY", example: "MAX_RETRIES = 3" }
                                            ].map((item, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                                                    <strong className="text-emerald-400 block mb-1">{item.title}</strong>
                                                    <span className="text-slate-400 text-sm block mb-2">{item.desc}</span>
                                                    <code className="text-xs text-slate-500">{item.example}</code>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="space-y-6">
                                        <h2 className="text-2xl font-display font-medium text-white">Features</h2>
                                        <div className="grid grid-cols-1 gap-4">
                                            {[
                                                { title: "Pattern Detection", desc: "Automatically identifies the dominant naming convention in your codebase by scanning functions, variables, and classes." },
                                                { title: "Codebase Analysis", desc: "Scans up to 50 Python files to determine your project's style, ignoring test files and virtual environments." },
                                                { title: "Auto-Correction", desc: "Converts variable and function names to match detected project conventions using LLM assistance." },
                                                { title: "Typo Detection", desc: "Uses Levenshtein distance to find similar existing names that might be typos (e.g., 'usre' → 'user')." }
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
                                                title="StyleForge Output (snake_case)"
                                                code={`def calculate_total(users_list):
    total_value = 0
    for user in users_list:
        total_value += user.price
    return total_value`}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Python API Usage</h2>
                                        <CodeBlock 
                                            title="styleforge_example.py"
                                            code={`from codeshield.styleforge.corrector import check_style

result = check_style(
    code="def GetUserData(): pass",
    codebase_path="./src"
)

print(result.conventions_detected)  
# {'functions': 'snake_case', 'variables': 'snake_case'}

print(result.corrected_code)
# def get_user_data(): pass`}
                                        />
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

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Python API Usage</h2>
                                        <CodeBlock 
                                            title="contextvault_example.py"
                                            code={`from codeshield.contextvault.capture import save_context, list_contexts
from codeshield.contextvault.restore import restore_context

# Save current state
save_context(
    name="auth-refactor",
    files=["src/auth.py", "tests/test_auth.py"],
    cursor={"file": "src/auth.py", "line": 42, "column": 10},
    notes="Fixing token expiration logic"
)

# List all saved contexts
contexts = list_contexts()
for ctx in contexts:
    print(f"{ctx['name']} - {ctx['created_at']}")

# Restore with AI-powered briefing
result = restore_context("auth-refactor")
print(result["briefing"])
# "You were working on auth token logic at line 42..."`}
                                        />
                                    </div>
                                </div>
                            )}

                            {activeSection === 'metrics' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">Metrics & Observability</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            CodeShield provides real-time, transparent statistics tracking for all features. Every verification, style check, and context operation is measured and persisted to SQLite for historical analysis.
                                        </p>
                                    </div>

                                    <div className="space-y-6">
                                        <h2 className="text-2xl font-display font-medium text-white">Tracked Metrics</h2>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {[
                                                { 
                                                    title: "TrustGate Metrics", 
                                                    items: ["Total verifications", "Issues detected", "Auto-fixes applied", "Fix success rate", "Sandbox executions", "Sandbox pass rate"]
                                                },
                                                { 
                                                    title: "StyleForge Metrics", 
                                                    items: ["Style checks performed", "Conventions detected", "Corrections applied", "Detection accuracy"]
                                                },
                                                { 
                                                    title: "ContextVault Metrics", 
                                                    items: ["Contexts saved", "Contexts restored", "Active contexts", "Restore success rate"]
                                                },
                                                { 
                                                    title: "Token Metrics", 
                                                    items: ["Input tokens used", "Output tokens used", "Tokens saved by cache", "Token efficiency ratio", "Estimated cost (USD)"]
                                                }
                                            ].map((group, i) => (
                                                <div key={i} className="p-5 rounded-xl bg-white/[0.02] border border-white/5">
                                                    <strong className="text-emerald-400 block mb-3">{group.title}</strong>
                                                    <ul className="space-y-1">
                                                        {group.items.map((item, j) => (
                                                            <li key={j} className="text-slate-400 text-sm flex items-center gap-2">
                                                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/50"></span>
                                                                {item}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">API Endpoints</h2>
                                        <div className="space-y-3">
                                            {[
                                                { endpoint: "GET /api/metrics", desc: "Full metrics summary for all features" },
                                                { endpoint: "GET /api/metrics/trustgate", desc: "TrustGate-specific statistics" },
                                                { endpoint: "GET /api/metrics/styleforge", desc: "StyleForge-specific statistics" },
                                                { endpoint: "GET /api/metrics/tokens", desc: "Token usage and efficiency data" }
                                            ].map((item, i) => (
                                                <div key={i} className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center justify-between">
                                                    <code className="text-emerald-400 text-sm">{item.endpoint}</code>
                                                    <span className="text-slate-400 text-xs">{item.desc}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Python API Usage</h2>
                                        <CodeBlock 
                                            title="metrics_example.py"
                                            code={`from codeshield.utils.metrics import get_metrics

metrics = get_metrics()
summary = metrics.get_summary()

# TrustGate stats
tg = summary['trustgate']
print(f"Verifications: {tg['total_verifications']}")
print(f"Detection rate: {tg['detection_rate']}%")
print(f"Fix success rate: {tg['fix_success_rate']}%")

# Token stats
tokens = summary['tokens']
print(f"Total tokens: {tokens['total_tokens']}")
print(f"Efficiency: {tokens['token_efficiency']}")
print(f"Est. cost: \${tokens['estimated_cost_usd']:.4f}")`}
                                        />
                                    </div>
                                </div>
                            )}

                            {activeSection === 'tokens' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">Token Efficiency</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            CodeShield implements advanced optimization techniques to minimize LLM token usage, achieving up to 90% savings on common operations. This translates directly to cost savings and faster response times.
                                        </p>
                                    </div>

                                    {/* Savings Table */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">Optimization Techniques</h2>
                                        <div className="space-y-4">
                                            {[
                                                { 
                                                    title: "Local Processing", 
                                                    savings: "100%",
                                                    desc: "Fixes 35+ common imports (json, os, requests, numpy, etc.) without any LLM call",
                                                    color: "emerald"
                                                },
                                                { 
                                                    title: "Response Caching", 
                                                    savings: "100%",
                                                    desc: "SQLite-based cache returns identical responses for repeated requests instantly",
                                                    color: "emerald"
                                                },
                                                { 
                                                    title: "Prompt Compression", 
                                                    savings: "40-60%",
                                                    desc: "Shorter, optimized prompts that produce the same quality results",
                                                    color: "teal"
                                                },
                                                { 
                                                    title: "Dynamic max_tokens", 
                                                    savings: "50-75%",
                                                    desc: "Adaptive response limits (100-500 tokens) based on task complexity vs fixed 2000",
                                                    color: "teal"
                                                },
                                                { 
                                                    title: "Model Tiering", 
                                                    savings: "30-50%",
                                                    desc: "Uses cheaper/faster models for simple tasks, reserves powerful models for complex work",
                                                    color: "cyan"
                                                }
                                            ].map((opt, i) => (
                                                <div key={i} className={`p-5 rounded-xl bg-${opt.color}-500/5 border border-${opt.color}-500/20`}>
                                                    <div className="flex items-center justify-between mb-2">
                                                        <strong className={`text-${opt.color}-400`}>{opt.title}</strong>
                                                        <span className={`px-2 py-1 rounded text-xs font-bold bg-${opt.color}-500/20 text-${opt.color}-400`}>{opt.savings} savings</span>
                                                    </div>
                                                    <p className="text-slate-400 text-sm">{opt.desc}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Supported Local Fixes */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Zero-Token Import Fixes</h2>
                                        <p className="text-slate-400 mb-4">These 35+ imports are fixed locally without any LLM call:</p>
                                        <div className="flex flex-wrap gap-2">
                                            {['json', 'os', 'sys', 're', 'math', 'random', 'datetime', 'time', 'pathlib', 'typing', 'dataclasses', 'collections', 'itertools', 'functools', 'requests', 'httpx', 'asyncio', 'logging', 'subprocess', 'tempfile', 'shutil', 'glob', 'csv', 'sqlite3', 'hashlib', 'base64', 'copy', 'io', 'threading', 'uuid', 'enum', 'abc', 'contextlib', 'pydantic', 'fastapi', 'flask', 'numpy', 'pandas', 'pytest'].map((pkg, i) => (
                                                <code key={i} className="px-2 py-1 rounded bg-white/5 text-emerald-400 text-xs border border-white/10">{pkg}</code>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">How It Works</h2>
                                        <CodeBlock 
                                            title="token_optimizer_example.py"
                                            code={`from codeshield.utils.token_optimizer import (
    LocalProcessor, 
    get_token_optimizer
)

# Example: Code with missing import
code = "data = json.loads(response)"
issues = ["Missing import: json"]

# Step 1: Try local fix first (0 tokens!)
if LocalProcessor.can_fix_locally(code, issues):
    fixed = LocalProcessor.fix_locally(code, issues)
    # Result: "import json\\ndata = json.loads(response)"
    print("Fixed locally - 0 tokens used!")
else:
    # Step 2: Fall back to LLM with optimizations
    # - Compressed prompt (40% smaller)
    # - Dynamic max_tokens based on code size
    # - Model tiering (cheap model for simple fix)
    # - Response cached for future requests
    pass

# Check efficiency stats
optimizer = get_token_optimizer()
stats = optimizer.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache hit rate: {stats['cache_hit_rate']}%")
print(f"Tokens saved: {stats['tokens_saved_by_cache']}")`}
                                        />
                                    </div>

                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">API Endpoints</h2>
                                        <div className="space-y-3">
                                            {[
                                                { endpoint: "GET /api/tokens/efficiency", desc: "Token optimization statistics and savings" },
                                                { endpoint: "GET /api/tokens/budget", desc: "Budget limits and remaining tokens" }
                                            ].map((item, i) => (
                                                <div key={i} className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center justify-between">
                                                    <code className="text-emerald-400 text-sm">{item.endpoint}</code>
                                                    <span className="text-slate-400 text-xs">{item.desc}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeSection === 'mcp' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">MCP Server Integration</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            CodeShield exposes functionality via the Model Context Protocol (MCP), allowing AI models like Claude and Cursor to leverage secure execution and validation capabilities directly.
                                        </p>
                                    </div>

                                    {/* Installation */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Quick Install</h2>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                            <div className="p-4 rounded-xl bg-gradient-to-r from-red-500/10 to-transparent border border-red-500/20">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <span className="text-red-400 font-bold">npm</span>
                                                    <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">Recommended</span>
                                                </div>
                                                <code className="text-sm text-slate-300">npm install -g codeshield-mcp</code>
                                            </div>
                                            <div className="p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-transparent border border-blue-500/20">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <span className="text-blue-400 font-bold">pip</span>
                                                </div>
                                                <code className="text-sm text-slate-300">pip install codeshield-ai</code>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Available Tools */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">Available MCP Tools</h2>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {[
                                                { name: "verify_code", desc: "Verify Python code for syntax errors and issues" },
                                                { name: "full_verify", desc: "Complete verification with sandbox execution" },
                                                { name: "check_style", desc: "Check code against codebase conventions" },
                                                { name: "save_context", desc: "Save current coding context" },
                                                { name: "restore_context", desc: "Restore a previously saved context" },
                                                { name: "list_contexts", desc: "List all saved contexts" }
                                            ].map((tool, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                                                    <code className="text-emerald-400 text-sm">{tool.name}</code>
                                                    <p className="text-slate-400 text-xs mt-1">{tool.desc}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Configuration */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Claude Desktop Configuration</h2>
                                        <p className="text-slate-400 mb-4">Add to your <code className="text-emerald-400">claude_desktop_config.json</code>:</p>
                                        <CodeBlock 
                                            title="claude_desktop_config.json (npm - Recommended)"
                                            code={`{
  "mcpServers": {
    "codeshield": {
      "command": "npx",
      "args": ["codeshield-mcp"]
    }
  }
}`}
                                        />
                                        <CodeBlock 
                                            title="claude_desktop_config.json (Python alternative)"
                                            code={`{
  "mcpServers": {
    "codeshield": {
      "command": "python",
      "args": ["-m", "codeshield.mcp.server"],
      "cwd": "\${workspaceFolder}",
      "env": {
        "PYTHONPATH": "\${workspaceFolder}/src"
      }
    }
  }
}`}
                                        />
                                    </div>

                                    {/* Observability */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Checking Connectivity</h2>
                                        <p className="text-slate-400 mb-4">Use these tools to verify MCP is working:</p>
                                        <CodeBlock 
                                            title="In Claude/Cursor"
                                            code={`# Check server health and provider status
mcp_health()

# Test LLM connection (uses first available provider)
test_llm_connection()

# Test specific provider
test_llm_connection(provider="cometapi")
test_llm_connection(provider="novita")`}
                                        />
                                    </div>

                                    {/* LLM Providers */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Supported LLM Providers</h2>
                                        <div className="space-y-3">
                                            {[
                                                { 
                                                    name: "CometAPI", 
                                                    desc: "Unified gateway to 100+ models (primary LLM)", 
                                                    url: "apidoc.cometapi.com",
                                                    envVar: "COMETAPI_KEY",
                                                    required: true
                                                },
                                                { 
                                                    name: "Novita.ai", 
                                                    desc: "Cost-effective open-source inference (secondary LLM)", 
                                                    url: "novita.ai/docs",
                                                    envVar: "NOVITA_API_KEY",
                                                    required: true
                                                },
                                                { 
                                                    name: "AIML API", 
                                                    desc: "Fallback LLM provider", 
                                                    url: "aimlapi.com",
                                                    envVar: "AIML_API_KEY",
                                                    required: true
                                                },
                                                { 
                                                    name: "Daytona", 
                                                    desc: "Secure sandbox execution environment", 
                                                    url: "daytona.io/docs",
                                                    envVar: "DAYTONA_API_KEY",
                                                    required: true
                                                },
                                                { 
                                                    name: "LeanMCP", 
                                                    desc: "MCP observability & analytics platform", 
                                                    url: "docs.leanmcp.com",
                                                    envVar: "LEANMCP_KEY",
                                                    required: true
                                                }
                                            ].map((provider, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-gradient-to-r from-emerald-500/5 to-transparent border border-emerald-500/10">
                                                    <div className="flex items-center justify-between">
                                                        <div>
                                                            <strong className="text-white">{provider.name}</strong>
                                                            <span className="text-slate-400 text-sm ml-2">- {provider.desc}</span>
                                                            {provider.required && <span className="ml-2 text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/20">Required</span>}
                                                        </div>
                                                        <code className="text-xs text-slate-500">{provider.envVar}</code>
                                                    </div>
                                                    <a href={`https://${provider.url}`} target="_blank" rel="noopener" className="text-emerald-400 text-xs hover:underline">{provider.url}</a>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeSection === 'api' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">API Reference</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            The CodeShield REST API allows you to integrate security scanning, style enforcement, and observability directly into your CI/CD pipelines or custom tools.
                                        </p>
                                    </div>

                                    {/* Core Endpoints */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">Core Endpoints</h2>
                                        <div className="space-y-6">
                                            <div className="border border-white/5 rounded-2xl overflow-hidden bg-white/[0.01]">
                                                <div className="bg-white/[0.03] px-5 py-4 flex items-center gap-3 border-b border-white/5">
                                                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/10">POST</span>
                                                    <code className="text-sm text-slate-300 font-mono">/api/verify</code>
                                                    <span className="text-slate-500 text-xs ml-auto">Verify code for issues</span>
                                                </div>
                                                <div className="p-6">
                                                    <CodeBlock
                                                        title="Request"
                                                        code={`{
  "code": "x = json.loads(data)",
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
                                                    <span className="text-slate-500 text-xs ml-auto">Check style conventions</span>
                                                </div>
                                                <div className="p-6">
                                                    <CodeBlock
                                                        title="Request"
                                                        code={`{
  "code": "def MyFunction(): pass",
  "codebase_path": "./src"
}`}
                                                    />
                                                </div>
                                            </div>

                                            <div className="border border-white/5 rounded-2xl overflow-hidden bg-white/[0.01]">
                                                <div className="bg-white/[0.03] px-5 py-4 flex items-center gap-3 border-b border-white/5">
                                                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/10">POST</span>
                                                    <code className="text-sm text-slate-300 font-mono">/api/context/save</code>
                                                    <span className="text-slate-500 text-xs ml-auto">Save coding context</span>
                                                </div>
                                                <div className="p-6">
                                                    <CodeBlock
                                                        title="Request"
                                                        code={`{
  "name": "auth-refactor",
  "files": ["src/auth.py"],
  "cursor": {"file": "src/auth.py", "line": 42},
  "notes": "Fixing token logic"
}`}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Observability Endpoints */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">Observability Endpoints</h2>
                                        <div className="grid grid-cols-1 gap-3">
                                            {[
                                                { method: "GET", endpoint: "/api/health", desc: "Server health check" },
                                                { method: "GET", endpoint: "/api/metrics", desc: "Full metrics summary" },
                                                { method: "GET", endpoint: "/api/metrics/trustgate", desc: "TrustGate statistics" },
                                                { method: "GET", endpoint: "/api/metrics/styleforge", desc: "StyleForge statistics" },
                                                { method: "GET", endpoint: "/api/metrics/tokens", desc: "Token usage metrics" },
                                                { method: "GET", endpoint: "/api/tokens/efficiency", desc: "Token optimization stats" },
                                                { method: "GET", endpoint: "/api/providers/status", desc: "LLM provider status" },
                                                { method: "GET", endpoint: "/api/providers/test", desc: "Test LLM connectivity" },
                                                { method: "GET", endpoint: "/api/integrations/status", desc: "All integrations status" },
                                                { method: "GET", endpoint: "/api/contexts", desc: "List saved contexts" }
                                            ].map((item, i) => (
                                                <div key={i} className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center gap-3">
                                                    <span className="px-2 py-0.5 rounded text-xs font-bold bg-blue-500/20 text-blue-400">{item.method}</span>
                                                    <code className="text-emerald-400 text-sm flex-1">{item.endpoint}</code>
                                                    <span className="text-slate-500 text-xs">{item.desc}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Example Response */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Example: Metrics Response</h2>
                                        <CodeBlock
                                            title="GET /api/metrics"
                                            code={`{
  "trustgate": {
    "total_verifications": 150,
    "issues_detected": 45,
    "auto_fixes_applied": 38,
    "detection_rate": 30.0,
    "fix_success_rate": 84.4,
    "sandbox_executions": 25,
    "sandbox_success_rate": 92.0
  },
  "styleforge": {
    "total_checks": 80,
    "conventions_detected": 75,
    "corrections_applied": 60
  },
  "tokens": {
    "total_input_tokens": 15000,
    "total_output_tokens": 8000,
    "tokens_saved_by_cache": 12000,
    "token_efficiency": 1.88,
    "estimated_cost_usd": 0.0115
  }
}`}
                                        />
                                    </div>
                                </div>
                            )}

                            {activeSection === 'faq' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">Frequently Asked Questions</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            Common questions about CodeShield, its features, integrations, and token efficiency.
                                        </p>
                                    </div>

                                    <div className="space-y-6">
                                        {[
                                            {
                                                q: "What integrations are required?",
                                                a: "CodeShield requires 5 services: CometAPI (primary LLM), Novita.ai (secondary LLM), AIML API (fallback), Daytona (sandbox execution), and LeanMCP (observability). All API keys must be configured in .env for full functionality."
                                            },
                                            {
                                                q: "How much can I save on tokens?",
                                                a: "CodeShield achieves up to 90% token savings through: local processing (100% savings for 35+ common imports), response caching (100% for repeated requests), prompt compression (40-60%), dynamic max_tokens (50-75%), and model tiering (30-50%)."
                                            },
                                            {
                                                q: "What is local processing?",
                                                a: "Local processing fixes common imports like json, os, requests, numpy, pandas, etc. without making any LLM call. This means 0 tokens and instant results for the most common code issues. 35+ imports are supported."
                                            },
                                            {
                                                q: "How do I check if all services are connected?",
                                                a: "Use GET /api/integrations/status to check all services, or mcp_health() in Claude/Cursor. The response shows which integrations are configured and their current status."
                                            },
                                            {
                                                q: "What is CometAPI?",
                                                a: "CometAPI is a unified AI gateway providing access to 100+ models (GPT, Claude, Llama, DeepSeek) through a single OpenAI-compatible API. It's the primary LLM provider with free tier models like deepseek-chat. Docs: apidoc.cometapi.com"
                                            },
                                            {
                                                q: "What is Novita.ai used for?",
                                                a: "Novita.ai is the secondary LLM provider offering cost-effective inference for open-source models. It automatically takes over if CometAPI fails, providing redundancy. Docs: novita.ai/docs"
                                            },
                                            {
                                                q: "What is LeanMCP?",
                                                a: "LeanMCP provides production-grade MCP infrastructure with observability, metrics tracking, and analytics. It tracks tool usage, performance, and health status across all MCP calls. Docs: docs.leanmcp.com"
                                            },
                                            {
                                                q: "What is Daytona used for?",
                                                a: "Daytona provides secure sandbox execution for the full_verify tool. It runs untrusted code in an isolated environment to detect runtime issues without risking the host system. Docs: daytona.io/docs"
                                            },
                                            {
                                                q: "What's the difference between verify_code and full_verify?",
                                                a: "verify_code does fast static analysis (AST parsing, import checking) - no sandbox needed. full_verify additionally runs code in a sandboxed Daytona environment to catch runtime issues like infinite loops."
                                            },
                                            {
                                                q: "How does StyleForge detect conventions?",
                                                a: "StyleForge scans up to 50 Python files in your codebase, extracts function and variable names, then determines the dominant pattern (snake_case, camelCase, PascalCase) using pattern matching."
                                            },
                                            {
                                                q: "Is the response caching secure?",
                                                a: "Yes, responses are cached in a local SQLite database keyed by a hash of the prompt. Cache is local to your machine and not shared. You can clear the cache anytime."
                                            },
                                            {
                                                q: "How do I integrate with Claude Desktop?",
                                                a: "Add the mcp_config.json configuration to your Claude Desktop settings. This registers CodeShield's tools (verify_code, check_style, etc.) so Claude can use them during conversations."
                                            }
                                        ].map((faq, i) => (
                                            <div key={i} className="p-5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-emerald-500/20 transition-colors">
                                                <h3 className="text-white font-medium mb-3 flex items-start gap-3">
                                                    <span className="text-emerald-400 mt-0.5"><QuestionIcon /></span>
                                                    {faq.q}
                                                </h3>
                                                <p className="text-slate-400 text-sm leading-relaxed pl-7">{faq.a}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {activeSection === 'troubleshooting' && (
                                <div className="space-y-10">
                                    <div>
                                        <h1 className="text-4xl font-display font-medium text-white mb-4">Troubleshooting</h1>
                                        <p className="text-lg text-slate-400 leading-relaxed font-light">
                                            Common issues and their solutions when working with CodeShield.
                                        </p>
                                    </div>

                                    {/* Connectivity Issues */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">LLM Provider Issues</h2>
                                        <div className="space-y-4">
                                            {[
                                                {
                                                    issue: "LLM observability shows 0 calls",
                                                    solution: "Check that at least one API key is set in .env (COMETAPI_KEY, NOVITA_API_KEY, or AIML_API_KEY). Test connectivity with GET /api/providers/test."
                                                },
                                                {
                                                    issue: "CometAPI returns 401 Unauthorized",
                                                    solution: "Verify your API key at api.cometapi.com/console/token. Ensure the key starts with 'sk-' and is correctly copied without extra spaces."
                                                },
                                                {
                                                    issue: "Novita.ai requests failing",
                                                    solution: "Check your credit balance at novita.ai/billing. The API requires a positive balance. Verify the key at novita.ai/settings/key-management."
                                                },
                                                {
                                                    issue: "All providers failing (fallback exhausted)",
                                                    solution: "Check network connectivity. Verify .env file is in the project root. Restart the server after changing environment variables."
                                                }
                                            ].map((item, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-red-500/5 border border-red-500/10">
                                                    <strong className="text-red-400 block mb-2">❌ {item.issue}</strong>
                                                    <span className="text-slate-400 text-sm">✅ {item.solution}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* MCP Issues */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">MCP Server Issues</h2>
                                        <div className="space-y-4">
                                            {[
                                                {
                                                    issue: "MCP tools not appearing in Claude/Cursor",
                                                    solution: "Ensure mcp_config.json is added to your MCP client settings. Check PYTHONPATH includes ./src. Restart the MCP client."
                                                },
                                                {
                                                    issue: "'mcp' module not found",
                                                    solution: "Install the MCP SDK: pip install mcp. This is required for the FastMCP server implementation."
                                                },
                                                {
                                                    issue: "mcp_health returns empty provider stats",
                                                    solution: "This is normal on fresh start. Stats accumulate as LLM calls are made. Make a test call to populate stats."
                                                }
                                            ].map((item, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
                                                    <strong className="text-amber-400 block mb-2">⚠️ {item.issue}</strong>
                                                    <span className="text-slate-400 text-sm">✅ {item.solution}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* API Issues */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-6">API Server Issues</h2>
                                        <div className="space-y-4">
                                            {[
                                                {
                                                    issue: "CORS errors in browser",
                                                    solution: "The API server allows localhost:5173 by default. For production, update CORS settings in api_server.py."
                                                },
                                                {
                                                    issue: "Backend modules not loaded",
                                                    solution: "Run the server as a module: python -m uvicorn codeshield.api_server:app. Ensure PYTHONPATH includes src/."
                                                },
                                                {
                                                    issue: "Sandbox verification timeout",
                                                    solution: "Code with infinite loops or heavy computation may timeout. Check for while True loops or reduce computation complexity."
                                                }
                                            ].map((item, i) => (
                                                <div key={i} className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/10">
                                                    <strong className="text-blue-400 block mb-2">🔧 {item.issue}</strong>
                                                    <span className="text-slate-400 text-sm">✅ {item.solution}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Quick Diagnostic */}
                                    <div>
                                        <h2 className="text-2xl font-display font-medium text-white mb-4">Quick Diagnostic Commands</h2>
                                        <CodeBlock 
                                            title="diagnostic.sh"
                                            code={`# Check API server health
curl http://localhost:8000/api/health

# Check LLM provider status
curl http://localhost:8000/api/providers/status

# Test LLM connectivity (with CometAPI)
curl "http://localhost:8000/api/providers/test?provider=cometapi"

# Test LLM connectivity (with Novita)
curl "http://localhost:8000/api/providers/test?provider=novita"

# Check MCP server status
curl http://localhost:8000/api/mcp/status

# In Claude/Cursor MCP, call:
# mcp_health() or test_llm_connection()`}
                                        />
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
