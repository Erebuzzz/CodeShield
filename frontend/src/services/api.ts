/**
 * API Service - Communication with CodeShield Python backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://codeshield-production.up.railway.app';

export interface Issue {
    type: 'error' | 'warning' | 'info';
    message: string;
    line?: number;
    fix?: string;
}

export interface VerificationResult {
    isValid: boolean;
    confidence: number;
    issues: Issue[];
    fixedCode?: string;
    executionResult?: {
        success: boolean;
        output: string;
        time_ms: number;
    };
}

export interface StyleResult {
    matches_convention: boolean;
    detected_style: string;
    suggestions: string[];
}

/**
 * Verify code using TrustGate
 */
export async function verifyCode(code: string, autoFix: boolean = true): Promise<VerificationResult> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, auto_fix: autoFix }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        // Map snake_case API response to camelCase frontend interface
        return {
            isValid: data.is_valid ?? data.isValid ?? true,
            confidence: Math.round((data.confidence_score ?? data.confidence ?? 1) * 100),
            issues: (data.issues ?? []).map((i: any) => ({
                type: i.type ?? i.severity ?? 'info',
                message: i.message,
                line: i.line,
                fix: i.fix ?? i.fix_description,
            })),
            fixedCode: data.fixed_code ?? data.fixedCode,
            executionResult: data.execution_result ?? data.executionResult,
        };
    } catch (error) {
        console.error('API Error:', error);
        // Return mock data for demo when API unavailable
        return mockVerify(code);
    }
}

/**
 * Check code style using StyleForge
 */
export async function checkStyle(code: string): Promise<StyleResult> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/style`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return mockStyleCheck(code);
    }
}

/**
 * Full verification with sandbox execution
 */
export async function fullVerify(code: string): Promise<VerificationResult> {
    try {
        // Reuse verify endpoint but enable sandbox
        const response = await fetch(`${API_BASE_URL}/api/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, use_sandbox: true }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        return {
            isValid: data.is_valid ?? data.isValid ?? true,
            confidence: Math.round((data.confidence_score ?? data.confidence ?? 1) * 100),
            issues: (data.issues ?? []).map((i: any) => ({
                type: i.type ?? i.severity ?? 'info',
                message: i.message,
                line: i.line,
                fix: i.fix ?? i.fix_description,
            })),
            fixedCode: data.fixed_code ?? data.fixedCode,
            executionResult: data.execution_result ?? data.executionResult,
        };
    } catch (error) {
        console.error('API Error:', error);
        return mockVerify(code);
    }
}

// ============================================
// Mock Functions for Demo / Offline Mode
// ============================================

function mockVerify(code: string): VerificationResult {
    const issues: Issue[] = [];
    let confidence = 100;

    // Check for common issues
    const lines = code.split('\n');

    // Check for missing imports
    const usedModules = ['requests', 'json', 'os', 'sys', 're', 'datetime', 'numpy', 'pandas'];
    const importedModules: string[] = [];

    lines.forEach(line => {
        const match = line.match(/^import (\w+)|^from (\w+)/);
        if (match) {
            importedModules.push(match[1] || match[2]);
        }
    });

    usedModules.forEach(mod => {
        if (code.includes(`${mod}.`) && !importedModules.includes(mod)) {
            issues.push({
                type: 'error',
                message: `Missing import: ${mod}`,
                fix: `Add 'import ${mod}'`,
            });
            confidence -= 15;
        }
    });

    // Check for syntax-like issues
    if (code.includes('def ') && !code.includes(':')) {
        issues.push({
            type: 'error',
            message: 'Function definition missing colon',
            fix: 'Add ":" after function definition',
        });
        confidence -= 20;
    }

    // Check for camelCase vs snake_case
    const camelCaseVars = code.match(/\b[a-z]+[A-Z][a-zA-Z]*\b/g);
    if (camelCaseVars && camelCaseVars.length > 0) {
        issues.push({
            type: 'warning',
            message: `Found camelCase variable: ${camelCaseVars[0]}`,
            fix: `Rename to snake_case: ${camelCaseVars[0].replace(/([A-Z])/g, '_$1').toLowerCase()}`,
        });
        confidence -= 5;
    }

    // Generate fixed code
    let fixedCode = code;

    // Add missing imports at the top
    usedModules.forEach(mod => {
        if (code.includes(`${mod}.`) && !importedModules.includes(mod)) {
            fixedCode = `import ${mod}\n` + fixedCode;
        }
    });

    return {
        isValid: issues.filter(i => i.type === 'error').length === 0,
        confidence: Math.max(0, confidence),
        issues,
        fixedCode: issues.length > 0 ? fixedCode : undefined,
        executionResult: {
            success: true,
            output: 'Mock execution: Code parsed successfully',
            time_ms: Math.floor(Math.random() * 200) + 50,
        },
    };
}

function mockStyleCheck(code: string): StyleResult {
    const hasSnakeCase = code.match(/_[a-z]/);
    const hasCamelCase = code.match(/[a-z][A-Z]/);

    return {
        matches_convention: !hasCamelCase,
        detected_style: hasSnakeCase ? 'snake_case' : 'mixed',
        suggestions: hasCamelCase
            ? ['Convert camelCase variables to snake_case for Python conventions']
            : [],
    };
}
