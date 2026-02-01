/**
 * CodeShield - AI Code Verification Frontend
 */

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import { ReactiveCodeGraph } from './components/ReactiveCodeGraph';
import { Hero } from './components/Hero';
import { CodeEditor } from './components/CodeEditor';
import { ResultsPanel } from './components/ResultsPanel';
import { Docs } from './components/Docs';
import { Logo } from './components/Logo';
import type { VerificationResult } from './components/ResultsPanel';

// API
import { verifyCode, checkStyle, fullVerify } from './services/api';

type AppView = 'hero' | 'demo' | 'docs';

const App: React.FC = () => {
  const [view, setView] = useState<AppView>('hero');
  const [code, setCode] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const demoRef = useRef<HTMLDivElement>(null);

  const handleGetStarted = () => {
    setView('demo');
    setTimeout(() => {
      demoRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleViewDocs = () => {
    setView('docs');
  };

  const handleVerify = async () => {
    if (!code.trim()) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const verificationResult = await verifyCode(code, true);
      setResult(verificationResult);
    } catch (error) {
      console.error('Verification failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCheckStyle = async () => {
    if (!code.trim()) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const styleResult = await checkStyle(code);
      setResult({
        isValid: styleResult.matches_convention,
        confidence: styleResult.matches_convention ? 100 : 70,
        issues: styleResult.suggestions.map(s => ({
          type: 'warning' as const,
          message: s,
        })),
      });
    } catch (error) {
      console.error('Style check failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAutoFix = async () => {
    if (!code.trim()) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const verificationResult = await fullVerify(code);
      setResult(verificationResult);
    } catch (error) {
      console.error('Auto-fix failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleApplyFix = (fixedCode: string) => {
    setCode(fixedCode);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-[#030305] text-white relative overflow-hidden">
      {/* Animated AST Background */}
      <ReactiveCodeGraph isProcessing={isProcessing} mcpConnected={true} />

      {/* Main Content */}
      <div className="relative z-10">
        <AnimatePresence mode="wait">
          {view === 'hero' && (
            <motion.div
              key="hero"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.5 }}
            >
              <Hero onGetStarted={handleGetStarted} onViewDocs={handleViewDocs} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Docs Section */}
        {view === 'docs' && (
          <Docs onBack={() => setView('hero')} />
        )}

        {/* Demo Section */}
        {view === 'demo' && (
          <motion.div
            ref={demoRef}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="min-h-screen py-8 px-6 md:px-12"
          >
            {/* Nav */}
            <div className="max-w-5xl mx-auto mb-10 flex items-center justify-between">
              <Logo size="sm" />
              <div className="flex items-center gap-4">
                <a
                  href="https://github.com/Erebuzzz/CodeShield"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                  </svg>
                  GitHub
                </a>
                <button
                  onClick={() => setView('hero')}
                  className="text-sm text-slate-400 hover:text-white transition-colors flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/50 border border-slate-700/50"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  Back
                </button>
              </div>
            </div>

            {/* Header */}
            <div className="max-w-5xl mx-auto mb-10 text-center">
              <h1 className="text-3xl font-semibold tracking-tight mb-3 text-white">
                Verify Your{' '}
                <span className="text-emerald-400">Code</span>
              </h1>
              <p className="text-slate-400 text-sm max-w-md mx-auto">
                Paste your Python code below. We'll analyze it for errors, missing imports, and style issues.
              </p>
            </div>

            {/* Code Editor */}
            <CodeEditor
              code={code}
              onCodeChange={setCode}
              onVerify={handleVerify}
              onCheckStyle={handleCheckStyle}
              onAutoFix={handleAutoFix}
              isProcessing={isProcessing}
            />

            {/* Results */}
            <ResultsPanel
              result={result}
              onApplyFix={handleApplyFix}
            />
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default App;
