import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import type { StatsResponse, TimelineEvent } from '@/types/api';
import { 
  BarChart3, 
  Database, 
  FileText, 
  GitBranch,
  Layers,
  HardDrive,
  Files,
  Boxes,
  Percent,
  TrendingUp
} from 'lucide-react';
import { TimelineViewer } from '@/components/TimelineViewer';

interface DedupStats {
  total_files: number;
  total_size: number;
  total_chunks: number;
  unique_chunks: number;
  dedup_ratio: number;
  storage_saved: number;
  avg_reuse: number;
}

export function Dashboard() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [dedupStats, setDedupStats] = useState<DedupStats | null>(null);
  const [recentEvents, setRecentEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        
        // Fetch dedup stats
        const dedupResponse = await fetch('http://localhost:3000/api/dedup/stats');
        const dedupData = await dedupResponse.json();
        setDedupStats(dedupData);
        
        // Fetch regular stats and timeline
        const [statsData, timelineData] = await Promise.all([
          apiClient.getStats(),
          apiClient.getTimeline(),
        ]);
        
        setStats(statsData);
        setRecentEvents(timelineData.events.slice(0, 10));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-panini-blue"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
        <h2 className="text-red-400 font-semibold mb-2">Error loading dashboard</h2>
        <p className="text-red-300">{error}</p>
        <p className="text-sm text-gray-400 mt-4">
          Make sure the API server is running on <code>http://localhost:3000</code>
        </p>
      </div>
    );
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const dedupRatio = stats
    ? (stats.dedup_savings / (stats.total_size + stats.dedup_savings)) * 100
    : 0;

  const avgChunksPerFile = dedupStats && dedupStats.total_files > 0
    ? (dedupStats.total_chunks / dedupStats.total_files).toFixed(2)
    : '0';

  return (
    <div className="space-y-8">
      {/* Filesystem Stats Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4">📊 Filesystem Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Files */}
          <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 rounded-lg p-6 border border-blue-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-300 text-sm font-medium">Total Files</p>
                <p className="text-4xl font-bold text-white mt-2">
                  {dedupStats?.total_files?.toLocaleString() || 0}
                </p>
                <p className="text-xs text-blue-400 mt-1">in filesystem</p>
              </div>
              <Files className="w-14 h-14 text-blue-400 opacity-40" />
            </div>
          </div>

          {/* Total Chunks */}
          <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 rounded-lg p-6 border border-purple-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm font-medium">Total Chunks</p>
                <p className="text-4xl font-bold text-white mt-2">
                  {dedupStats?.total_chunks?.toLocaleString() || 0}
                </p>
                <p className="text-xs text-purple-400 mt-1">
                  {dedupStats?.unique_chunks?.toLocaleString() || 0} unique
                </p>
              </div>
              <Boxes className="w-14 h-14 text-purple-400 opacity-40" />
            </div>
          </div>

          {/* Avg Chunks per File */}
          <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 rounded-lg p-6 border border-green-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-300 text-sm font-medium">Avg Chunks/File</p>
                <p className="text-4xl font-bold text-white mt-2">
                  {avgChunksPerFile}
                </p>
                <p className="text-xs text-green-400 mt-1">chunks per file</p>
              </div>
              <TrendingUp className="w-14 h-14 text-green-400 opacity-40" />
            </div>
          </div>

          {/* Dedup Ratio */}
          <div className="bg-gradient-to-br from-cyan-900/30 to-cyan-800/20 rounded-lg p-6 border border-cyan-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-cyan-300 text-sm font-medium">Dedup Ratio</p>
                <p className="text-4xl font-bold text-white mt-2">
                  {dedupStats?.dedup_ratio?.toFixed(1) || 0}%
                </p>
                <p className="text-xs text-cyan-400 mt-1">
                  {formatBytes(dedupStats?.storage_saved || 0)} saved
                </p>
              </div>
              <Percent className="w-14 h-14 text-cyan-400 opacity-40" />
            </div>
          </div>
        </div>
      </div>

      {/* System Overview */}
      <div>
        <h2 className="text-2xl font-bold mb-4">🖥️ System Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Total Concepts */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Concepts</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats?.total_concepts || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">semantic entities</p>
              </div>
              <FileText className="w-12 h-12 text-panini-blue opacity-50" />
            </div>
          </div>

          {/* Total Versions */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Versions</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats?.total_versions || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">temporal versions</p>
              </div>
              <GitBranch className="w-12 h-12 text-panini-purple opacity-50" />
            </div>
          </div>

          {/* Total Snapshots */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Snapshots</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats?.total_snapshots || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">time points</p>
              </div>
              <Layers className="w-12 h-12 text-green-500 opacity-50" />
            </div>
          </div>

          {/* Storage Size */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Storage Size</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {dedupStats ? formatBytes(dedupStats.total_size) : '0 B'}
                </p>
                <p className="text-xs text-gray-500 mt-1">on disk</p>
              </div>
              <HardDrive className="w-12 h-12 text-orange-500 opacity-50" />
            </div>
          </div>

          {/* Avg Reuse */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Avg Chunk Reuse</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {dedupStats?.avg_reuse?.toFixed(2) || 0}x
                </p>
                <p className="text-xs text-gray-500 mt-1">reuse factor</p>
              </div>
              <Database className="w-12 h-12 text-yellow-500 opacity-50" />
            </div>
          </div>

          {/* Legacy Dedup */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Legacy Dedup</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {dedupRatio.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats ? formatBytes(stats.dedup_savings) : '0 B'}
                </p>
              </div>
              <BarChart3 className="w-12 h-12 text-cyan-500 opacity-50" />
            </div>
          </div>
        </div>
      </div>

      {/* Timeline Viewer */}
      <div>
        <h2 className="text-2xl font-bold mb-4">📅 Recent Activity</h2>
        <TimelineViewer events={recentEvents} />
      </div>
    </div>
  );
}
