/**
 * ResultsPanel - Display verification results with issues and confidence
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// SVG Icons
const CheckCircleIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M8 12L11 15L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const XCircleIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M15 9L9 15M9 9L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
);

const AlertTriangleIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
        <path d="M12 9V13M12 17H12.01M10.29 3.86L1.82 18C1.64 18.3 1.55 18.64 1.55 19C1.55 19.35 1.65 19.69 1.82 19.99C2 20.3 2.25 20.55 2.55 20.73C2.86 20.91 3.21 21 3.56 21H20.44C20.79 21 21.13 20.91 21.44 20.73C21.74 20.55 21.99 20.3 22.17 19.99C22.34 19.69 22.44 19.35 22.44 19C22.44 18.64 22.35 18.3 22.17 18L13.7 3.86C13.53 3.56 13.28 3.31 12.97 3.14C12.67 2.96 12.33 2.87 11.99 2.87C11.65 2.87 11.31 2.96 11.01 3.14C10.71 3.31 10.46 3.56 10.29 3.86Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const CopyIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" strokeWidth="2" />
    </svg>
);

export interface Issue {
    type: 'error' | 'warning' | 'info';
    message: string;
    line?: number;
    fix?: string;
}

export interface VerificationResult {
    isValid: boolean;
    confidence: number;
    issues: Issue[];
    fixedCode?: string;
    executionResult?: {
        success: boolean;
        output: string;
        time_ms: number;
    };
}

interface ResultsPanelProps {
    result: VerificationResult | null;
    onApplyFix: (fixedCode: string) => void;
}

const IssueCard: React.FC<{ issue: Issue; index: number }> = ({ issue, index }) => {
    const colors = {
        error: { bg: 'bg-red-500/10', border: 'border-red-500/20', text: 'text-red-400', icon: <XCircleIcon /> },
        warning: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', icon: <AlertTriangleIcon /> },
        info: { bg: 'bg-cyan-500/10', border: 'border-cyan-500/20', text: 'text-cyan-400', icon: <CheckCircleIcon /> },
    };

    const style = colors[issue.type];

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className={`p-4 rounded-xl border ${style.bg} ${style.border}`}
        >
            <div className="flex items-start gap-3">
                <span className={style.text}>{style.icon}</span>
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        {issue.line && (
                            <span className="text-xs font-mono text-slate-500 bg-white/5 px-2 py-0.5 rounded">Line {issue.line}</span>
                        )}
                        <span className={`text-xs font-medium uppercase ${style.text}`}>{issue.type}</span>
                    </div>
                    <p className="text-sm text-slate-300">{issue.message}</p>
                    {issue.fix && (
                        <p className="mt-2 text-xs text-slate-400 font-mono bg-white/5 p-2 rounded-lg">
                            💡 <span className="text-emerald-400">{issue.fix}</span>
                        </p>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

const ConfidenceGauge: React.FC<{ value: number }> = ({ value }) => {
    const color = value >= 80 ? '#10b981' : value >= 50 ? '#f59e0b' : '#ef4444';
    const circumference = 2 * Math.PI * 45;
    const strokeDashoffset = circumference - (value / 100) * circumference;

    return (
        <div className="relative w-28 h-28">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                {/* Background circle */}
                <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#1e293b"
                    strokeWidth="6"
                />
                {/* Progress circle */}
                <motion.circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke={color}
                    strokeWidth="6"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <motion.span
                    className="text-2xl font-light"
                    style={{ color }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                >
                    {value}%
                </motion.span>
            </div>
        </div>
    );
};

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ result, onApplyFix }) => {
    const [copied, setCopied] = React.useState(false);

    if (!result) return null;

    const handleCopyFixed = () => {
        if (result.fixedCode) {
            navigator.clipboard.writeText(result.fixedCode);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-5xl mx-auto mt-10"
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <h2 className="text-xl font-semibold text-white">Results</h2>
                <div className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-full ${result.isValid
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                    {result.isValid ? <CheckCircleIcon /> : <XCircleIcon />}
                    {result.isValid ? 'Verified' : 'Issues Found'}
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Confidence Gauge */}
                <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm p-6 flex flex-col items-center justify-center">
                    <ConfidenceGauge value={result.confidence} />
                    <p className="mt-4 text-sm text-slate-400 text-center">
                        {result.confidence >= 80
                            ? 'Safe to use'
                            : result.confidence >= 50
                                ? 'Review recommended'
                                : 'Issues detected'}
                    </p>
                </div>

                {/* Issues List */}
                <div className="md:col-span-2 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm p-6">
                    <h3 className="text-sm font-medium text-slate-400 mb-4">
                        Issues ({result.issues.length})
                    </h3>

                    {result.issues.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-8 text-slate-600">
                            <CheckCircleIcon />
                            <p className="mt-2 text-xs">No issues detected</p>
                        </div>
                    ) : (
                        <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
                            <AnimatePresence>
                                {result.issues.map((issue, i) => (
                                    <IssueCard key={i} issue={issue} index={i} />
                                ))}
                            </AnimatePresence>
                        </div>
                    )}
                </div>
            </div>

            {/* Execution Result */}
            {result.executionResult && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="mt-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm p-6"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-medium text-slate-400">
                            Sandbox Execution
                        </h3>
                        <span className={`text-sm font-mono px-3 py-1 rounded-full ${result.executionResult.success 
                            ? 'text-emerald-400 bg-emerald-500/10' 
                            : 'text-red-400 bg-red-500/10'
                            }`}>
                            {result.executionResult.success ? '✓ Passed' : '✗ Failed'}
                            <span className="text-slate-500 ml-2">{result.executionResult.time_ms}ms</span>
                        </span>
                    </div>
                    <pre className="bg-black/30 p-4 text-sm font-mono text-slate-400 overflow-x-auto rounded-xl">
                        {result.executionResult.output || 'No output'}
                    </pre>
                </motion.div>
            )}

            {/* Fixed Code */}
            {result.fixedCode && result.fixedCode !== '' && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="mt-6 rounded-2xl bg-gradient-to-b from-emerald-500/10 to-emerald-500/5 border border-emerald-500/20 p-6"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-medium text-emerald-400">
                            ✨ Auto-Fixed Code
                        </h3>
                        <div className="flex gap-2">
                            <button
                                onClick={handleCopyFixed}
                                className="flex items-center gap-1 px-4 py-2 text-xs text-slate-400 hover:text-white border border-white/10 hover:border-white/20 transition-colors duration-300 rounded-lg"
                            >
                                <CopyIcon />
                                {copied ? 'Copied!' : 'Copy'}
                            </button>
                            <button
                                onClick={() => onApplyFix(result.fixedCode!)}
                                className="px-5 py-2 text-xs font-medium text-white bg-gradient-to-r from-emerald-500 to-cyan-500 hover:shadow-lg hover:shadow-emerald-500/25 transition-all duration-300 rounded-lg"
                            >
                                Apply Fix
                            </button>
                        </div>
                    </div>
                    <pre className="bg-black/30 p-4 text-sm font-mono text-emerald-300/80 overflow-x-auto max-h-64 rounded-xl">
                        {result.fixedCode}
                    </pre>
                </motion.div>
            )}
        </motion.div>
    );
};

export default ResultsPanel;
