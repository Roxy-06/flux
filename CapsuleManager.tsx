"use client";

import React, { useState } from 'react';
import { Package, Download, ExternalLink, Copy, CheckCircle, AlertCircle } from 'lucide-react';
import { 
  generateCapsule, 
  getCapsule, 
  exportCapsuleJson, 
  startMCPServer, 
  stopMCPServer, 
  getMCPServerStatus,
  type Capsule 
} from '../lib/api';

interface CapsuleManagerProps {
  owner: string;
  repo: string;
}

export default function CapsuleManager({ owner, repo }: CapsuleManagerProps) {
  const [capsule, setCapsule] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mcpServerRunning, setMcpServerRunning] = useState(false);
  const [exportedJson, setExportedJson] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleGenerateCapsule = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await generateCapsule(owner, repo);
      setCapsule(result.capsule);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate CAPSULE');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCapsule = async () => {
    try {
      const result = await exportCapsuleJson(owner, repo);
      setExportedJson(result.capsule_json);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export CAPSULE');
    }
  };

  const handleCopyToClipboard = () => {
    if (exportedJson) {
      navigator.clipboard.writeText(exportedJson);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleStartMCP = async () => {
    try {
      await startMCPServer();
      setMcpServerRunning(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start MCP server');
    }
  };

  const handleStopMCP = async () => {
    try {
      await stopMCPServer();
      setMcpServerRunning(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop MCP server');
    }
  };

  return (
    <div className="space-y-6">
      {/* CAPSULE Generation */}
      <div className="akaru-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#df7d4c]/15 text-[#df7d4c] flex items-center justify-center">
              <Package className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#171817]">Project CAPSULE</h3>
              <p className="text-xs text-[#6b6963]">Portable project state snapshot</p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={handleGenerateCapsule}
              disabled={loading}
              className="btn-terracotta px-4 py-2 text-xs font-bold disabled:opacity-50"
            >
              {loading ? 'Generating...' : capsule ? 'Regenerate' : 'Generate'}
            </button>
            
            {capsule && (
              <button
                onClick={handleExportCapsule}
                className="btn-white px-4 py-2 text-xs font-bold flex items-center gap-2"
              >
                <Download className="w-3 h-3" />
                Export
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600">
            {error}
          </div>
        )}

        {capsule && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-[#fffefa] rounded-xl border">
              <div className="font-bold text-[#171817]">{capsule.metadata.total_components}</div>
              <div className="text-[#6b6963]">Components</div>
            </div>
            <div className="p-3 bg-[#fffefa] rounded-xl border">
              <div className="font-bold text-[#171817]">{capsule.metadata.total_tasks}</div>
              <div className="text-[#6b6963]">Tasks</div>
            </div>
            <div className="p-3 bg-[#fffefa] rounded-xl border">
              <div className="font-bold text-[#171817]">{capsule.metadata.total_decisions}</div>
              <div className="text-[#6b6963]">Decisions</div>
            </div>
            <div className="p-3 bg-[#fffefa] rounded-xl border">
              <div className="font-bold text-[#171817]">{Object.keys(capsule.code_index || {}).length}</div>
              <div className="text-[#6b6963]">Code Pointers</div>
            </div>
          </div>
        )}
      </div>

      {/* MCP Server Control */}
      <div className="akaru-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-[#171817] flex items-center gap-2">
              MCP Server
              <div className={`w-2 h-2 rounded-full ${mcpServerRunning ? 'bg-green-500' : 'bg-gray-400'}`} />
            </h3>
            <p className="text-xs text-[#6b6963]">
              {mcpServerRunning ? 'Ready for AI tool connections' : 'Start server to enable AI tool integration'}
            </p>
          </div>
          
          <button
            onClick={mcpServerRunning ? handleStopMCP : handleStartMCP}
            className={`px-4 py-2 text-xs font-bold ${
              mcpServerRunning 
                ? 'btn-white' 
                : 'btn-terracotta'
            }`}
          >
            {mcpServerRunning ? 'Stop Server' : 'Start Server'}
          </button>
        </div>

        {mcpServerRunning && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 text-xs text-green-700">
              <CheckCircle className="w-4 h-4" />
              <span>MCP server running on port 3001</span>
            </div>
            <div className="text-xs text-green-600 mt-1">
              AI tools can now access get_capsule, get_code, and get_state_registry tools
            </div>
          </div>
        )}
      </div>

      {/* JSON Export Modal */}
      {exportedJson && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="akaru-card max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold">CAPSULE JSON Export</h3>
              <button
                onClick={() => setExportedJson(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-xs text-[#6b6963]">
                  Copy this JSON and paste it into your AI tool chat
                </p>
                <button
                  onClick={handleCopyToClipboard}
                  className="btn-terracotta px-3 py-1 text-xs font-bold flex items-center gap-2"
                >
                  {copySuccess ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  {copySuccess ? 'Copied!' : 'Copy'}
                </button>
              </div>
              
              <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-auto max-h-96 font-mono">
                {exportedJson}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
