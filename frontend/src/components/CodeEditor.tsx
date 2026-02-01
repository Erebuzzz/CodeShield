/**
 * CodeEditor - Code input panel with syntax highlighting
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';

// SVG Icons
const VerifyIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M8 12L11 15L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const StyleIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const FixIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const CopyIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" strokeWidth="2" />
    </svg>
);

interface CodeEditorProps {
    code: string;
    onCodeChange: (code: string) => void;
    onVerify: () => void;
    onCheckStyle: () => void;
    onAutoFix: () => void;
    isProcessing: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
    code,
    onCodeChange,
    onVerify,
    onCheckStyle,
    onAutoFix,
    isProcessing,
}) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const lineCount = code.split('\n').length;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-5xl mx-auto"
        >
            {/* Editor Container */}
            <div className="rounded-2xl overflow-hidden border border-white/10 bg-[#0a0a10]/80 backdrop-blur-sm">
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-3 border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="flex gap-1.5">
                            <div className="w-3 h-3 rounded-full bg-red-500/80" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                            <div className="w-3 h-3 rounded-full bg-green-500/80" />
                        </div>
                        <span className="text-xs text-slate-500 font-mono">input.py</span>
                    </div>

                    <button
                        onClick={handleCopy}
                        className="flex items-center gap-2 px-3 py-1.5 text-xs text-slate-500 hover:text-emerald-400 transition-colors duration-300 rounded-lg hover:bg-white/5"
                    >
                        <CopyIcon />
                        {copied ? 'Copied!' : 'Copy'}
                    </button>
                </div>

                {/* Editor */}
                <div className="relative">
                    <div className="flex">
                        {/* Line Numbers */}
                        <div className="flex-shrink-0 py-4 px-4 bg-white/[0.02] border-r border-white/5 select-none">
                            {Array.from({ length: Math.max(lineCount, 12) }, (_, i) => (
                                <div key={i} className="text-xs text-slate-700 font-mono text-right leading-6">
                                    {i + 1}
                                </div>
                            ))}
                        </div>

                        {/* Code Area */}
                        <textarea
                            value={code}
                            onChange={(e) => onCodeChange(e.target.value)}
                            placeholder="# Paste your Python code here..."
                            className="flex-1 min-h-[320px] p-4 bg-transparent text-slate-300 font-mono text-sm leading-6 resize-none focus:outline-none placeholder:text-slate-600"
                            style={{ caretColor: '#10b981' }}
                            spellCheck={false}
                        />
                    </div>

                    {/* Processing Overlay */}
                    {isProcessing && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center rounded-b-2xl"
                        >
                            <div className="flex flex-col items-center gap-4">
                                <div className="w-10 h-10 border-2 border-slate-700 border-t-emerald-500 rounded-full animate-spin" />
                                <span className="text-sm text-slate-400">Analyzing code...</span>
                            </div>
                        </motion.div>
                    )}
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 mt-6 justify-center">
                <motion.button
                    onClick={onVerify}
                    disabled={isProcessing || !code.trim()}
                    className="flex items-center gap-2 px-8 py-3.5 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:shadow-lg hover:shadow-emerald-500/25 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-600 text-white text-sm font-medium transition-all duration-300 rounded-xl"
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <VerifyIcon />
                    Verify Code
                </motion.button>

                <motion.button
                    onClick={onCheckStyle}
                    disabled={isProcessing || !code.trim()}
                    className="flex items-center gap-2 px-8 py-3.5 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-emerald-500/50 disabled:bg-transparent disabled:border-white/5 disabled:text-slate-600 text-white text-sm font-medium transition-all duration-300 rounded-xl backdrop-blur-sm"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <StyleIcon />
                    Check Style
                </motion.button>

                <motion.button
                    onClick={onAutoFix}
                    disabled={isProcessing || !code.trim()}
                    className="flex items-center gap-2 px-8 py-3.5 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-500/50 disabled:bg-transparent disabled:border-white/5 disabled:text-slate-600 text-white text-sm font-medium transition-all duration-300 rounded-xl backdrop-blur-sm"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <FixIcon />
                    Auto-Fix
                </motion.button>
            </div>
        </motion.div>
    );
};

export default CodeEditor;
