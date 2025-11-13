import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface DedupStats {
  total_files: number;
  total_size: number;
  total_atoms: number;
  unique_atoms: number;
  dedup_ratio: number;
  storage_saved: number;
  avg_reuse: number;
  top_atoms: Array<{
    hash: string;
    usage_count: number;
    size: number;
  }>;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function DeduplicationDashboard() {
  const [stats, setStats] = useState<DedupStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
    // Rafraîchir toutes les 5 secondes
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/dedup/stats');
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat().format(num);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading deduplication stats...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-red-600">Error: {error}</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">No data available</div>
      </div>
    );
  }

  // Données pour les graphiques
  const storageData = [
    {
      name: 'Stockage Brut',
      value: stats.total_size,
      color: '#FF8042',
    },
    {
      name: 'Après Dédup',
      value: stats.total_size * (1 - stats.dedup_ratio),
      color: '#00C49F',
    },
  ];

  const topAtomsData = stats.top_atoms.map((atom, idx) => ({
    name: `${atom.hash.substring(0, 8)}...`,
    count: atom.usage_count,
    size: atom.size,
  }));

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🔍 Déduplication Dashboard
          </h1>
          <p className="text-gray-600">
            Analyse en temps réel de la déduplication et réutilisation des atomes
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Files */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <div className="text-sm text-gray-600 mb-1">Fichiers Totaux</div>
            <div className="text-3xl font-bold text-gray-900">
              {formatNumber(stats.total_files)}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {formatBytes(stats.total_size)}
            </div>
          </div>

          {/* Dedup Ratio */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <div className="text-sm text-gray-600 mb-1">Taux Déduplication</div>
            <div className="text-3xl font-bold text-green-600">
              {(stats.dedup_ratio * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {formatBytes(stats.storage_saved)} économisés
            </div>
          </div>

          {/* Atoms */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
            <div className="text-sm text-gray-600 mb-1">Atomes</div>
            <div className="text-3xl font-bold text-gray-900">
              {formatNumber(stats.unique_atoms)}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {formatNumber(stats.total_atoms)} total
            </div>
          </div>

          {/* Avg Reuse */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <div className="text-sm text-gray-600 mb-1">Réutilisation Moy.</div>
            <div className="text-3xl font-bold text-gray-900">
              {stats.avg_reuse.toFixed(2)}x
            </div>
            <div className="text-xs text-gray-500 mt-2">
              par atome
            </div>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Storage Comparison */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              💾 Économie de Stockage
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={storageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis tickFormatter={(value) => formatBytes(value)} />
                <Tooltip
                  formatter={(value: number) => formatBytes(value)}
                  labelStyle={{ color: '#000' }}
                />
                <Bar dataKey="value" fill="#8884d8">
                  {storageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                -{formatBytes(stats.storage_saved)}
              </div>
              <div className="text-sm text-gray-600">
                ({(stats.dedup_ratio * 100).toFixed(1)}% d'économie)
              </div>
            </div>
          </div>

          {/* Dedup Ratio Pie */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              ♻️  Distribution des Atomes
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    {
                      name: 'Atomes Uniques',
                      value: stats.unique_atoms,
                      color: '#0088FE',
                    },
                    {
                      name: 'Atomes Réutilisés',
                      value: stats.total_atoms - stats.unique_atoms,
                      color: '#00C49F',
                    },
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${formatNumber(entry.value)}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {[0, 1].map((index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={index === 0 ? '#0088FE' : '#00C49F'}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatNumber(value)} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 text-center text-sm text-gray-600">
              Ratio déduplication: {(stats.dedup_ratio * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Top Atoms Table */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">
            🏆 Top 10 Atomes les Plus Réutilisés
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rang
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hash
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Utilisations
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Taille
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Économie Totale
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats.top_atoms.slice(0, 10).map((atom, idx) => (
                  <tr key={atom.hash} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      #{idx + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
                        {atom.hash.substring(0, 16)}...
                      </code>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {atom.usage_count}x
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatBytes(atom.size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                      {formatBytes(atom.size * (atom.usage_count - 1))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Atoms Chart */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h2 className="text-xl font-semibold mb-4">
            📊 Réutilisation des Top Atomes
          </h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={topAtomsData.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                formatter={(value: number, name: string) =>
                  name === 'count'
                    ? [`${value} utilisations`, 'Utilisations']
                    : [formatBytes(value), 'Taille']
                }
              />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" name="Utilisations" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Auto-refresh indicator */}
        <div className="mt-6 text-center text-sm text-gray-500">
          🔄 Rafraîchissement automatique toutes les 5 secondes
        </div>
      </div>
    </div>
  );
}
