/**
 * CodeShield Logo - SVG Component
 * Neural tree branches within a shield shape
 */

import React from 'react';
import { motion } from 'framer-motion';

interface LogoProps {
    size?: number;
    animated?: boolean;
    showText?: boolean;
    className?: string;
}

// Static SVG for fast loading
export const CodeShieldLogoStatic: React.FC<{ size?: number; className?: string }> = ({
    size = 48,
    className = ''
}) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 100 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
    >
        <defs>
            <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ff6b35" />
                <stop offset="50%" stopColor="#f7931e" />
                <stop offset="100%" stopColor="#ff6b35" />
            </linearGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                </feMerge>
            </filter>
        </defs>

        {/* Shield outline */}
        <path
            d="M50 5 L90 20 L90 55 Q90 85 50 110 Q10 85 10 55 L10 20 Z"
            stroke="url(#shieldGradient)"
            strokeWidth="2.5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
        />

        {/* Center core */}
        <circle cx="50" cy="52" r="5" fill="#f7931e" filter="url(#glow)" />

        {/* Neural tree branches - radiating outward */}
        {/* Up */}
        <path d="M50 52 L50 28" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M50 28 L42 18" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M50 28 L58 18" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M42 18 L38 12" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M42 18 L46 12" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M58 18 L54 12" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M58 18 L62 12" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />

        {/* Upper right */}
        <path d="M50 52 L70 38" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M70 38 L80 32" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M70 38 L78 44" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M80 32 L85 28" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M78 44 L84 48" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />

        {/* Right */}
        <path d="M50 52 L75 52" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M75 52 L82 46" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M75 52 L82 58" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />

        {/* Lower right */}
        <path d="M50 52 L68 68" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M68 68 L76 74" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M68 68 L74 80" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M76 74 L80 78" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M74 80 L76 88" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />

        {/* Down */}
        <path d="M50 52 L50 78" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M50 78 L44 92" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M50 78 L56 92" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M44 92 L42 100" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M56 92 L58 100" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />

        {/* Lower left */}
        <path d="M50 52 L32 68" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M32 68 L24 74" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M32 68 L26 80" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M24 74 L20 78" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M26 80 L24 88" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />

        {/* Left */}
        <path d="M50 52 L25 52" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M25 52 L18 46" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M25 52 L18 58" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />

        {/* Upper left */}
        <path d="M50 52 L30 38" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M30 38 L20 32" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M30 38 L22 44" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" />
        <path d="M20 32 L15 28" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />
        <path d="M22 44 L16 48" stroke="#ff6b35" strokeWidth="1" strokeLinecap="round" />

        {/* Small nodes at key intersections */}
        <circle cx="50" cy="28" r="2" fill="#ff6b35" />
        <circle cx="70" cy="38" r="2" fill="#ff6b35" />
        <circle cx="75" cy="52" r="2" fill="#ff6b35" />
        <circle cx="68" cy="68" r="2" fill="#ff6b35" />
        <circle cx="50" cy="78" r="2" fill="#ff6b35" />
        <circle cx="32" cy="68" r="2" fill="#ff6b35" />
        <circle cx="25" cy="52" r="2" fill="#ff6b35" />
        <circle cx="30" cy="38" r="2" fill="#ff6b35" />
    </svg>
);

// Animated version with motion
export const CodeShieldLogoAnimated: React.FC<LogoProps> = ({
    size = 80,
    showText = false,
    className = ''
}) => {
    const branchVariants = {
        hidden: { pathLength: 0, opacity: 0 },
        visible: (i: number) => ({
            pathLength: 1,
            opacity: 1,
            transition: {
                pathLength: { type: "spring", duration: 1.5, bounce: 0, delay: i * 0.1 },
                opacity: { duration: 0.2, delay: i * 0.1 }
            }
        })
    };

    return (
        <div className={`flex flex-col items-center gap-4 ${className}`}>
            <motion.svg
                width={size}
                height={size * 1.2}
                viewBox="0 0 100 120"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                initial="hidden"
                animate="visible"
            >
                <defs>
                    <linearGradient id="shieldGradientAnim" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#ff6b35" />
                        <stop offset="50%" stopColor="#f7931e" />
                        <stop offset="100%" stopColor="#ff6b35" />
                    </linearGradient>
                    <filter id="glowAnim">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Shield outline */}
                <motion.path
                    d="M50 5 L90 20 L90 55 Q90 85 50 110 Q10 85 10 55 L10 20 Z"
                    stroke="url(#shieldGradientAnim)"
                    strokeWidth="2.5"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    variants={branchVariants}
                    custom={0}
                />

                {/* Center core with pulse */}
                <motion.circle
                    cx="50"
                    cy="52"
                    r="5"
                    fill="#f7931e"
                    filter="url(#glowAnim)"
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: 1
                    }}
                    transition={{
                        scale: { duration: 2, repeat: Infinity },
                        opacity: { duration: 0.5, delay: 0.5 }
                    }}
                />

                {/* Main branches - up */}
                <motion.path d="M50 52 L50 28" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={1} />
                <motion.path d="M50 28 L42 18" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" variants={branchVariants} custom={2} />
                <motion.path d="M50 28 L58 18" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" variants={branchVariants} custom={2} />

                {/* Right branches */}
                <motion.path d="M50 52 L70 38" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={3} />
                <motion.path d="M70 38 L80 32" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" variants={branchVariants} custom={4} />
                <motion.path d="M50 52 L75 52" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={5} />
                <motion.path d="M50 52 L68 68" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={6} />

                {/* Down branch */}
                <motion.path d="M50 52 L50 78" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={7} />
                <motion.path d="M50 78 L44 92" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" variants={branchVariants} custom={8} />
                <motion.path d="M50 78 L56 92" stroke="#ff6b35" strokeWidth="1.2" strokeLinecap="round" variants={branchVariants} custom={8} />

                {/* Left branches */}
                <motion.path d="M50 52 L32 68" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={9} />
                <motion.path d="M50 52 L25 52" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={10} />
                <motion.path d="M50 52 L30 38" stroke="#ff6b35" strokeWidth="1.5" strokeLinecap="round" variants={branchVariants} custom={11} />

                {/* Nodes */}
                {[
                    { cx: 50, cy: 28 }, { cx: 70, cy: 38 }, { cx: 75, cy: 52 }, { cx: 68, cy: 68 },
                    { cx: 50, cy: 78 }, { cx: 32, cy: 68 }, { cx: 25, cy: 52 }, { cx: 30, cy: 38 }
                ].map((node, i) => (
                    <motion.circle
                        key={i}
                        cx={node.cx}
                        cy={node.cy}
                        r="2"
                        fill="#ff6b35"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.5 + i * 0.1 }}
                    />
                ))}
            </motion.svg>

            {showText && (
                <motion.div
                    className="text-center"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.5 }}
                >
                    <div className="text-2xl font-light tracking-[0.3em] text-slate-200">CODESHIELD</div>
                    <div className="text-xs text-slate-500 tracking-widest mt-1">AI NEURAL PROTECTION</div>
                </motion.div>
            )}
        </div>
    );
};

// Default export
export const CodeShieldLogo = CodeShieldLogoStatic;
export default CodeShieldLogo;
