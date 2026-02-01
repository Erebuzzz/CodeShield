import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { verifyCode, type VerificationResult } from '../services/api';

// Icons
const PlayIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-white hover:text-white/80 transition-colors">
    <path d="M5 3l14 9-14 9V3z" fill="currentColor" />
  </svg>
);

const LoaderIcon = () => (
  <svg className="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  onVerify: (result: VerificationResult) => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ code, onChange, onVerify }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  
  const handleVerify = async () => {
    setIsProcessing(true);
    try {
      const result = await verifyCode(code);
      onVerify(result);
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const lineCount = code.split('\n').length;

  return (
    <div className="h-full flex flex-col bg-slate-900/30 backdrop-blur-md rounded-2xl border border-white/5 overflow-hidden shadow-2xl shadow-indigo-500/10">
      {/* Search Bar / Header */}
      <div className="bg-white/[0.03] border-b border-white/5 px-4 py-3 flex items-center justify-between">
        <div className="flex gap-2 items-center">
            <div className="flex gap-1.5 mr-4">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
            </div>
            <span className="text-xs font-mono text-slate-500">script.py</span>
        </div>
        <div>
           {/* Maybe some mock status indicators? */}
        </div>
      </div>

      {/* Editor Area */}
      <div className="relative flex-1 flex overflow-hidden group">
        {/* Line Numbers */}
        <div className="w-12 bg-white/[0.01] border-r border-white/5 pt-4 text-right pr-3 select-none text-slate-700 font-mono text-xs leading-6">
          {Array.from({ length: Math.max(lineCount, 20) }).map((_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>

        {/* Textarea */}
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 bg-transparent text-slate-300 font-mono text-xs leading-6 p-4 resize-none focus:outline-none focus:ring-0 custom-scrollbar whitespace-pre"
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
        />
        
        {/* Floating Run Button */}
        <div className="absolute bottom-6 right-6">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleVerify}
                disabled={isProcessing}
                className={`
                    h-14 px-6 rounded-full flex items-center gap-3 font-medium transition-all shadow-lg shadow-brand-500/25
                    ${isProcessing 
                        ? 'bg-slate-700 cursor-wait text-slate-400' 
                        : 'bg-gradient-to-r from-brand-500 to-violet-600 text-white hover:shadow-brand-500/40'
                    }
                `}
            >
                {isProcessing ? (
                    <>
                        <LoaderIcon />
                        <span>Analyzing...</span>
                    </>
                ) : (
                    <>
                        <PlayIcon />
                        <span>Run Verification</span>
                    </>
                )}
            </motion.button>
        </div>
      </div>
    </div>
  );
};
