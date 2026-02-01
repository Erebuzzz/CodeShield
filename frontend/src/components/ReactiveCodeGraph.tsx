/**
 * ReactiveCodeGraph - Animated AST background with colorful nodes
 * Vibrant colors for the background animation only
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Node {
    id: string;
    x: number;
    y: number;
    offsetX: number;
    offsetY: number;
    type: 'function' | 'class' | 'import' | 'variable' | 'mcp';
    label: string;
    active: boolean;
    size: number;
    duration: number;
}

interface Connection {
    from: string;
    to: string;
    active: boolean;
}

// Deep Techno/Scientific colors - Increased brightness for contrast
const NODE_COLORS = {
    function: '#818cf8',  // Bright Indigo
    class: '#c084fc',     // Bright Purple
    import: '#60a5fa',    // Bright Blue
    variable: '#a5b4fc',  // Very Light Indigo
    mcp: '#ffffff'        // Pure White
};

const generateNodes = (count: number): Node[] => {
    const types: Array<'function' | 'class' | 'import' | 'variable' | 'mcp'> = ['function', 'class', 'import', 'variable', 'mcp'];
    const labels = {
        function: ['verify()', 'check()', 'parse()', 'analyze()', 'execute()'],
        class: ['TrustGate', 'StyleForge', 'ContextVault', 'Sandbox'],
        import: ['ast', 'typing', 'httpx', 'sqlite3'],
        variable: ['result', 'issues', 'code', 'context'],
        mcp: ['MCP', 'tool', 'hook', 'server'],
    };

    return Array.from({ length: count }, (_, i) => {
        const type = types[Math.floor(Math.random() * types.length)];
        return {
            id: `node-${i}`,
            x: 10 + Math.random() * 80,
            y: 10 + Math.random() * 80,
            offsetX: Math.random() * 5 - 2.5,
            offsetY: Math.random() * 5 - 2.5,
            type,
            label: labels[type][Math.floor(Math.random() * labels[type].length)],
            active: false,
            size: type === 'class' ? 6 : type === 'mcp' ? 8 : 4,
            duration: 3 + Math.random() * 2,
        };
    });
};

const generateConnections = (nodes: Node[]): Connection[] => {
    const connections: Connection[] = [];
    nodes.forEach((node, i) => {
        // Create more connections for MCP nodes
        const connectionChance = node.type === 'mcp' ? 0.7 : 0.4;
        if (i > 0 && Math.random() > (1 - connectionChance)) {
            const targetIndex = Math.floor(Math.random() * i);
            connections.push({
                from: node.id,
                to: nodes[targetIndex].id,
                active: false,
            });
        }
    });
    return connections;
};

interface ReactiveCodeGraphProps {
    mode?: 'ambient' | 'reactive';
    code?: string;
    isProcessing?: boolean;
    mcpConnected?: boolean;
}

export const ReactiveCodeGraph: React.FC<ReactiveCodeGraphProps> = ({ 
    mode = 'ambient',
    code = '',
    isProcessing = false,
    mcpConnected = true 
}) => {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [connections, setConnections] = useState<Connection[]>([]);
    const containerRef = useRef<HTMLDivElement>(null);

    // Initial setup and mode reaction
    useEffect(() => {
        const count = mode === 'reactive' ? 30 : 20;
        const initialNodes = generateNodes(count);
        
        // Use timeout to avoid synchronous state update warning during render
        const timer = setTimeout(() => {
            setNodes(initialNodes);
            setConnections(generateConnections(initialNodes));
        }, 0);
        
        return () => clearTimeout(timer);
    }, [mode]);

    // React to code typing
    useEffect(() => {
        if (code) {
           const timer = setTimeout(() => {
                setNodes(prev => prev.map(n => ({
                    ...n,
                    active: Math.random() > 0.8
                })));
           }, 0);
           return () => clearTimeout(timer);
        }
    }, [code]);

    // Fast animation when processing
    useEffect(() => {
        if (!isProcessing) return;

        const interval = setInterval(() => {
            setNodes(prev => prev.map(n => ({
                ...n,
                x: n.x + (Math.random() - 0.5) * 2,
                y: n.y + (Math.random() - 0.5) * 2,
                active: Math.random() > 0.7,
            })));
        }, 100);

        return () => clearInterval(interval);
    }, [isProcessing]);

    return (
        <div ref={containerRef} className="absolute inset-0 overflow-hidden pointer-events-none z-0">
            {/* Ambient Background Gradient - Slight boost in opacity for contrast */}
            <div className="absolute inset-0 bg-gradient-to-br from-[#0f172a] via-[#030305] to-[#1e1b4b] opacity-80" />
            
            {/* Grid Pattern */}
            <div 
                className="absolute inset-0 opacity-[0.03]" 
                style={{
                    backgroundImage: `linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)`,
                    backgroundSize: '50px 50px'
                }}
            />

            <AnimatePresence>
                {/* Connections */}
                <svg className="absolute inset-0 w-full h-full">
                    {connections.map((conn, i) => {
                        const fromNode = nodes.find(n => n.id === conn.from);
                        const toNode = nodes.find(n => n.id === conn.to);
                        if (!fromNode || !toNode) return null;

                        return (
                            <motion.line
                                key={`conn-${i}`}
                                x1={`${fromNode.x}%`}
                                y1={`${fromNode.y}%`}
                                x2={`${toNode.x}%`}
                                y2={`${toNode.y}%`}
                                stroke={NODE_COLORS[fromNode.type]}
                                strokeWidth="1"
                                initial={{ opacity: 0, pathLength: 0 }}
                                animate={{ 
                                    opacity: isProcessing ? 0.6 : 0.2, // Increased opacity
                                    pathLength: 1 
                                }}
                                transition={{ duration: 1.5, repeat: Infinity, repeatType: "reverse" }}
                            />
                        );
                    })}
                </svg>

                {/* Nodes */}
                {nodes.map((node) => (
                    <motion.div
                        key={node.id}
                        className="absolute rounded-full"
                        style={{
                            left: `${node.x}%`,
                            top: `${node.y}%`,
                            width: node.size,
                            height: node.size,
                            backgroundColor: NODE_COLORS[node.type],
                            boxShadow: `0 0 15px ${NODE_COLORS[node.type]}`, // Enhanced glow
                        }}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ 
                            opacity: [0.4, 1, 0.4], // Higher minimum opacity
                            scale: [1, 1.5, 1],
                            x: `${node.x + node.offsetX}%`,
                            y: `${node.y + node.offsetY}%`
                        }}
                        transition={{
                            duration: node.duration,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    >
                        {/* Pulse Effect for Active Nodes */}
                        {node.active && (
                            <>
                                <motion.div
                                    className="absolute rounded-full"
                                    style={{ 
                                        inset: -2,
                                        border: `1px solid ${NODE_COLORS[node.type]}` 
                                    }}
                                    initial={{ scale: 1, opacity: 1 }}
                                    animate={{ scale: 3, opacity: 0 }}
                                    transition={{ duration: 0.8 }}
                                />
                                <motion.div
                                    className="absolute rounded-full"
                                    style={{ 
                                        inset: -2,
                                        border: `1px solid ${NODE_COLORS[node.type]}` 
                                    }}
                                    initial={{ scale: 1, opacity: 0.8 }}
                                    animate={{ scale: 2, opacity: 0 }}
                                    transition={{ duration: 0.6, delay: 0.1 }}
                                />
                            </>
                        )}

                        {/* Label */}
                        {node.active && (
                            <motion.span
                                className="absolute left-full ml-2 text-[10px] font-bold font-mono whitespace-nowrap drop-shadow-md"
                                style={{ color: NODE_COLORS[node.type] }}
                                initial={{ opacity: 0, x: -5 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0 }}
                            >
                                {node.label}
                            </motion.span>
                        )}
                    </motion.div>
                ))}
            </AnimatePresence>

            {/* MCP Status Indicator */}
            {mcpConnected && (
                <div className="absolute bottom-8 left-8 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.5)]" />
                    <span className="text-[10px] text-slate-400 font-mono font-medium tracking-wide">MCP LINKED</span>
                </div>
            )}
        </div>
    );
};

export default ReactiveCodeGraph;
