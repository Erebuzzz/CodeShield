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
    type: 'function' | 'class' | 'import' | 'variable' | 'mcp';
    label: string;
    active: boolean;
    size: number;
}

interface Connection {
    from: string;
    to: string;
    active: boolean;
}

// Vibrant colors for the animated background
const NODE_COLORS = {
    function: '#10b981',  // emerald
    class: '#8b5cf6',     // purple
    import: '#f59e0b',    // amber
    variable: '#06b6d4',  // cyan
    mcp: '#ec4899',       // pink - MCP connections
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
            type,
            label: labels[type][Math.floor(Math.random() * labels[type].length)],
            active: false,
            size: type === 'class' ? 6 : type === 'mcp' ? 8 : 4,
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
    isProcessing?: boolean;
    mcpConnected?: boolean;
}

export const ReactiveCodeGraph: React.FC<ReactiveCodeGraphProps> = ({ 
    isProcessing = false,
    mcpConnected = true 
}) => {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [connections, setConnections] = useState<Connection[]>([]);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const initialNodes = generateNodes(20);
        setNodes(initialNodes);
        setConnections(generateConnections(initialNodes));
    }, []);

    // Fast animation when processing
    useEffect(() => {
        if (!isProcessing) return;

        const interval = setInterval(() => {
            // Activate multiple nodes at once during processing
            setNodes(prev => {
                const updated = [...prev];
                const count = Math.floor(Math.random() * 3) + 2;
                for (let j = 0; j < count; j++) {
                    const randomIndex = Math.floor(Math.random() * updated.length);
                    updated[randomIndex] = { ...updated[randomIndex], active: true };
                }
                return updated;
            });

            setTimeout(() => {
                setNodes(p => p.map(n => ({ ...n, active: false })));
            }, 400);

            setConnections(prev => {
                if (prev.length === 0) return prev;
                const updated = [...prev];
                const count = Math.min(3, updated.length);
                for (let j = 0; j < count; j++) {
                    const randomIndex = Math.floor(Math.random() * updated.length);
                    updated[randomIndex] = { ...updated[randomIndex], active: true };
                }
                return updated;
            });

            setTimeout(() => {
                setConnections(p => p.map(c => ({ ...c, active: false })));
            }, 300);
        }, 200);

        return () => clearInterval(interval);
    }, [isProcessing]);

    // Ambient animation - MCP pulse effect
    useEffect(() => {
        if (isProcessing) return;

        const interval = setInterval(() => {
            setNodes(prev => {
                const updated = [...prev];
                // Prioritize MCP nodes when connected
                const mcpNodes = updated.filter(n => n.type === 'mcp');
                const targetNodes = mcpConnected && mcpNodes.length > 0 ? mcpNodes : updated;
                const randomIndex = Math.floor(Math.random() * targetNodes.length);
                const nodeIndex = updated.findIndex(n => n.id === targetNodes[randomIndex].id);
                if (nodeIndex >= 0) {
                    updated[nodeIndex] = { ...updated[nodeIndex], active: true };
                }
                return updated;
            });

            setTimeout(() => {
                setNodes(p => p.map(n => ({ ...n, active: false })));
            }, 1200);
        }, 2500);

        return () => clearInterval(interval);
    }, [isProcessing, mcpConnected]);

    const getNodePosition = (nodeId: string) => {
        const node = nodes.find(n => n.id === nodeId);
        return node ? { x: node.x, y: node.y } : { x: 0, y: 0 };
    };

    return (
        <div
            ref={containerRef}
            className="fixed inset-0 overflow-hidden pointer-events-none z-0"
        >
            {/* Gradient Orbs */}
            <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px]" />
            {mcpConnected && (
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-pink-500/5 rounded-full blur-[80px] animate-pulse" />
            )}

            {/* Connection Lines */}
            <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.6 }}>
                <defs>
                    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.4" />
                    </linearGradient>
                    <linearGradient id="mcpGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#ec4899" stopOpacity="0.6" />
                        <stop offset="100%" stopColor="#10b981" stopOpacity="0.6" />
                    </linearGradient>
                </defs>
                {connections.map((conn, i) => {
                    const from = getNodePosition(conn.from);
                    const to = getNodePosition(conn.to);
                    const fromNode = nodes.find(n => n.id === conn.from);
                    const isMcpConnection = fromNode?.type === 'mcp';
                    return (
                        <motion.line
                            key={i}
                            x1={`${from.x}%`}
                            y1={`${from.y}%`}
                            x2={`${to.x}%`}
                            y2={`${to.y}%`}
                            stroke={conn.active ? (isMcpConnection ? '#ec4899' : '#10b981') : (isMcpConnection ? 'url(#mcpGradient)' : 'url(#lineGradient)')}
                            strokeWidth={conn.active ? 2 : 1}
                            strokeOpacity={conn.active ? 0.9 : 0.15}
                            strokeLinecap="round"
                            animate={{
                                strokeOpacity: conn.active ? [0.15, 0.9, 0.15] : 0.15,
                            }}
                            transition={{ duration: 0.4 }}
                        />
                    );
                })}
            </svg>

            {/* AST Nodes */}
            <AnimatePresence>
                {nodes.map((node) => (
                    <motion.div
                        key={node.id}
                        className="absolute"
                        style={{
                            left: `${node.x}%`,
                            top: `${node.y}%`,
                            transform: 'translate(-50%, -50%)',
                        }}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{
                            opacity: node.active ? 1 : 0.4,
                            scale: node.active ? 1.5 : 1,
                        }}
                        transition={{ duration: 0.2 }}
                    >
                        {/* Node Circle */}
                        <div
                            className="relative flex items-center justify-center rounded-full"
                            style={{
                                width: node.size,
                                height: node.size,
                                backgroundColor: NODE_COLORS[node.type],
                                boxShadow: node.active
                                    ? `0 0 20px ${NODE_COLORS[node.type]}, 0 0 40px ${NODE_COLORS[node.type]}60`
                                    : `0 0 8px ${NODE_COLORS[node.type]}40`,
                            }}
                        />

                        {/* Pulse ring when active */}
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
                                className="absolute left-full ml-2 text-[9px] font-mono whitespace-nowrap"
                                style={{ color: NODE_COLORS[node.type] }}
                                initial={{ opacity: 0, x: -5 }}
                                animate={{ opacity: 0.8, x: 0 }}
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
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] text-slate-500 font-mono">MCP Connected</span>
                </div>
            )}
        </div>
    );
};

export default ReactiveCodeGraph;
