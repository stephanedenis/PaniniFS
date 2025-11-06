import { useState, useEffect } from 'react';
import {
  Brain,
  Search,
  Filter,
  TrendingUp,
  Users,
  MapPin,
  Building2,
  Tag,
  Calendar,
  Network,
  Sparkles,
  BarChart3,
  Play,
  RefreshCw
} from 'lucide-react';

interface Concept {
  id: string;
  canonical_name: string;
  concept_type: string;
  entity_subtype?: string;
  versions: ConceptVersion[];
  source_chunks: string[];
  confidence: number;
  created_at: number;
}

interface ConceptVersion {
  version_id: string;
  text: string;
  language: string;
  source_chunk: string;
  timestamp: number;
  confidence: number;
  context?: string;
}

interface ConceptStats {
  total_concepts: number;
  by_type: Record<string, number>;
  avg_confidence: number;
  total_versions: number;
}

export function ConceptsExplorer() {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [stats, setStats] = useState<ConceptStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/concepts/stats');
      const data = await response.json();
      if (data.success) {
        setStats(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const fetchConcepts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:3000/api/concepts/list');
      const data = await response.json();
      if (data.success) {
        setConcepts(data.data.concepts);
      }
    } catch (err) {
      console.error('Failed to fetch concepts:', err);
    } finally {
      setLoading(false);
    }
  };

  const startExtraction = async () => {
    try {
      setExtracting(true);
      const response = await fetch('http://localhost:3000/api/concepts/extract', {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        alert(`Extraction started! Job ID: ${data.data.job_id}`);
        // Refresh after extraction
        setTimeout(() => {
          fetchStats();
          fetchConcepts();
          setExtracting(false);
        }, 2000);
      }
    } catch (err) {
      console.error('Failed to start extraction:', err);
      setExtracting(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchConcepts();
  }, []);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'NamedEntity':
        return <Users className="w-5 h-5" />;
      case 'TechnicalTerm':
        return <Sparkles className="w-5 h-5" />;
      case 'Category':
        return <Tag className="w-5 h-5" />;
      case 'Event':
        return <Calendar className="w-5 h-5" />;
      case 'Relation':
        return <Network className="w-5 h-5" />;
      default:
        return <Brain className="w-5 h-5" />;
    }
  };

  const getEntityIcon = (subtype?: string) => {
    switch (subtype) {
      case 'Person':
        return <Users className="w-4 h-4" />;
      case 'Organization':
        return <Building2 className="w-4 h-4" />;
      case 'Location':
        return <MapPin className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const filteredConcepts = concepts.filter(concept => {
    const matchesSearch = concept.canonical_name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || concept.concept_type === filterType;
    return matchesSearch && matchesType;
  });

  const types = ['all', ...Object.keys(stats?.by_type || {})];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Brain className="w-8 h-8 text-purple-400" />
            Concept Explorer
          </h1>
          <p className="text-gray-400 mt-1">
            Semantic entities extracted from Wikipedia chunks
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchConcepts}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={startExtraction}
            disabled={extracting}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${extracting ? 'animate-pulse' : ''}`} />
            {extracting ? 'Extracting...' : 'Start Extraction'}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 rounded-lg p-6 border border-purple-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm font-medium">Total Concepts</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats.total_concepts.toLocaleString()}
                </p>
              </div>
              <Brain className="w-10 h-10 text-purple-400 opacity-40" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 rounded-lg p-6 border border-blue-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-300 text-sm font-medium">Total Versions</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats.total_versions.toLocaleString()}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-400 opacity-40" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 rounded-lg p-6 border border-green-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-300 text-sm font-medium">Avg Confidence</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {(stats.avg_confidence * 100).toFixed(1)}%
                </p>
              </div>
              <BarChart3 className="w-10 h-10 text-green-400 opacity-40" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-cyan-900/30 to-cyan-800/20 rounded-lg p-6 border border-cyan-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-cyan-300 text-sm font-medium">Concept Types</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {Object.keys(stats.by_type).length}
                </p>
              </div>
              <Filter className="w-10 h-10 text-cyan-400 opacity-40" />
            </div>
          </div>
        </div>
      )}

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search concepts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
        >
          {types.map((type) => (
            <option key={type} value={type}>
              {type === 'all' ? 'All Types' : type}
            </option>
          ))}
        </select>
      </div>

      {/* Concepts List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-2 flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          </div>
        ) : filteredConcepts.length === 0 ? (
          <div className="col-span-2 bg-gray-800 rounded-lg p-12 text-center">
            <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-300 mb-2">No Concepts Yet</h3>
            <p className="text-gray-400 mb-4">
              Start extraction to analyze chunks and extract semantic concepts
            </p>
            <button
              onClick={startExtraction}
              disabled={extracting}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg inline-flex items-center gap-2 transition-colors"
            >
              <Play className="w-5 h-5" />
              Start Extraction
            </button>
          </div>
        ) : (
          filteredConcepts.map((concept) => (
            <div
              key={concept.id}
              onClick={() => setSelectedConcept(concept)}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-purple-500 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-900/30 rounded-lg">
                    {getTypeIcon(concept.concept_type)}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {concept.canonical_name}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <span className="px-2 py-0.5 bg-purple-900/30 rounded">
                        {concept.concept_type}
                      </span>
                      {concept.entity_subtype && (
                        <span className="flex items-center gap-1 px-2 py-0.5 bg-blue-900/30 rounded">
                          {getEntityIcon(concept.entity_subtype)}
                          {concept.entity_subtype}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-400">Confidence</div>
                  <div className="text-lg font-bold text-green-400">
                    {(concept.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span>{concept.versions.length} versions</span>
                <span>•</span>
                <span>{concept.source_chunks.length} chunks</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Selected Concept Detail Modal */}
      {selectedConcept && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto border border-gray-700">
            <div className="p-6 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-2xl font-bold">{selectedConcept.canonical_name}</h2>
              <button
                onClick={() => setSelectedConcept(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">Versions</h3>
                <div className="space-y-2">
                  {selectedConcept.versions.map((version) => (
                    <div key={version.version_id} className="bg-gray-800 p-3 rounded">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-400">{version.language}</span>
                        <span className="text-sm font-mono text-purple-400">
                          {(version.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-white">{version.text}</p>
                      {version.context && (
                        <p className="text-sm text-gray-400 mt-1">{version.context}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Source Chunks</h3>
                <div className="space-y-1">
                  {selectedConcept.source_chunks.map((hash) => (
                    <div key={hash} className="font-mono text-sm text-gray-400 bg-gray-800 p-2 rounded">
                      {hash}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
