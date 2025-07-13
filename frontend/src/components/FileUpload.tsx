import React, { useEffect, useState } from 'react';
import { uploadDocument } from '../services/api';

interface FileUploadProps {
    onUploadSuccess: () => void; // cb to refresh document list
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);    // Selected file
    const [uploading, setUploading] = useState<boolean>(false);            // Uploading state
    const [uploadProgress, setUploadProgress] = useState<number>(0);        // Upload progress %
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            setSelectedFile(event.target.files[0]);
            setError(null);
            setSuccess(null);
            setUploadProgress(0);
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError('Please select a file first.');
            return;
        }
        setUploading(true);
        setError(null);
        setSuccess(null);

        try {
            // API Call
            const response = await uploadDocument(selectedFile, (progressEvent) => {
                const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                setUploadProgress(percent);
            });
            setSuccess(`File "${selectedFile.name}" uploaded successfully!`);
            setSelectedFile(null);
            onUploadSuccess(); // document list refresh
        
        } catch (err: any) {
            console.error('Error uploading file:', err);
            setError(err.response?.data?.detail || 'Failed to upload file.');
        
        } finally {
            setUploading(false);
            setUploadProgress(0);
        }
    };

    useEffect(() => {
        if (success || error) {
            const timer = setTimeout(() => {
                setError(null);
                setSuccess(null);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [success, error]);

    return (
        <div className="file-upload">
            <input type="file" onChange={handleFileChange} accept=".pdf,.txt" disabled={uploading} />
            {selectedFile && <p>Selected: {selectedFile.name}</p>}
            <button onClick={handleUpload} disabled={!selectedFile || uploading}>
                {uploading ? `Uploading (${uploadProgress}%)` : 'Upload Document'}
            </button>

            {uploading && uploadProgress > 0 && uploadProgress < 100 && (
                <progress value={uploadProgress} max="100" />
            )}
            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}
        </div>
    );
};

export default FileUpload;