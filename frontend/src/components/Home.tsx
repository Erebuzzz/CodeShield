import React, { Suspense } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Hero } from './Hero';
import type { VerificationResult } from '../services/api';

// Lazy load heavy components
const CodeEditor = React.lazy(() => import('./CodeEditor').then(m => ({ default: m.CodeEditor })));
const ResultsPanel = React.lazy(() => import('./ResultsPanel').then(m => ({ default: m.ResultsPanel })));

interface HomeProps {
  mode: 'hero' | 'demo';
  setMode: (mode: 'hero' | 'demo') => void;
  code: string;
  setCode: (code: string) => void;
  verificationResult: VerificationResult | null;
  setVerificationResult: (result: VerificationResult | null) => void;
}

export const Home: React.FC<HomeProps> = ({
  mode,
  setMode,
  code,
  setCode,
  verificationResult,
  setVerificationResult
}) => {
  return (
    <AnimatePresence mode="wait">
      {mode === 'hero' && (
        <Hero key="hero" onStart={() => setMode('demo')} />
      )}

      {mode === 'demo' && (
        <div key="demo" className="p-6 md:p-12 min-h-[85vh] flex flex-col items-center">
           <h2 className="text-3xl font-display font-light mb-8 text-white tracking-tight">
              <span className="text-brand-400">TrustGate</span> Verification
           </h2>
           <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
              <Suspense fallback={<div className="text-white text-center py-10">Loading Editor...</div>}>
                <div className="h-[600px]">
                    <CodeEditor 
                      code={code} 
                      onChange={setCode} 
                      onVerify={(res) => { setVerificationResult(res); }}
                    />
                </div>
              </Suspense>
              
              <Suspense fallback={<div className="text-white text-center py-10">Loading Results...</div>}>
                <div className="h-[600px] flex flex-col">
                    <ResultsPanel result={verificationResult} />
                </div>
              </Suspense>
           </div>
        </div>
      )}
    </AnimatePresence>
  );
};
