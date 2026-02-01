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

// Simple syntax highlighter
const highlightSyntax = (code: string): string => {
    // This is a basic highlighter, you could use a library like Prism.js for better results
    return code
        .replace(/(def |class |import |from |return |if |else |elif |for |while |try |except |finally |with |as |in |not |and |or |True|False|None)/g, '<span class="text-purple-400">$1</span>')
        .replace(/(["'])(.*?)\1/g, '<span class="text-green-400">$1$2$1</span>')
        .replace(/(#.*$)/gm, '<span class="text-slate-500">$1</span>')
        .replace(/\b(\d+)\b/g, '<span class="text-orange-400">$1</span>');
};

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
            className="w-full max-w-4xl mx-auto"
        >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#1a1a24] border border-b-0 border-slate-800 rounded-t-lg">
                <div className="flex items-center gap-2">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-green-500/80" />
                    </div>
                    <span className="ml-3 text-sm text-slate-500 font-mono">paste_code.py</span>
                </div>

                <button
                    onClick={handleCopy}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs text-slate-400 hover:text-white transition-colors"
                >
                    <CopyIcon />
                    {copied ? 'Copied!' : 'Copy'}
                </button>
            </div>

            {/* Editor */}
            <div className="relative bg-[#12121a] border border-slate-800 rounded-b-lg overflow-hidden">
                <div className="flex">
                    {/* Line Numbers */}
                    <div className="flex-shrink-0 py-4 px-3 bg-[#0d0d14] border-r border-slate-800/50 select-none">
                        {Array.from({ length: Math.max(lineCount, 10) }, (_, i) => (
                            <div key={i} className="text-xs text-slate-600 font-mono text-right leading-6">
                                {i + 1}
                            </div>
                        ))}
                    </div>

                    {/* Code Area */}
                    <textarea
                        value={code}
                        onChange={(e) => onCodeChange(e.target.value)}
                        placeholder="# Paste your AI-generated Python code here...&#10;&#10;def example():&#10;    pass"
                        className="flex-1 min-h-[300px] p-4 bg-transparent text-slate-200 font-mono text-sm leading-6 resize-none focus:outline-none"
                        style={{ caretColor: '#22c55e' }}
                        spellCheck={false}
                    />
                </div>

                {/* Processing Overlay */}
                {isProcessing && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center"
                    >
                        <div className="flex flex-col items-center gap-4">
                            <div className="w-12 h-12 border-4 border-slate-700 border-t-green-500 rounded-full animate-spin" />
                            <span className="text-sm text-slate-400 font-mono">Analyzing code...</span>
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 mt-4 justify-center">
                <motion.button
                    onClick={onVerify}
                    disabled={isProcessing || !code.trim()}
                    className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium rounded-lg transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <VerifyIcon />
                    Verify Code
                </motion.button>

                <motion.button
                    onClick={onCheckStyle}
                    disabled={isProcessing || !code.trim()}
                    className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium rounded-lg transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <StyleIcon />
                    Check Style
                </motion.button>

                <motion.button
                    onClick={onAutoFix}
                    disabled={isProcessing || !code.trim()}
                    className="flex items-center gap-2 px-6 py-3 bg-amber-600 hover:bg-amber-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium rounded-lg transition-colors"
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
