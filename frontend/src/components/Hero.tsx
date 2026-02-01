/**
 * Hero Section - Landing page with animated background
 */

import React from 'react';
import { motion } from 'framer-motion';
import { CodeShieldLogoStatic } from './Logo';

const VerifyIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M8 12L11 15L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const StyleIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const MemoryIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M9 9H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M9 12H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M9 15H12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
);

interface FeaturePillProps {
    icon: React.ReactNode;
    title: string;
    color: string;
    delay: number;
}

const FeaturePill: React.FC<FeaturePillProps> = ({ icon, title, color, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay }}
        className="flex items-center gap-3 px-5 py-3 rounded-full border backdrop-blur-sm"
        style={{
            borderColor: `${color}40`,
            backgroundColor: `${color}10`,
        }}
    >
        <span style={{ color }}>{icon}</span>
        <span className="text-sm font-medium" style={{ color }}>{title}</span>
    </motion.div>
);

interface HeroProps {
    onGetStarted: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onGetStarted }) => {
    return (
        <section className="relative min-h-screen flex flex-col items-center justify-center px-6 py-20">
            {/* Content */}
            <div className="relative z-10 max-w-4xl mx-auto text-center">
                {/* Badge */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full border border-green-500/30 bg-green-500/10"
                >
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-xs font-mono text-green-500 uppercase tracking-wider">
                        AI Vibe Coding Hackathon 2026
                    </span>
                </motion.div>

                {/* Logo */}
                <motion.div
                    className="flex justify-center mb-6"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.1 }}
                >
                    <CodeShieldLogoStatic size={120} />
                </motion.div>

                {/* Title */}
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="text-6xl md:text-8xl font-bold tracking-tight mb-4"
                >
                    <span className="gradient-text">Code</span>
                    <span className="text-white">Shield</span>
                </motion.h1>

                {/* Tagline */}
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="text-xl md:text-2xl text-slate-400 mb-4"
                >
                    AI Code That Actually Works
                </motion.p>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="text-base text-slate-500 max-w-2xl mx-auto mb-10"
                >
                    Verify, fix, and enforce conventions on AI-generated code before it breaks your build.
                    Powered by LLM analysis and sandboxed execution.
                </motion.p>

                {/* Feature Pills */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    className="flex flex-wrap justify-center gap-4 mb-12"
                >
                    <FeaturePill
                        icon={<VerifyIcon />}
                        title="TrustGate"
                        color="#22c55e"
                        delay={0.6}
                    />
                    <FeaturePill
                        icon={<StyleIcon />}
                        title="StyleForge"
                        color="#3b82f6"
                        delay={0.7}
                    />
                    <FeaturePill
                        icon={<MemoryIcon />}
                        title="ContextVault"
                        color="#f59e0b"
                        delay={0.8}
                    />
                </motion.div>

                {/* CTA Button */}
                <motion.button
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.9 }}
                    onClick={onGetStarted}
                    className="group relative px-8 py-4 rounded-lg font-semibold text-lg overflow-hidden"
                    style={{
                        background: 'linear-gradient(135deg, #22c55e 0%, #06b6d4 100%)',
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <span className="relative z-10 text-white flex items-center gap-2">
                        Try Demo
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                            <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </span>
                    <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity" />
                </motion.button>

                {/* Scroll indicator */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.2 }}
                    className="absolute bottom-8 left-1/2 -translate-x-1/2"
                >
                    <motion.div
                        animate={{ y: [0, 8, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="w-6 h-10 rounded-full border-2 border-slate-600 flex items-start justify-center p-2"
                    >
                        <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                    </motion.div>
                </motion.div>
            </div>
        </section>
    );
};

export default Hero;
