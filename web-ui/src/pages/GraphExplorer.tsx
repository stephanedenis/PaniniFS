import React, { useState, useEffect } from 'react';
import { Search, FileText, Share2, Clock, Database, Zap, TrendingUp } from 'lucide-react';

interface ChunkNode {
  hash: string;
  size: number;
  usageCount: number;
  files: string[];
}

interface FileNode {
  path: string;
  size: number;
  atoms: string[];
  timestamp?: number;
  dhatu?: {
    emotions: Record<string, number>;
    arousal: number;
    topEmotion: string;
  };
}

interface GraphStats {
  totalFiles: number;
  totalAtoms: number;
  uniqueAtoms: number;
  dedupRatio: number;
  storageSaved: number;
  avgReuse: number;
}

export default function GraphExplorer() {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<AtomNode | FileNode | null>(null);
  const [viewMode, setViewMode] = useState<'atoms' | 'files' | 'network'>('atoms');
  const [topAtoms, setTopAtoms] = useState<AtomNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:3000/api/dedup/stats');
      const data = await response.json();
      
      if (data.success) {
        setStats({
          totalFiles: data.total_files || 0,
          totalAtoms: data.total_chunks || 0,
          uniqueAtoms: data.unique_chunks || 0,
          dedupRatio: data.dedup_ratio || 0,
          storageSaved: data.storage_saved || 0,
          avgReuse: data.avg_reuse || 0,
        });

        // Transform top atoms
        if (data.top_chunks) {
          setTopAtoms(
            data.top_chunks.map((atom: any) => ({
              hash: atom.hash,
              size: atom.size,
              usageCount: atom.usage_count,
              files: [],
            }))
          );
        }
      }
    } catch (error) {
      console.error('Error fetching graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(2)} KB`;
    if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(2)} MB`;
    return `${(bytes / 1073741824).toFixed(2)} GB`;
  };

  const formatHash = (hash: string) => {
    return `${hash.substring(0, 8)}...${hash.substring(hash.length - 8)}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3">
                <Share2 className="text-blue-600" size={40} />
                Panini Graph Explorer
              </h1>
              <p className="text-gray-600 mt-2">
                Navigate the complete content-addressed storage graph
              </p>
            </div>
            
            {/* View Mode Selector */}
            <div className="flex gap-2">
              {(['atoms', 'files', 'network'] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    viewMode === mode
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by hash, filename, or content..."
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Files</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {stats.totalFiles.toLocaleString()}
                  </p>
                </div>
                <FileText className="text-blue-600" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Unique Chunks</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {stats.uniqueAtoms.toLocaleString()}
                  </p>
                </div>
                <Database className="text-purple-600" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Deduplication</p>
                  <p className="text-3xl font-bold text-green-600">
                    {(stats.dedupRatio * 100).toFixed(2)}%
                  </p>
                </div>
                <Zap className="text-green-600" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Storage Saved</p>
                  <p className="text-3xl font-bold text-orange-600">
                    {formatBytes(stats.storageSaved)}
                  </p>
                </div>
                <TrendingUp className="text-orange-600" size={32} />
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Panel - List View */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-lg border border-gray-200">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Share2 className="text-blue-600" size={24} />
                  {viewMode === 'atoms' && 'Top Shared Chunks'}
                  {viewMode === 'files' && 'Recent Files'}
                  {viewMode === 'network' && 'Network Graph'}
                </h2>

                {viewMode === 'atoms' && (
                  <div className="space-y-3">
                    {topAtoms.length === 0 ? (
                      <div className="text-center py-12 text-gray-500">
                        <Database size={48} className="mx-auto mb-4 opacity-30" />
                        <p>No atoms found</p>
                      </div>
                    ) : (
                      topAtoms.map((atom) => (
                        <div
                          key={atom.hash}
                          onClick={() => setSelectedNode(atom)}
                          className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <p className="font-mono text-sm text-gray-700 mb-1">
                                {formatHash(atom.hash)}
                              </p>
                              <div className="flex items-center gap-4 text-sm text-gray-600">
                                <span className="flex items-center gap-1">
                                  <Database size={14} />
                                  {formatBytes(atom.size)}
                                </span>
                                <span className="flex items-center gap-1">
                                  <Share2 size={14} />
                                  Used {atom.usageCount}x
                                </span>
                              </div>
                            </div>
                            <div className="text-right">
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {atom.usageCount > 5 ? 'Hot' : atom.usageCount > 2 ? 'Warm' : 'Cold'}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {viewMode === 'files' && (
                  <div className="text-center py-12 text-gray-500">
                    <FileText size={48} className="mx-auto mb-4 opacity-30" />
                    <p>File view coming soon</p>
                    <p className="text-sm mt-2">Will show all ingested files with metadata</p>
                  </div>
                )}

                {viewMode === 'network' && (
                  <div className="text-center py-12 text-gray-500">
                    <Share2 size={48} className="mx-auto mb-4 opacity-30" />
                    <p>Network visualization coming soon</p>
                    <p className="text-sm mt-2">Interactive graph of atoms and files</p>
                  </div>
                )}
              </div>
            </div>

            {/* Right Panel - Details View */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Details</h2>
                
                {selectedNode ? (
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Hash</label>
                      <p className="font-mono text-xs text-gray-800 break-all mt-1 p-2 bg-gray-50 rounded">
                        {'hash' in selectedNode ? selectedNode.hash : 'N/A'}
                      </p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-gray-600">Size</label>
                      <p className="text-lg font-semibold text-gray-900 mt-1">
                        {formatBytes(selectedNode.size)}
                      </p>
                    </div>

                    {'usageCount' in selectedNode && (
                      <div>
                        <label className="text-sm font-medium text-gray-600">Usage Count</label>
                        <p className="text-lg font-semibold text-gray-900 mt-1">
                          {selectedNode.usageCount} files
                        </p>
                        <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${Math.min(selectedNode.usageCount * 10, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    <div className="pt-4 border-t border-gray-200">
                      <label className="text-sm font-medium text-gray-600 mb-2 block">Actions</label>
                      <div className="space-y-2">
                        <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                          View Content
                        </button>
                        <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                          Show Connections
                        </button>
                        <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                          Export Data
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <p>Select a node to view details</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Stats Footer */}
          <div className="mt-6 bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Graph Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-2">Average Reuse Factor</p>
                <p className="text-2xl font-bold text-blue-600">
                  {stats.avgReuse.toFixed(3)}x
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Each atom is reused on average
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600 mb-2">Total Graph Size</p>
                <p className="text-2xl font-bold text-purple-600">
                  {formatBytes(stats.totalAtoms * 100)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Estimated total size
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600 mb-2">Efficiency Gain</p>
                <p className="text-2xl font-bold text-green-600">
                  {(stats.dedupRatio * 100).toFixed(2)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Space saved by deduplication
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
