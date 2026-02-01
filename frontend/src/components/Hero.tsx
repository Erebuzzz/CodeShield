import React from 'react';
import { motion } from 'framer-motion';

interface HeroProps {
    onStart: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onStart }) => {
    return (
        <div className='relative z-10 flex flex-col items-center justify-center min-h-[85vh] text-center px-6'>
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className='max-w-5xl mx-auto space-y-8'
            >
                <h1 className='font-display font-light text-6xl md:text-8xl tracking-tight leading-[1.1] text-white'>
                    Verify code <br />
                    <span className='text-transparent bg-clip-text bg-gradient-to-r from-brand-300 to-brand-500'>
                        before it breaks
                    </span>
                </h1>

                <p className='text-xl md:text-2xl text-slate-400 max-w-2xl mx-auto font-sans font-light leading-relaxed'>
                    The complete safety net for AI coding. <br className='hidden md:block' />
                    Verify logic, enforce style, and preserve context.
                </p>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3, duration: 0.5 }}
                >
                    <button 
                        onClick={onStart}
                        className='group relative inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-slate-950 rounded-full font-medium text-lg transition-all hover:scale-105 active:scale-95 shadow-[0_0_40px_-5px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_-10px_rgba(255,255,255,0.4)]'
                    >
                        <span className='relative z-10'>Try the Demo</span>
                    </button>
                    
                    <div className='mt-8 flex items-center justify-center gap-6 text-sm text-slate-500'>
                        <a href='https://github.com/Erebuzzz/CodeShield' target='_blank' rel='noopener' className='hover:text-white transition-colors flex items-center gap-2'>
                            GITHUB REPO
                        </a>
                        <span>|</span>
                        <span>v0.1.0</span>
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
};
