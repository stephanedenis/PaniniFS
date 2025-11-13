import { useState, useEffect } from 'react';
import { Search, File, Hash, Database } from 'lucide-react';

interface Atom {
  hash: string;
  size: number;
  type: string;
  created_at: string;
  usage_count: number;
  files: string[];
}

interface AtomSearchResult {
  atoms: Atom[];
  total: number;
}

export default function AtomExplorer() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Atom[]>([]);
  const [selectedAtom, setSelectedAtom] = useState<Atom | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchAtoms = async (query: string) => {
    if (!query || query.length < 3) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:3000/api/atoms/search?q=${encodeURIComponent(query)}`
      );
      if (!response.ok) throw new Error('Search failed');
      const data: AtomSearchResult = await response.json();
      setSearchResults(data.atoms);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const fetchAtomDetails = async (hash: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:3000/api/atoms/${hash}`);
      if (!response.ok) throw new Error('Failed to fetch atom details');
      const data: Atom = await response.json();
      setSelectedAtom(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const debounce = setTimeout(() => {
      searchAtoms(searchQuery);
    }, 300);

    return () => clearTimeout(debounce);
  }, [searchQuery]);

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const formatDate = (dateStr: string): string => {
    return new Date(dateStr).toLocaleString('fr-FR');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🔍 Atom Explorer
          </h1>
          <p className="text-gray-600">
            Recherchez et explorez les atomes de contenu
          </p>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher par hash (min 3 caractères)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          {loading && (
            <div className="mt-2 text-sm text-gray-500">Recherche en cours...</div>
          )}
          {error && (
            <div className="mt-2 text-sm text-red-600">Erreur: {error}</div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Search Results */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Database className="w-5 h-5 mr-2" />
              Résultats ({searchResults.length})
            </h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {searchResults.length === 0 && searchQuery.length >= 3 && !loading && (
                <div className="text-center text-gray-500 py-8">
                  Aucun atome trouvé
                </div>
              )}
              {searchResults.length === 0 && searchQuery.length < 3 && (
                <div className="text-center text-gray-500 py-8">
                  Entrez au moins 3 caractères pour rechercher
                </div>
              )}
              {searchResults.map((atom) => (
                <div
                  key={atom.hash}
                  onClick={() => fetchAtomDetails(atom.hash)}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedAtom?.hash === atom.hash
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <Hash className="w-4 h-4 mr-2 text-gray-400" />
                        <code className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
                          {atom.hash.substring(0, 16)}...
                        </code>
                      </div>
                      <div className="text-sm text-gray-600">
                        Taille: {formatBytes(atom.size)}
                      </div>
                      <div className="text-sm text-gray-600">
                        Type: <span className="font-medium">{atom.type}</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {atom.usage_count}x
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Atom Details */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <File className="w-5 h-5 mr-2" />
              Détails de l'Atome
            </h2>
            {!selectedAtom && (
              <div className="text-center text-gray-500 py-8">
                Sélectionnez un atome pour voir les détails
              </div>
            )}
            {selectedAtom && (
              <div className="space-y-6">
                {/* Hash */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hash SHA256
                  </label>
                  <code className="block w-full p-3 bg-gray-50 rounded-lg text-xs font-mono break-all">
                    {selectedAtom.hash}
                  </code>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Taille</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {formatBytes(selectedAtom.size)}
                    </div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Utilisations</div>
                    <div className="text-2xl font-bold text-green-600">
                      {selectedAtom.usage_count}x
                    </div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Type</div>
                    <div className="text-xl font-bold text-purple-600">
                      {selectedAtom.type}
                    </div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Économie</div>
                    <div className="text-xl font-bold text-yellow-600">
                      {formatBytes(
                        selectedAtom.size * (selectedAtom.usage_count - 1)
                      )}
                    </div>
                  </div>
                </div>

                {/* Created */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Créé le
                  </label>
                  <div className="text-gray-900">
                    {formatDate(selectedAtom.created_at)}
                  </div>
                </div>

                {/* Files using this atom */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fichiers utilisant cet atome ({selectedAtom.files.length})
                  </label>
                  <div className="max-h-[300px] overflow-y-auto space-y-2">
                    {selectedAtom.files.map((file, idx) => (
                      <div
                        key={idx}
                        className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <File className="w-4 h-4 mr-2 text-gray-400 flex-shrink-0" />
                        <span className="text-sm text-gray-700 truncate" title={file}>
                          {file}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Impact Analysis */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    💡 Analyse d'Impact
                  </h3>
                  <ul className="text-sm text-gray-700 space-y-1">
                    <li>
                      • Cet atome est partagé par{' '}
                      <strong>{selectedAtom.files.length}</strong> fichiers
                    </li>
                    <li>
                      • Économie totale :{' '}
                      <strong className="text-green-600">
                        {formatBytes(
                          selectedAtom.size * (selectedAtom.usage_count - 1)
                        )}
                      </strong>
                    </li>
                    <li>
                      • Sans dédup :{' '}
                      {formatBytes(selectedAtom.size * selectedAtom.usage_count)}
                    </li>
                    <li>
                      • Avec dédup : {formatBytes(selectedAtom.size)} (
                      {(
                        ((selectedAtom.usage_count - 1) / selectedAtom.usage_count) *
                        100
                      ).toFixed(1)}
                      % d'économie)
                    </li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
