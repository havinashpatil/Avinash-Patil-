/**
 * File Upload Component
 * Modern drag-and-drop interface with multi-file support
 */
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt, FaImage, FaTimes } from 'react-icons/fa';

const UploadZone = ({ onUpload, loading, mode = 'single' }) => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [previews, setPreviews] = useState([]);

    const onDrop = useCallback((acceptedFiles) => {
        if (mode === 'single') {
            // Single file mode - replace any existing file
            setSelectedFiles([acceptedFiles[0]]);

            // Generate preview
            const reader = new FileReader();
            reader.onload = (e) => {
                setPreviews([{ file: acceptedFiles[0], url: e.target.result }]);
            };
            reader.readAsDataURL(acceptedFiles[0]);
        } else {
            // Multi-file mode - add to existing
            setSelectedFiles((prev) => [...prev, ...acceptedFiles]);

            // Generate previews
            acceptedFiles.forEach((file) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    setPreviews((prev) => [...prev, { file, url: e.target.result }]);
                };
                reader.readAsDataURL(file);
            });
        }
    }, [mode]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpg', '.jpeg', '.png']
        },
        multiple: mode === 'batch'
    });

    const removeFile = (index) => {
        setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
        setPreviews((prev) => prev.filter((_, i) => i !== index));
    };

    const handleUpload = () => {
        if (selectedFiles.length > 0) {
            if (mode === 'single') {
                onUpload(selectedFiles[0]);
            } else {
                onUpload(selectedFiles);
            }
        }
    };

    return (
        <div className="space-y-6">
            {/* Drop Zone */}
            <div
                {...getRootProps()}
                className={`${isDragActive ? 'upload-zone-active' : 'upload-zone'}`}
            >
                <input {...getInputProps()} />
                <FaCloudUploadAlt className="text-6xl text-primary-400 mx-auto mb-4" />
                {isDragActive ? (
                    <p className="text-lg font-medium text-primary-600">
                        Drop the {mode === 'batch' ? 'images' : 'image'} here...
                    </p>
                ) : (
                    <div className="text-center">
                        <p className="text-lg font-medium text-neutral-700 mb-2">
                            Click to upload or drag and drop
                        </p>
                        <p className="text-sm text-neutral-500">
                            {mode === 'batch' ? 'Multiple images' : 'Single image'} (JPG, JPEG, PNG)
                        </p>
                    </div>
                )}
            </div>

            {/* File Previews */}
            {previews.length > 0 && (
                <div className="glass-card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-neutral-800">
                            Selected {mode === 'batch' ? 'Images' : 'Image'} ({previews.length})
                        </h3>
                        <button
                            onClick={() => {
                                setSelectedFiles([]);
                                setPreviews([]);
                            }}
                            className="text-sm text-danger-600 hover:text-danger-700 font-medium"
                        >
                            Clear All
                        </button>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {previews.map((preview, index) => (
                            <div key={index} className="relative group">
                                <div className="aspect-square rounded-lg overflow-hidden bg-neutral-100">
                                    <img
                                        src={preview.url}
                                        alt={`Preview ${index + 1}`}
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                                <button
                                    onClick={() => removeFile(index)}
                                    className="absolute top-2 right-2 w-8 h-8 bg-danger-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg hover:bg-danger-600"
                                >
                                    <FaTimes />
                                </button>
                                <p variant="caption" className="text-xs text-neutral-600 mt-2 truncate">
                                    {preview.file.name}
                                </p>
                            </div>
                        ))}
                    </div>

                    <button
                        onClick={handleUpload}
                        disabled={loading || selectedFiles.length === 0}
                        className="btn-primary w-full mt-6"
                    >
                        {loading ? (
                            <span className="flex items-center justify-center gap-2">
                                <span className="spinner"></span>
                                Processing...
                            </span>
                        ) : (
                            <span className="flex items-center justify-center gap-2">
                                <FaImage />
                                Analyze {mode === 'batch' ? `${selectedFiles.length} Images` : 'Image'}
                            </span>
                        )}
                    </button>
                </div>
            )}
        </div>
    );
};

export default UploadZone;
