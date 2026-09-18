"use client";

import React, { useEffect, useRef } from 'react';

interface BlastRadiusAnimationProps {
  nodes: Array<{id: string, x: number, y: number}>;
  focusedNodeId?: string;
  affectedNodeIds?: string[];
}

export default function BlastRadiusAnimation({ nodes, focusedNodeId, affectedNodeIds = [] }: BlastRadiusAnimationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);

  useEffect(() => {
    if (!focusedNodeId || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frame = 0;
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Find focused node
      const focusedNode = nodes.find(n => n.id === focusedNodeId);
      if (!focusedNode) return;
      
      // Draw pulse animation from focused node
      const pulseRadius = (Math.sin(frame * 0.1) + 1) * 20 + 10;
      const pulseOpacity = (Math.sin(frame * 0.1) + 1) * 0.3 + 0.1;
      
      ctx.beginPath();
      ctx.arc(focusedNode.x, focusedNode.y, pulseRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(223, 125, 76, ${pulseOpacity})`;
      ctx.fill();
      
      // Draw connections to affected nodes
      affectedNodeIds.forEach(nodeId => {
        const affectedNode = nodes.find(n => n.id === nodeId);
        if (!affectedNode) return;
        
        // Draw animated line
        const progress = (Math.sin(frame * 0.05) + 1) / 2;
        const x = focusedNode.x + (affectedNode.x - focusedNode.x) * progress;
        const y = focusedNode.y + (affectedNode.y - focusedNode.y) * progress;
        
        ctx.beginPath();
        ctx.moveTo(focusedNode.x, focusedNode.y);
        ctx.lineTo(x, y);
        ctx.strokeStyle = 'rgba(223, 125, 76, 0.6)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw pulse at affected node
        ctx.beginPath();
        ctx.arc(affectedNode.x, affectedNode.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(223, 125, 76, ${0.5 * progress})`;
        ctx.fill();
      });
      
      frame++;
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [focusedNodeId, affectedNodeIds, nodes]);

  if (!focusedNodeId) return null;

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={600}
      className="absolute inset-0 pointer-events-none z-10"
      style={{ mixBlendMode: 'multiply' }}
    />
  );
}
