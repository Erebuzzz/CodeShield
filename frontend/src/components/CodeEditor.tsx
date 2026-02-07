import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { verifyCode, type VerificationResult } from '../services/api';

// Icons
const PlayIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-white hover:text-white/80 transition-colors">
    <path d="M5 3l14 9-14 9V3z" fill="currentColor" />
  </svg>
);

const LoaderIcon = () => (
  <svg className="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

const UploadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const TemplateIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" />
    <rect x="14" y="3" width="7" height="7" />
    <rect x="14" y="14" width="7" height="7" />
    <rect x="3" y="14" width="7" height="7" />
  </svg>
);

const CheckCircle = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="text-emerald-400">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);

const XCircle = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="text-red-400">
    <circle cx="12" cy="12" r="10" />
    <line x1="15" y1="9" x2="9" y2="15" />
    <line x1="9" y1="9" x2="15" y2="15" />
  </svg>
);

// --- Code Templates ---
interface CodeTemplate {
  label: string;
  description: string;
  expectPass: boolean;
  code: string;
}

const CODE_TEMPLATES: CodeTemplate[] = [
  // ---- Passing examples ----
  {
    label: 'Clean Function',
    description: 'Well-structured code with no issues',
    expectPass: true,
    code: `def calculate_total(prices, tax_rate=0.1):
    """Calculate total price with tax."""
    subtotal = sum(prices)
    tax = subtotal * tax_rate
    return round(subtotal + tax, 2)

print(calculate_total([19.99, 5.50, 12.00]))`,
  },
  {
    label: 'File Reader',
    description: 'Clean file handling with context manager',
    expectPass: true,
    code: `def read_config(path):
    """Read a config file and return lines."""
    with open(path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

config = read_config("settings.txt")
print(config)`,
  },
  {
    label: 'Data Processor',
    description: 'Clean list comprehension & logic',
    expectPass: true,
    code: `def filter_and_transform(items, threshold=10):
    """Filter items above threshold and double them."""
    result = [x * 2 for x in items if x > threshold]
    return sorted(result, reverse=True)

data = [5, 12, 3, 18, 7, 25, 9, 14]
print(filter_and_transform(data))`,
  },
  // ---- Failing examples ----
  {
    label: 'Type Error',
    description: 'Adds arithmetic result to a string',
    expectPass: false,
    code: `def add_numbers(a, b):
    # This function bravely returns nonsense.
    return a * b + "not even a number"

print(add_numbers(5, 7))`,
  },
  {
    label: 'Missing Import',
    description: 'Uses requests without importing it',
    expectPass: false,
    code: `def fetch_data(url):
    response = requests.get(url)
    data = json.loads(response.text)
    return data

result = fetch_data("https://api.example.com/data")
print(result)`,
  },
  {
    label: 'Syntax Error',
    description: 'Missing colon in function definition',
    expectPass: false,
    code: `def broken_function(x, y)
    result = x + y
    return result

print(broken_function(1, 2))`,
  },
  {
    label: 'Mixed Issues',
    description: 'Multiple problems in one snippet',
    expectPass: false,
    code: `def process_data(items):
    total = sum(items)
    average = total / len(items)
    result = os.path.join("/tmp", "output.txt")
    timestamp = datetime.now().isoformat()
    return {"avg": average, "file": result, "time": timestamp}

print(process_data([1, 2, 3]))`,
  },
];

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  onVerify: (result: VerificationResult) => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ code, onChange, onVerify }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleVerify = async () => {
    setIsProcessing(true);
    try {
      const result = await verifyCode(code);
      onVerify(result);
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result;
      if (typeof text === 'string') {
        onChange(text);
      }
    };
    reader.readAsText(file);
    // Reset so same file can be re-imported
    e.target.value = '';
  };

  const loadTemplate = (template: CodeTemplate) => {
    onChange(template.code);
    setShowTemplates(false);
  };

  const lineCount = code.split('\n').length;

  return (
    <div className="h-full flex flex-col bg-slate-900/30 backdrop-blur-md rounded-2xl border border-white/5 overflow-hidden shadow-2xl shadow-indigo-500/10">
      {/* Header */}
      <div className="bg-white/[0.03] border-b border-white/5 px-4 py-3 flex items-center justify-between">
        <div className="flex gap-2 items-center">
            <div className="flex gap-1.5 mr-4">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
            </div>
            <span className="text-xs font-mono text-slate-500">script.py</span>
            <span className="text-[10px] text-slate-600 ml-2 px-1.5 py-0.5 bg-slate-800/60 rounded">Python</span>
        </div>
        <div className="flex items-center gap-2">
            {/* Import File */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".py,.txt,.pyw,.pyi"
              className="hidden"
              onChange={handleFileImport}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-1.5 text-[11px] text-slate-400 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-white/5 transition-all"
              title="Import from file (.py, .txt)"
            >
              <UploadIcon />
              <span>Import</span>
            </button>

            {/* Templates */}
            <div className="relative">
              <button
                onClick={() => setShowTemplates(!showTemplates)}
                className={`flex items-center gap-1.5 text-[11px] px-2.5 py-1.5 rounded-lg transition-all ${
                  showTemplates ? 'text-white bg-white/10' : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
                title="Load a code template"
              >
                <TemplateIcon />
                <span>Templates</span>
              </button>

              {/* Templates Dropdown */}
              <AnimatePresence>
                {showTemplates && (
                  <motion.div
                    initial={{ opacity: 0, y: -4, scale: 0.97 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -4, scale: 0.97 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 top-full mt-2 w-72 bg-slate-900 border border-white/10 rounded-xl shadow-2xl shadow-black/50 z-50 overflow-hidden"
                  >
                    <div className="px-3 py-2 border-b border-white/5">
                      <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Try an Example</span>
                    </div>
                    <div className="max-h-80 overflow-y-auto custom-scrollbar">
                      {CODE_TEMPLATES.map((t, idx) => (
                        <button
                          key={idx}
                          onClick={() => loadTemplate(t)}
                          className="w-full text-left px-3 py-2.5 hover:bg-white/5 transition-colors flex items-start gap-2.5 group border-b border-white/[0.03] last:border-0"
                        >
                          <div className="mt-0.5 shrink-0">
                            {t.expectPass ? <CheckCircle /> : <XCircle />}
                          </div>
                          <div className="min-w-0">
                            <div className="text-xs font-medium text-slate-200 group-hover:text-white flex items-center gap-2">
                              {t.label}
                              <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${
                                t.expectPass
                                  ? 'bg-emerald-500/10 text-emerald-400'
                                  : 'bg-red-500/10 text-red-400'
                              }`}>
                                {t.expectPass ? 'PASS' : 'FAIL'}
                              </span>
                            </div>
                            <p className="text-[10px] text-slate-500 mt-0.5 leading-snug">{t.description}</p>
                          </div>
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
        </div>
      </div>

      {/* Editor Area */}
      <div className="relative flex-1 flex overflow-hidden group">
        {/* Line Numbers */}
        <div className="w-12 bg-white/[0.01] border-r border-white/5 pt-4 text-right pr-3 select-none text-slate-700 font-mono text-xs leading-6">
          {Array.from({ length: Math.max(lineCount, 20) }).map((_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>

        {/* Textarea */}
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 bg-transparent text-slate-300 font-mono text-xs leading-6 p-4 resize-none focus:outline-none focus:ring-0 custom-scrollbar whitespace-pre"
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
        />
        
        {/* Floating Run Button */}
        <div className="absolute bottom-6 right-6">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleVerify}
                disabled={isProcessing}
                className={`
                    h-14 px-6 rounded-full flex items-center gap-3 font-medium transition-all shadow-lg shadow-brand-500/25
                    ${isProcessing 
                        ? 'bg-slate-700 cursor-wait text-slate-400' 
                        : 'bg-gradient-to-r from-brand-500 to-violet-600 text-white hover:shadow-brand-500/40'
                    }
                `}
            >
                {isProcessing ? (
                    <>
                        <LoaderIcon />
                        <span>Analyzing...</span>
                    </>
                ) : (
                    <>
                        <PlayIcon />
                        <span>Run Verification</span>
                    </>
                )}
            </motion.button>
        </div>
      </div>

      {/* Click-away overlay for templates dropdown */}
      {showTemplates && (
        <div className="fixed inset-0 z-40" onClick={() => setShowTemplates(false)} />
      )}
    </div>
  );
};
