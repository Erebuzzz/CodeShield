import React from 'react';
import { motion } from 'framer-motion';
import type { VerificationResult } from '../services/api';

// Icons
const CheckIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-brand-400">
    <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const AlertIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-amber-400">
    <path d="M12 9v4m0 4h.01M20.618 5.984A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const BugIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-red-400">
    <path d="M12 2a3 3 0 0 0-3 3v1h6V5a3 3 0 0 0-3-3z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M19 11h2m-2-3h2m-2 6h2M5 11H3m2-3H3m2 6H3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M5 18v1a2 2 0 0 0 2 2h2m10-3v1a2 2 0 0 1-2 2h-2m-8-5a6 6 0 1 1 12 0v2a6 6 0 1 1-12 0v-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const TerminalIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-slate-400">
    <path d="M4 17l6-6-6-6M12 19h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

interface ResultsPanelProps {
  result: VerificationResult | null;
  onApplyFix?: (fixedCode: string) => void;
}

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.05, duration: 0.3 }
  })
};

const ConfidenceScore: React.FC<{ score: number }> = ({ score }) => {
  const isHigh = score >= 90;
  const isMed = score >= 70 && score < 90;
  
  // Color calculation
  const colorClass = isHigh ? 'text-brand-400' : isMed ? 'text-amber-400' : 'text-red-400';
  
  return (
    <div className="flex items-center justify-between mb-8">
      <div>
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Trust Score</h3>
        <div className={`text-6xl font-light font-display tracking-tight mt-1 ${colorClass}`}>
          {score}%
        </div>
      </div>
      <div className="h-16 w-16 rounded-full border-4 border-slate-800 flex items-center justify-center relative">
         <svg className="absolute inset-0 transform -rotate-90 w-full h-full">
            <circle 
                cx="32" cy="32" r="28" 
                stroke="currentColor" 
                strokeWidth="4" 
                className="text-slate-800" 
                fill="none" 
            />
            <motion.circle 
                initial={{ pathLength: 0 }}
                animate={{ pathLength: score / 100 }}
                transition={{ duration: 1, ease: "easeOut" }}
                cx="32" cy="32" r="28" 
                stroke="currentColor" 
                strokeWidth="4" 
                className={colorClass} 
                fill="none"
                style={{ strokeLinecap: 'round' }}
            />
         </svg>
      </div>
    </div>
  );
};

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ result, onApplyFix }) => {
  if (!result) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-500 border border-slate-800/50 rounded-2xl bg-slate-900/20 backdrop-blur-sm">
        <motion.div 
            animate={{ opacity: [0.5, 1, 0.5] }} 
            transition={{ duration: 2, repeat: Infinity }}
            className="mb-4"
        >
            <div className="w-12 h-12 rounded-xl bg-slate-800/50 flex items-center justify-center">
                <TerminalIcon />
            </div>
        </motion.div>
        <p className="font-light">Ready to analyze</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-900/30 backdrop-blur-md rounded-2xl border border-white/5 overflow-hidden">
        {/* Header Section */}
        <div className="p-6 border-b border-white/5 bg-white/[0.02]">
            <ConfidenceScore score={result.confidence} />
            
            <div className="flex gap-4 text-xs font-medium">
                <div className="px-3 py-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/10">
                    {result.issues.filter(i => i.type === 'error').length} Errors
                </div>
                <div className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/10">
                    {result.issues.filter(i => i.type === 'warning').length} Warnings
                </div>
            </div>
        </div>

        {/* Scrollable List */}
        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            <div className="space-y-1">
                {result.issues.length === 0 ? (
                    <motion.div 
                        initial={{ opacity: 0 }} 
                        animate={{ opacity: 1 }}
                        className="flex flex-col items-center justify-center py-12 text-center"
                    >
                        <div className="w-12 h-12 rounded-full bg-brand-500/20 text-brand-400 flex items-center justify-center mb-4">
                            <CheckIcon />
                        </div>
                        <h4 className="text-white font-medium">Perfect Code</h4>
                        <p className="text-sm text-slate-500 mt-1">No security or style issues found.</p>
                    </motion.div>
                ) : (
                    result.issues.map((issue, idx) => (
                        <motion.div
                            key={idx}
                            custom={idx}
                            variants={itemVariants}
                            initial="hidden"
                            animate="visible"
                            className="group p-4 hover:bg-white/5 rounded-xl transition-colors border border-transparent hover:border-white/5"
                        >
                            <div className="flex gap-4">
                                <div className="mt-0.5 shrink-0">
                                    {issue.type === 'error' && <BugIcon />}
                                    {issue.type === 'warning' && <AlertIcon />}
                                    {issue.type === 'info' && <div className="w-4 h-4 rounded-full border-2 border-brand-500/50" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-start">
                                        <p className="text-sm text-slate-200 font-medium leading-relaxed">
                                            {issue.message}
                                        </p>
                                        {issue.line && (
                                            <span className="text-[10px] font-mono text-slate-500 bg-slate-800/50 px-1.5 py-0.5 rounded ml-2 whitespace-nowrap">
                                                L{issue.line}
                                            </span>
                                        )}
                                    </div>
                                    
                                    {/* Fix Suggestion */}
                                    {issue.fix && (
                                        <div className="mt-3 pl-4 border-l-2 border-slate-700/50">
                                            <div className="text-xs text-slate-500 mb-1.5 uppercase tracking-wide font-semibold">Suggested Fix</div>
                                            <div className="bg-black/30 rounded-lg p-3 font-mono text-xs text-emerald-400 overflow-x-auto">
                                                {issue.fix}
                                            </div>
                                            {onApplyFix && (
                                                <button 
                                                    onClick={() => onApplyFix(issue.fix!)}
                                                    className="mt-2 text-xs text-slate-400 hover:text-white hover:underline decoration-brand-500/50 underline-offset-4 transition-all"
                                                >
                                                    Apply this fix
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>

            {/* Execution Output (if available) */}
            {result.executionResult && (
                <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-6 pt-6 border-t border-white/5"
                >
                    <div className="flex items-center gap-2 mb-3">
                        <TerminalIcon />
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Runtime Output</span>
                    </div>
                    <div className="bg-black/40 rounded-xl p-4 font-mono text-sm text-slate-300 border border-white/5">
                        {result.executionResult.output || <span className="text-slate-600 italic">No output</span>}
                    </div>
                </motion.div>
            )}
        </div>
    </div>
  );
};
