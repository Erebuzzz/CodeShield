/**
 * ReactiveCodeGraph - Animated background with AST nodes and connection lines
 * Creates a living dependency graph that pulses with code analysis
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Node {
    id: string;
    x: number;
    y: number;
    type: 'function' | 'class' | 'import' | 'variable';
    label: string;
    active: boolean;
}

interface Connection {
    from: string;
    to: string;
    active: boolean;
}

const NODE_COLORS = {
    function: '#22c55e',  // green
    class: '#3b82f6',     // blue
    import: '#f59e0b',    // gold
    variable: '#06b6d4',  // cyan
};

const generateNodes = (count: number): Node[] => {
    const types: Array<'function' | 'class' | 'import' | 'variable'> = ['function', 'class', 'import', 'variable'];
    const labels = {
        function: ['verify()', 'check()', 'parse()', 'analyze()', 'fix()'],
        class: ['TrustGate', 'StyleForge', 'ContextVault', 'Sandbox'],
        import: ['import ast', 'import re', 'from typing', 'import json'],
        variable: ['result', 'issues', 'code', 'config', 'data'],
    };

    return Array.from({ length: count }, (_, i) => {
        const type = types[Math.floor(Math.random() * types.length)];
        return {
            id: `node-${i}`,
            x: Math.random() * 100,
            y: Math.random() * 100,
            type,
            label: labels[type][Math.floor(Math.random() * labels[type].length)],
            active: false,
        };
    });
};

const generateConnections = (nodes: Node[]): Connection[] => {
    const connections: Connection[] = [];
    nodes.forEach((node, i) => {
        if (i > 0 && Math.random() > 0.5) {
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

export const ReactiveCodeGraph: React.FC<{ isProcessing?: boolean }> = ({ isProcessing = false }) => {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [connections, setConnections] = useState<Connection[]>([]);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const initialNodes = generateNodes(15);
        setNodes(initialNodes);
        setConnections(generateConnections(initialNodes));
    }, []);

    // Animate nodes when processing
    useEffect(() => {
        if (!isProcessing) return;

        const interval = setInterval(() => {
            setNodes(prev => {
                const updated = [...prev];
                const randomIndex = Math.floor(Math.random() * updated.length);
                updated[randomIndex] = { ...updated[randomIndex], active: true };

                setTimeout(() => {
                    setNodes(p => p.map((n, i) => i === randomIndex ? { ...n, active: false } : n));
                }, 800);

                return updated;
            });

            setConnections(prev => {
                if (prev.length === 0) return prev;
                const updated = [...prev];
                const randomIndex = Math.floor(Math.random() * updated.length);
                updated[randomIndex] = { ...updated[randomIndex], active: true };

                setTimeout(() => {
                    setConnections(p => p.map((c, i) => i === randomIndex ? { ...c, active: false } : c));
                }, 600);

                return updated;
            });
        }, 500);

        return () => clearInterval(interval);
    }, [isProcessing]);

    // Slow ambient animation when idle
    useEffect(() => {
        if (isProcessing) return;

        const interval = setInterval(() => {
            setNodes(prev => {
                const updated = [...prev];
                const randomIndex = Math.floor(Math.random() * updated.length);
                updated[randomIndex] = { ...updated[randomIndex], active: true };

                setTimeout(() => {
                    setNodes(p => p.map((n, i) => i === randomIndex ? { ...n, active: false } : n));
                }, 1500);

                return updated;
            });
        }, 2000);

        return () => clearInterval(interval);
    }, [isProcessing]);

    const getNodePosition = (nodeId: string) => {
        const node = nodes.find(n => n.id === nodeId);
        return node ? { x: node.x, y: node.y } : { x: 0, y: 0 };
    };

    return (
        <div
            ref={containerRef}
            className="absolute inset-0 overflow-hidden pointer-events-none"
            style={{ opacity: 0.4 }}
        >
            {/* Connection Lines */}
            <svg className="absolute inset-0 w-full h-full">
                <defs>
                    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#22c55e" stopOpacity="0.3" />
                        <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.3" />
                    </linearGradient>
                </defs>
                {connections.map((conn, i) => {
                    const from = getNodePosition(conn.from);
                    const to = getNodePosition(conn.to);
                    return (
                        <motion.line
                            key={i}
                            x1={`${from.x}%`}
                            y1={`${from.y}%`}
                            x2={`${to.x}%`}
                            y2={`${to.y}%`}
                            stroke={conn.active ? '#22c55e' : 'url(#lineGradient)'}
                            strokeWidth={conn.active ? 2 : 1}
                            strokeOpacity={conn.active ? 0.8 : 0.2}
                            animate={{
                                strokeOpacity: conn.active ? [0.2, 0.8, 0.2] : 0.2,
                            }}
                            transition={{ duration: 0.6 }}
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
                            opacity: node.active ? 1 : 0.3,
                            scale: node.active ? 1.2 : 1,
                        }}
                        transition={{ duration: 0.3 }}
                    >
                        {/* Node Circle */}
                        <div
                            className="relative flex items-center justify-center"
                            style={{
                                width: node.type === 'class' ? 12 : 8,
                                height: node.type === 'class' ? 12 : 8,
                            }}
                        >
                            <div
                                className="absolute inset-0 rounded-full"
                                style={{
                                    backgroundColor: NODE_COLORS[node.type],
                                    boxShadow: node.active
                                        ? `0 0 20px ${NODE_COLORS[node.type]}, 0 0 40px ${NODE_COLORS[node.type]}50`
                                        : 'none',
                                }}
                            />

                            {/* Pulse ring when active */}
                            {node.active && (
                                <motion.div
                                    className="absolute inset-0 rounded-full"
                                    style={{ border: `1px solid ${NODE_COLORS[node.type]}` }}
                                    initial={{ scale: 1, opacity: 1 }}
                                    animate={{ scale: 2.5, opacity: 0 }}
                                    transition={{ duration: 0.8 }}
                                />
                            )}
                        </div>

                        {/* Label (only show when active for larger nodes) */}
                        {node.active && node.type !== 'variable' && (
                            <motion.span
                                className="absolute top-full mt-1 text-[10px] font-mono whitespace-nowrap"
                                style={{ color: NODE_COLORS[node.type] }}
                                initial={{ opacity: 0, y: -5 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                            >
                                {node.label}
                            </motion.span>
                        )}
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    );
};

export default ReactiveCodeGraph;
