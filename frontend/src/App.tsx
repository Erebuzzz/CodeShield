/**
 * CodeShield - AI Code Verification Frontend
 */

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import { ReactiveCodeGraph } from './components/ReactiveCodeGraph';
import { Hero } from './components/Hero';
import { CodeEditor } from './components/CodeEditor';
import { ResultsPanel, VerificationResult } from './components/ResultsPanel';

// API
import { verifyCode, checkStyle, fullVerify } from './services/api';

type AppView = 'hero' | 'demo';

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
      // Convert style result to verification format
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
    <div className="min-h-screen bg-[#0a0a0f] text-white relative overflow-hidden">
      {/* Animated Background */}
      <ReactiveCodeGraph isProcessing={isProcessing} />

      {/* Gradient Overlays */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-[150px]" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[150px]" />
      </div>

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
              <Hero onGetStarted={handleGetStarted} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Demo Section */}
        {view === 'demo' && (
          <motion.div
            ref={demoRef}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="min-h-screen py-20 px-6"
          >
            {/* Header */}
            <div className="max-w-4xl mx-auto mb-12 text-center">
              <button
                onClick={() => setView('hero')}
                className="text-sm text-slate-500 hover:text-white transition-colors mb-6 flex items-center gap-2 mx-auto"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Back to Home
              </button>

              <h1 className="text-4xl font-bold mb-4">
                <span className="gradient-text">Verify</span> Your Code
              </h1>
              <p className="text-slate-400 max-w-xl mx-auto">
                Paste your AI-generated Python code below. CodeShield will analyze it for errors,
                missing imports, style issues, and optionally run it in a sandbox.
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

            {/* Footer */}
            <footer className="mt-20 text-center text-sm text-slate-600">
              <p>
                Built with ❤️ for AI Vibe Coding Hackathon 2026
              </p>
              <p className="mt-2 text-xs text-slate-700">
                Powered by Daytona • CometAPI • LeanMCP
              </p>
            </footer>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default App;
