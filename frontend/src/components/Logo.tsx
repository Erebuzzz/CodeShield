/**
 * CodeShield Logo - Shield with Code Tree/Graph Inside
 * Represents context and code verification
 */

import React from 'react';
import { motion } from 'framer-motion';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

export const Logo: React.FC<LogoProps> = ({ 
  size = 'md', 
  showText = true,
  className = '' 
}) => {
  const sizes = {
    sm: { icon: 28, text: 'text-base', gap: 'gap-2' },
    md: { icon: 36, text: 'text-lg', gap: 'gap-2.5' },
    lg: { icon: 48, text: 'text-2xl', gap: 'gap-3' },
  };

  const { icon, text, gap } = sizes[size];

  return (
    <motion.div 
      className={`flex items-center ${gap} ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Shield Icon with Code Tree Inside */}
      <svg 
        width={icon} 
        height={icon} 
        viewBox="0 0 40 40" 
        fill="none"
        className="flex-shrink-0"
      >
        <defs>
          <linearGradient id="shieldStroke" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#34d399" />
            <stop offset="100%" stopColor="#5eead4" />
          </linearGradient>
          <linearGradient id="shieldBg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#34d399" stopOpacity="0.08" />
            <stop offset="100%" stopColor="#5eead4" stopOpacity="0.03" />
          </linearGradient>
          <linearGradient id="treeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#34d399" />
            <stop offset="100%" stopColor="#5eead4" />
          </linearGradient>
        </defs>
        
        {/* Shield Outline */}
        <path 
          d="M20 3L5 9.5V18C5 27.5 11.5 35.5 20 37C28.5 35.5 35 27.5 35 18V9.5L20 3Z" 
          fill="url(#shieldBg)"
          stroke="url(#shieldStroke)"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Code Tree/Graph Structure Inside */}
        {/* Root node */}
        <circle cx="20" cy="12" r="2.5" fill="url(#treeGradient)" />
        
        {/* Trunk line */}
        <path 
          d="M20 14.5V18" 
          stroke="url(#treeGradient)" 
          strokeWidth="1.5" 
          strokeLinecap="round"
        />
        
        {/* Branch lines */}
        <path 
          d="M20 18L13 24M20 18L27 24M20 18V28" 
          stroke="url(#treeGradient)" 
          strokeWidth="1.5" 
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Leaf nodes */}
        <circle cx="13" cy="25" r="2" fill="url(#treeGradient)" />
        <circle cx="20" cy="29" r="2" fill="url(#treeGradient)" />
        <circle cx="27" cy="25" r="2" fill="url(#treeGradient)" />
      </svg>

      {showText && (
        <span className={`font-medium tracking-tight ${text}`}>
          <span className="text-white">Code</span>
          <span className="text-emerald-400">Shield</span>
        </span>
      )}
    </motion.div>
  );
};

export default Logo;
