import { useState, useCallback } from 'react';
import { Upload, File, Check, X, AlertCircle } from 'lucide-react';

interface UploadResult {
  filename: string;
  size: number;
  atoms_created: number;
  atoms_reused: number;
  dedup_ratio: number;
  storage_saved: number;
  hash: string;
  processing_time_ms: number;
}

interface AnalysisDetails {
  atoms: Array<{
    hash: string;
    size: number;
    is_new: boolean;
    reuse_count: number;
  }>;
}

export default function FileUploadAnalysis() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<UploadResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<UploadResult | null>(null);
  const [analysisDetails, setAnalysisDetails] = useState<AnalysisDetails | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...droppedFiles]);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadAndAnalyze = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);
    const newResults: UploadResult[] = [];

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:3000/api/files/analyze', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Failed to upload ${file.name}`);
        }

        const result: UploadResult = await response.json();
        newResults.push(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Upload failed');
        break;
      }
    }

    setResults(newResults);
    setFiles([]);
    setUploading(false);
  };

  const fetchAnalysisDetails = async (hash: string) => {
    try {
      const response = await fetch(
        `http://localhost:3000/api/files/${hash}/atoms`
      );
      if (!response.ok) throw new Error('Failed to fetch details');
      const data: AnalysisDetails = await response.json();
      setAnalysisDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load details');
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const totalSaved = results.reduce((sum, r) => sum + r.storage_saved, 0);
  const avgDedupRatio =
    results.length > 0
      ? results.reduce((sum, r) => sum + r.dedup_ratio, 0) / results.length
      : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📤 Upload & Analysis
          </h1>
          <p className="text-gray-600">
            Uploadez des fichiers et analysez leur décomposition en atomes
          </p>
        </div>

        {/* Upload Zone */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors cursor-pointer"
          >
            <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <p className="text-lg text-gray-700 mb-2">
              Glissez-déposez vos fichiers ici
            </p>
            <p className="text-sm text-gray-500 mb-4">ou</p>
            <label className="inline-block">
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
              />
              <span className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors">
                Sélectionner des fichiers
              </span>
            </label>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">
                Fichiers sélectionnés ({files.length})
              </h3>
              <div className="space-y-2 max-h-[200px] overflow-y-auto">
                {files.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center flex-1 min-w-0">
                      <File className="w-5 h-5 mr-3 text-gray-400 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 truncate">
                          {file.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatBytes(file.size)}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(idx)}
                      className="ml-4 p-1 hover:bg-gray-200 rounded transition-colors"
                    >
                      <X className="w-5 h-5 text-gray-500" />
                    </button>
                  </div>
                ))}
              </div>

              <button
                onClick={uploadAndAnalyze}
                disabled={uploading}
                className="mt-4 w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {uploading ? 'Upload en cours...' : `Analyser ${files.length} fichier(s)`}
              </button>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {results.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
              <div className="text-sm text-gray-600 mb-1">Fichiers Analysés</div>
              <div className="text-3xl font-bold text-gray-900">{results.length}</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
              <div className="text-sm text-gray-600 mb-1">Économie Totale</div>
              <div className="text-3xl font-bold text-green-600">
                {formatBytes(totalSaved)}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
              <div className="text-sm text-gray-600 mb-1">Dédup Moyenne</div>
              <div className="text-3xl font-bold text-purple-600">
                {(avgDedupRatio * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">📊 Résultats d'Analyse</h2>
            <div className="space-y-4">
              {results.map((result, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setSelectedResult(result);
                    fetchAnalysisDetails(result.hash);
                  }}
                  className={`p-6 border rounded-lg cursor-pointer transition-colors ${
                    selectedResult?.hash === result.hash
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      <File className="w-6 h-6 mr-3 text-gray-400" />
                      <div>
                        <div className="text-lg font-semibold text-gray-900">
                          {result.filename}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatBytes(result.size)} • {result.processing_time_ms}ms
                        </div>
                      </div>
                    </div>
                    <Check className="w-6 h-6 text-green-600" />
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="text-xs text-gray-600">Atomes Créés</div>
                      <div className="text-xl font-bold text-blue-600">
                        {result.atoms_created}
                      </div>
                    </div>
                    <div className="bg-green-50 p-3 rounded">
                      <div className="text-xs text-gray-600">Atomes Réutilisés</div>
                      <div className="text-xl font-bold text-green-600">
                        {result.atoms_reused}
                      </div>
                    </div>
                    <div className="bg-purple-50 p-3 rounded">
                      <div className="text-xs text-gray-600">Déduplication</div>
                      <div className="text-xl font-bold text-purple-600">
                        {(result.dedup_ratio * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="bg-yellow-50 p-3 rounded">
                      <div className="text-xs text-gray-600">Économie</div>
                      <div className="text-xl font-bold text-yellow-600">
                        {formatBytes(result.storage_saved)}
                      </div>
                    </div>
                  </div>

                  {selectedResult?.hash === result.hash && analysisDetails && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-3">
                        Détails des Atomes
                      </h3>
                      <div className="max-h-[300px] overflow-y-auto space-y-2">
                        {analysisDetails.atoms.map((atom, atomIdx) => (
                          <div
                            key={atomIdx}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded"
                          >
                            <code className="text-xs text-gray-700">
                              {atom.hash.substring(0, 16)}...
                            </code>
                            <div className="flex items-center gap-3">
                              <span className="text-xs text-gray-600">
                                {formatBytes(atom.size)}
                              </span>
                              {atom.is_new ? (
                                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                                  Nouveau
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                                  Réutilisé ({atom.reuse_count}x)
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
