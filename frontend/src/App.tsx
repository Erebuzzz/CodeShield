import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ReactiveCodeGraph } from './components/ReactiveCodeGraph';
import { Hero } from './components/Hero';
import { Logo } from './components/Logo';
import Docs from './components/Docs';

// Lazy load heavy components
const CodeEditor = React.lazy(() => import('./components/CodeEditor').then(m => ({ default: m.CodeEditor })));
const ResultsPanel = React.lazy(() => import('./components/ResultsPanel').then(m => ({ default: m.ResultsPanel })));

import type { VerificationResult } from './services/api';

function App() {
  const [mode, setMode] = useState<'hero' | 'demo' | 'docs'>('hero');
  const [code, setCode] = useState(`def calculate_total(items):
    return sum(item.price for item in items)`);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);

  const handleStartDemo = () => setMode('demo');
  const handleShowDocs = () => setMode('docs');
  const handleBackToHome = () => setMode('hero');

  return (
    <div className="relative w-full min-h-screen overflow-hidden selection:bg-brand-500 selection:text-white bg-dark-bg font-sans">
      {/* Background Layer */}
      <div className="fixed inset-0 z-0">
        <ReactiveCodeGraph mode={mode === 'hero' ? 'ambient' : 'reactive'} code={code} />
        {/* Vignette Overlay (OceanX style depth) */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_0%,_#030305_90%)] opacity-90 pointer-events-none" />
      </div>

      {/* Navbar */}
      {mode !== 'docs' && (
        <nav className="relative z-50 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
          <div onClick={handleBackToHome} className="cursor-pointer hover:opacity-80 transition-opacity">
            <Logo size="sm" />
          </div>
          <div className="hidden md:flex items-center gap-8">
            <button onClick={handleShowDocs} className="text-sm text-slate-400 hover:text-white transition-colors font-medium">
              Documentation
            </button>
            <a href="https://github.com/Erebuzzz/CodeShield" target="_blank" rel="noopener" className="text-sm text-slate-400 hover:text-white transition-colors font-medium">
              GitHub
            </a>
          </div>
        </nav>
      )}

      {/* Main Content */}
      <main className="relative z-10 w-full max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          {mode === 'hero' && (
            <Hero key="hero" onStart={handleStartDemo} />
          )}

          {mode === 'demo' && (
            <div key="demo" className="p-6 md:p-12 min-h-[85vh] flex flex-col items-center">
               <h2 className="text-3xl font-display font-light mb-8 text-white tracking-tight">
                  <span className="text-brand-400">TrustGate</span> Verification
               </h2>
               <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                  <React.Suspense fallback={<div className="text-white text-center py-10">Loading Editor...</div>}>
                    <div className="h-[600px]">
                        <CodeEditor 
                          code={code} 
                          onChange={setCode} 
                          onVerify={(res) => { setVerificationResult(res); }}
                        />
                    </div>
                  </React.Suspense>
                  
                  <React.Suspense fallback={<div className="text-white text-center py-10">Loading Results...</div>}>
                    <div className="h-[600px] flex flex-col">
                        <ResultsPanel result={verificationResult} />
                    </div>
                  </React.Suspense>
               </div>
            </div>
          )}

          {mode === 'docs' && (
            <Docs key="docs" onBack={handleBackToHome} />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
