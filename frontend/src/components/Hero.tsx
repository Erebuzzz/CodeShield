/**
 * Hero - Clean, Professional Landing
 * Style: Soft colors, Inter font, minimal icons
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Logo } from './Logo';

interface HeroProps {
  onGetStarted: () => void;
  onViewDocs: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onGetStarted, onViewDocs }) => {
  return (
    <div className="min-h-screen flex flex-col relative">
      {/* Navigation */}
      <nav className="w-full px-6 md:px-12 py-5 relative z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Logo size="md" />
          
          <div className="flex items-center gap-8">
            <button 
              onClick={onViewDocs}
              className="text-sm text-slate-400 hover:text-white transition-colors duration-200"
            >
              Docs
            </button>
            <a 
              href="https://github.com/Erebuzzz/CodeShield" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-slate-400 hover:text-white transition-colors duration-200 flex items-center gap-1.5"
            >
              <GitHubIcon />
              GitHub
            </a>
            <button
              onClick={onGetStarted}
              className="px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-lg text-sm font-medium hover:bg-emerald-500/20 transition-colors duration-200"
            >
              Try Demo
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-6 md:px-12 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700/50 mb-8"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span className="text-xs text-slate-300">MCP Protocol Compatible</span>
          </motion.div>

          {/* Headline */}
          <motion.h1 
            className="text-4xl md:text-6xl font-semibold tracking-tight text-white mb-5 leading-[1.1]"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            Trust your{' '}
            <span className="text-emerald-400">AI-generated</span>
            {' '}code
          </motion.h1>

          {/* Subheadline */}
          <motion.p 
            className="text-base md:text-lg text-slate-400 max-w-xl mx-auto mb-10 leading-relaxed"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
          >
            Verify, enforce conventions, and preserve context across your AI coding sessions.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="flex items-center justify-center gap-3 mb-16"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <button
              onClick={onGetStarted}
              className="group px-6 py-3 bg-emerald-500 rounded-lg text-white text-sm font-medium hover:bg-emerald-600 transition-colors duration-200"
            >
              <span className="flex items-center gap-2">
                Get Started
                <ArrowRightIcon />
              </span>
            </button>
            <button
              onClick={onViewDocs}
              className="px-6 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white text-sm font-medium hover:bg-slate-800 transition-colors duration-200"
            >
              Documentation
            </button>
          </motion.div>

          {/* Feature Cards - Larger with more padding */}
          <motion.div 
            className="grid md:grid-cols-3 gap-4"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <FeatureCard 
              icon={<ShieldCheckIcon />}
              title="TrustGate"
              description="Verification before acceptance. Catches missing imports, syntax errors, and runtime issues."
            />
            <FeatureCard 
              icon={<SparklesIcon />}
              title="StyleForge"
              description="Convention enforcement. Ensures AI code matches your codebase naming patterns."
            />
            <FeatureCard 
              icon={<FolderIcon />}
              title="ContextVault"
              description="Context memory save/restore. Resume exactly where you left off with AI briefings."
            />
          </motion.div>
        </div>
      </main>
    </div>
  );
};

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description }) => {
  return (
    <div className="p-6 rounded-xl bg-slate-800/30 border border-slate-700/40 text-left hover:border-slate-600/50 transition-colors duration-200">
      <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center mb-4 text-emerald-400">
        {icon}
      </div>
      <h3 className="text-base font-medium text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
};

// Simple, clean icons
const GitHubIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
  </svg>
);

const ArrowRightIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-0.5 transition-transform">
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </svg>
);

const ShieldCheckIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
    <path d="M9 12l2 2 4-4"/>
  </svg>
);

const SparklesIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"/>
    <circle cx="12" cy="12" r="4"/>
  </svg>
);

const FolderIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2v11z"/>
  </svg>
);

export default Hero;
