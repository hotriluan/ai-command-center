import React, { useRef } from 'react';
import { Upload, Loader2, Target } from 'lucide-react';

interface UploadSectionProps {
    isUploading: boolean;
    isUploadingCOGS: boolean;
    isUploadingTarget: boolean;
    onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
    onCOGSUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
    onTargetUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({
    isUploading,
    isUploadingCOGS,
    isUploadingTarget,
    onFileUpload,
    onCOGSUpload,
    onTargetUpload
}) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const cogsFileInputRef = useRef<HTMLInputElement>(null);
    const targetFileInputRef = useRef<HTMLInputElement>(null);

    return (
        <div className="flex gap-3">
            {/* Sales Data Upload */}
            <input type="file" accept=".xlsx, .xls" ref={fileInputRef} onChange={onFileUpload} className="hidden" />
            <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg shadow-md hover:shadow-lg transition-all text-sm font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
                aria-label="Upload Excel data file"
            >
                {isUploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
                {isUploading ? 'Processing...' : '📊 Sales Data'}
            </button>

            {/* COGS Upload */}
            <input type="file" accept=".xlsx, .xls" ref={cogsFileInputRef} onChange={onCOGSUpload} className="hidden" />
            <button
                onClick={() => cogsFileInputRef.current?.click()}
                disabled={isUploadingCOGS}
                className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white px-5 py-3 rounded-lg shadow-md hover:shadow-lg transition-all text-sm font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
                aria-label="Upload COGS Master File"
                title="Upload Cost of Goods Sold master file for real profit calculation"
            >
                {isUploadingCOGS ? <Loader2 size={16} className="animate-spin" /> : '⚙️'}
                {isUploadingCOGS ? 'Uploading...' : 'COGS'}
            </button>

            {/* Target Upload */}
            <input type="file" accept=".xlsx, .xls, .csv" ref={targetFileInputRef} onChange={onTargetUpload} className="hidden" />
            <button
                onClick={() => targetFileInputRef.current?.click()}
                disabled={isUploadingTarget}
                className="flex items-center gap-2 bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 px-5 py-3 rounded-lg shadow-sm hover:shadow-md transition-all text-sm font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
                aria-label="Upload Sales Targets"
                title="Upload Sales Targets for KPI tracking"
            >
                {isUploadingTarget ? <Loader2 size={16} className="animate-spin" /> : <Target size={16} className="text-red-500" />}
                {isUploadingTarget ? 'Uploading...' : 'Targets'}
            </button>
        </div>
    );
};

export default UploadSection;
