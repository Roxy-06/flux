"use client";

import React, { useState } from 'react';
import { Package, Download, ExternalLink, Copy, CheckCircle, AlertCircle } from 'lucide-react';

interface CapsuleManagerProps {
  owner: string;
  repo: string;
}

export default function CapsuleManager({ owner, repo }: CapsuleManagerProps) {
  const [capsule, setCapsule] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateCapsule = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Placeholder for actual API call
      console.log(`Generate CAPSULE for ${owner}/${repo}`);
      setCapsule({ metadata: { total_components: 5, total_tasks: 3, total_decisions: 2 } });
    } catch (err) {
      setError('Failed to generate CAPSULE');
    } finally {
      setLoading(false);
    }
  };

  return (
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
        
        <button
          onClick={handleGenerateCapsule}
          disabled={loading}
          className="btn-terracotta px-4 py-2 text-xs font-bold disabled:opacity-50"
        >
          {loading ? 'Generating...' : capsule ? 'Regenerate' : 'Generate'}
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600">
          {error}
        </div>
      )}

      {capsule && (
        <div className="grid grid-cols-3 gap-3 text-xs">
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
        </div>
      )}
    </div>
  );
}
