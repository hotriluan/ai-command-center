/**
 * Data Import Component
 * Handles sales data and COGS imports with validation and error handling
 */

'use client';

import React, { useState, useRef } from 'react';
import { Upload, Loader2, AlertCircle, CheckCircle, Download, FileSpreadsheet, DollarSign, Target } from 'lucide-react';

interface ImportResult {
    status: 'success' | 'error' | 'info';
    message: string;
    rows_imported?: number;
    rows_updated?: number;
    report_path?: string;
    missing_count?: number;
}

const DataImportPage: React.FC = () => {
    // State management
    const [salesUploading, setSalesUploading] = useState(false);
    const [cogsUploading, setCogsUploading] = useState(false);
    const [targetUploading, setTargetUploading] = useState(false);
    const [salesResult, setSalesResult] = useState<ImportResult | null>(null);
    const [cogsResult, setCogsResult] = useState<ImportResult | null>(null);
    const [targetResult, setTargetResult] = useState<ImportResult | null>(null);

    // File input refs
    const salesFileRef = useRef<HTMLInputElement>(null);
    const cogsFileRef = useRef<HTMLInputElement>(null);
    const targetFileRef = useRef<HTMLInputElement>(null);

    /**
     * Handle Sales Data Import
     */
    const handleSalesImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
            setSalesResult({
                status: 'error',
                message: 'Please select an Excel file (.xlsx or .xls)'
            });
            return;
        }

        setSalesUploading(true);
        setSalesResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/import/sales', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                setSalesResult(result);
            } else {
                // Handle missing COGS error
                if (result.status === 'error' && result.report_path) {
                    setSalesResult(result);

                    // Auto-download missing COGS report
                    setTimeout(() => {
                        downloadMissingCogsReport();
                    }, 1000);
                } else {
                    setSalesResult({
                        status: 'error',
                        message: result.message || 'Import failed'
                    });
                }
            }
        } catch (error) {
            setSalesResult({
                status: 'error',
                message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        } finally {
            setSalesUploading(false);
            event.target.value = ''; // Reset input
        }
    };

    /**
     * Handle COGS Data Import
     */
    const handleCogsImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
            setCogsResult({
                status: 'error',
                message: 'Please select an Excel file (.xlsx or .xls)'
            });
            return;
        }

        setCogsUploading(true);
        setCogsResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/import/cogs', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                setCogsResult(result);
            } else {
                setCogsResult({
                    status: 'error',
                    message: result.message || 'COGS import failed'
                });
            }
        } catch (error) {
            setCogsResult({
                status: 'error',
                message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        } finally {
            setCogsUploading(false);
            event.target.value = ''; // Reset input
        }
    };

    /**
     * Handle Target Data Import
     */
    const handleTargetImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
            setTargetResult({
                status: 'error',
                message: 'Please select an Excel or CSV file (.xlsx, .xls, or .csv)'
            });
            return;
        }

        setTargetUploading(true);
        setTargetResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/upload-target', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                setTargetResult({
                    status: 'success',
                    message: result.message || `Successfully updated targets for ${result.rows_processed} records`,
                    rows_updated: result.rows_processed
                });
            } else {
                setTargetResult({
                    status: 'error',
                    message: result.error || 'Target import failed'
                });
            }
        } catch (error) {
            setTargetResult({
                status: 'error',
                message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        } finally {
            setTargetUploading(false);
            event.target.value = ''; // Reset input
        }
    };

    /**
     * Download missing COGS report
     */
    const downloadMissingCogsReport = () => {
        window.open('http://localhost:8000/api/download/missing-cogs-report', '_blank');
    };

    /**
     * Render alert message
     */
    const renderAlert = (result: ImportResult) => {
        const alertStyles = {
            success: 'bg-green-50 border-green-200 text-green-800',
            error: 'bg-red-50 border-red-200 text-red-800',
            info: 'bg-blue-50 border-blue-200 text-blue-800'
        };

        const icons = {
            success: <CheckCircle className="w-5 h-5 text-green-600" />,
            error: <AlertCircle className="w-5 h-5 text-red-600" />,
            info: <AlertCircle className="w-5 h-5 text-blue-600" />
        };

        return (
            <div className={`border rounded-lg p-4 flex items-start gap-3 ${alertStyles[result.status]}`}>
                {icons[result.status]}
                <div className="flex-1">
                    <p className="font-medium">{result.message}</p>
                    {result.rows_imported !== undefined && (
                        <p className="text-sm mt-1">Rows imported: {result.rows_imported}</p>
                    )}
                    {result.rows_updated !== undefined && (
                        <p className="text-sm mt-1">Rows updated: {result.rows_updated}</p>
                    )}
                    {result.missing_count !== undefined && (
                        <div className="mt-3">
                            <button
                                onClick={downloadMissingCogsReport}
                                className="flex items-center gap-2 bg-white text-red-700 border border-red-300 px-4 py-2 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium"
                            >
                                <Download className="w-4 h-4" />
                                Download Missing COGS Report
                            </button>
                            <p className="text-sm mt-2 text-red-700">
                                Please fill in the costs in the downloaded file and upload it in Section B below.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            <div className="container mx-auto px-6 py-8 max-w-5xl">
                {/* Header */}
                <header className="mb-10">
                    <div className="flex items-center gap-3 mb-2">
                        <FileSpreadsheet className="w-10 h-10 text-indigo-600" />
                        <h1 className="text-4xl font-bold text-gray-900 tracking-tight bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                            Data Management
                        </h1>
                    </div>
                    <p className="text-gray-600 font-medium">Import and manage your sales data and product costs</p>
                </header>

                {/* Section A: Import Sales Data */}
                <div className="bg-white rounded-xl shadow-lg p-8 mb-6 border border-gray-200">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-indigo-100 p-3 rounded-lg">
                            <Upload className="w-6 h-6 text-indigo-600" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">Upload Sales Records</h2>
                            <p className="text-gray-600 text-sm">Daily task: Import zrsd002 sales data</p>
                        </div>
                    </div>

                    {/* File Upload */}
                    <div className="mb-6">
                        <input
                            type="file"
                            ref={salesFileRef}
                            onChange={handleSalesImport}
                            accept=".xlsx,.xls"
                            className="hidden"
                        />
                        <button
                            onClick={() => salesFileRef.current?.click()}
                            disabled={salesUploading}
                            className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-8 py-4 rounded-lg shadow-md hover:shadow-xl transition-all text-lg font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {salesUploading ? (
                                <>
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                    Processing Sales Data...
                                </>
                            ) : (
                                <>
                                    <Upload className="w-6 h-6" />
                                    Upload Sales Data (.xlsx)
                                </>
                            )}
                        </button>
                    </div>

                    {/* Result Alert */}
                    {salesResult && renderAlert(salesResult)}

                    {/* Instructions */}
                    <div className="mt-6 bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <h3 className="font-semibold text-gray-900 mb-2">📋 Expected File Format:</h3>
                        <ul className="text-sm text-gray-700 space-y-1">
                            <li>• <strong>Billing Document</strong> - Invoice ID</li>
                            <li>• <strong>Billing Item</strong> - Line item ID</li>
                            <li>• <strong>Material</strong> - SKU/Material code</li>
                            <li>• <strong>Net Value</strong> - Revenue amount</li>
                            <li>• <strong>Salesman Name</strong> - Salesperson name</li>
                            <li>• <strong>Billing Date</strong> - Transaction date</li>
                        </ul>
                    </div>
                </div>

                {/* Section B: Update COGS */}
                <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-amber-100 p-3 rounded-lg">
                            <DollarSign className="w-6 h-6 text-amber-600" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">Update Product Costs (COGS)</h2>
                            <p className="text-gray-600 text-sm">Maintain accurate cost prices for profit calculation</p>
                        </div>
                    </div>

                    {/* File Upload */}
                    <div className="mb-6">
                        <input
                            type="file"
                            ref={cogsFileRef}
                            onChange={handleCogsImport}
                            accept=".xlsx,.xls"
                            className="hidden"
                        />
                        <button
                            onClick={() => cogsFileRef.current?.click()}
                            disabled={cogsUploading}
                            className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white px-8 py-4 rounded-lg shadow-md hover:shadow-xl transition-all text-lg font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {cogsUploading ? (
                                <>
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                    Updating Prices...
                                </>
                            ) : (
                                <>
                                    <DollarSign className="w-6 h-6" />
                                    Update COGS Prices (.xlsx)
                                </>
                            )}
                        </button>
                    </div>

                    {/* Result Alert */}
                    {cogsResult && renderAlert(cogsResult)}

                    {/* Instructions */}
                    <div className="mt-6 bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <h3 className="font-semibold text-gray-900 mb-2">📋 Expected File Format:</h3>
                        <ul className="text-sm text-gray-700 space-y-1">
                            <li>• <strong>Description</strong> - Product description (unique)</li>
                            <li>• <strong>COGS</strong> - Cost of goods sold</li>
                        </ul>
                        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-sm text-blue-800">
                                <strong>💡 Tip:</strong> After updating COGS, re-upload sales data to recalculate profits with the new costs.
                            </p>
                        </div>
                        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-sm text-green-800">
                                <strong>✅ Example:</strong> Use <code className="bg-white px-2 py-1 rounded">demodata/cogsupload.xlsx</code> as reference
                            </p>
                        </div>
                    </div>
                </div>

                {/* Section C: Upload Sales Targets */}
                <div className="bg-white rounded-xl shadow-lg p-8 mb-6 border border-gray-200">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-green-100 p-3 rounded-lg">
                            <Target className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">Upload Sales Targets</h2>
                            <p className="text-gray-600 text-sm">Set monthly goals for KPI tracking</p>
                        </div>
                    </div>

                    {/* File Upload */}
                    <div className="mb-6">
                        <input
                            type="file"
                            ref={targetFileRef}
                            onChange={handleTargetImport}
                            accept=".xlsx,.xls,.csv"
                            className="hidden"
                        />
                        <button
                            onClick={() => targetFileRef.current?.click()}
                            disabled={targetUploading}
                            className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white px-8 py-4 rounded-lg shadow-md hover:shadow-xl transition-all text-lg font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {targetUploading ? (
                                <>
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                    Processing Targets...
                                </>
                            ) : (
                                <>
                                    <Target className="w-6 h-6" />
                                    Upload Targets (.xlsx, .csv)
                                </>
                            )}
                        </button>
                    </div>

                    {/* Result Alert */}
                    {targetResult && renderAlert(targetResult)}

                    {/* Instructions */}
                    <div className="mt-6 bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <h3 className="font-semibold text-gray-900 mb-2">📋 Expected File Format:</h3>
                        <ul className="text-sm text-gray-700 space-y-1">
                            <li>• <strong>Salesman Name</strong> - Salesperson name</li>
                            <li>• <strong>Year</strong> - Target year (e.g., 2025)</li>
                            <li>• <strong>Semester</strong> - 1 or 2</li>
                            <li>• <strong>Target</strong> - Semester target amount</li>
                        </ul>
                        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-sm text-blue-800">
                                <strong>💡 Auto-Splitting:</strong> Semester targets are automatically divided into 6 monthly targets for precise tracking.
                            </p>
                        </div>
                        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-sm text-green-800">
                                <strong>✅ Example:</strong> Use <code className="bg-white px-2 py-1 rounded">demodata/targets.xlsx</code> as reference
                            </p>
                        </div>
                    </div>
                </div>

                {/* Back to Dashboard Link */}
                <div className="mt-8 text-center">
                    <a
                        href="/"
                        className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
                    >
                        ← Back to Dashboard
                    </a>
                </div>
            </div>
        </div>
    );
};

export default DataImportPage;
