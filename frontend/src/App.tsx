import { useState } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ReactiveCodeGraph } from './components/ReactiveCodeGraph';
import { Logo } from './components/Logo';
import Docs from './components/Docs';
import { Home } from './components/Home';

import type { VerificationResult } from './services/api';

function App() {
  const [homeMode, setHomeMode] = useState<'hero' | 'demo'>('hero');
  const [code, setCode] = useState(`def calculate_total(items):
    return sum(item.price for item in items)`);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);

  const location = useLocation();
  const navigate = useNavigate();

  const handleBackToHome = () => {
    setHomeMode('hero');
    navigate('/');
  };

  const isDocs = location.pathname === '/docs';
  // Determine if background should be in 'reactive' mode (only on demo page)
  const bgMode = !isDocs && homeMode === 'demo' ? 'reactive' : 'ambient';

  return (
    <div className="relative w-full min-h-screen overflow-hidden selection:bg-brand-500 selection:text-white bg-dark-bg font-sans">
      {/* Background Layer */}
      <div className="fixed inset-0 z-0">
        <ReactiveCodeGraph mode={bgMode} code={code} />
        {/* Vignette Overlay (OceanX style depth) */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_0%,_#030305_90%)] opacity-90 pointer-events-none" />
      </div>

      {/* Navbar */}
      {!isDocs && (
        <nav className="relative z-50 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
          <div onClick={handleBackToHome} className="cursor-pointer hover:opacity-80 transition-opacity">
            <Logo size="sm" />
          </div>
          <div className="hidden md:flex items-center gap-8">
            <button onClick={() => navigate('/docs')} className="text-sm text-slate-400 hover:text-white transition-colors font-medium cursor-pointer">
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
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={
              <Home 
                mode={homeMode} 
                setMode={setHomeMode}
                code={code}
                setCode={setCode}
                verificationResult={verificationResult}
                setVerificationResult={setVerificationResult}
              />
            } />
            <Route path="/docs" element={
              <Docs onBack={() => navigate('/')} />
            } />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
