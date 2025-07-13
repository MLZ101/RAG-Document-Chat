import React from 'react';
import { deleteDocument as deleteDocumentApi } from '../services/api';
import { Document } from '../types';

interface DocumentListProps {
    documents: Document[];
    setDocuments: React.Dispatch<React.SetStateAction<Document[]>>;
    onDocumentSelect: (fileId: string | null) => void;
    selectedDocumentId: string | null;
    fetchDocuments: () => Promise<void>;
}

const DocumentList: React.FC<DocumentListProps> = ({
    documents,
    setDocuments,
    onDocumentSelect,
    selectedDocumentId,
    fetchDocuments,
}) => {

    const handleDelete = async (fileId: string) => {
        if (window.confirm('Are you sure you want to delete this document?')) {
            try {
                await deleteDocumentApi(fileId);
                setDocuments(prevDocs => prevDocs.filter(doc => doc.id !== fileId));
                if (selectedDocumentId === fileId) {
                    onDocumentSelect(null);
                }
            } catch (err: any) {
                console.error('Error deleting document:', err);
                alert(err.response?.data?.detail || 'Failed to delete document.');
            }
        }
    };

    return (
        <div className="document-list">
            {documents.length === 0 ? (
                <p>No documents uploaded yet.</p>
            ) : (
                <ul>
                    {documents.map((doc) => (
                        <li
                            key={doc.id}
                            className={selectedDocumentId === doc.id ? 'selected' : ''}
                            onClick={() => onDocumentSelect(doc.id)}
                        >
                            <span>{doc.filename}</span>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleDelete(doc.id);
                                }}
                                title="Delete Document"
                            >
                                X
                            </button>
                        </li>
                    ))}
                </ul>
            )}
            <button onClick={fetchDocuments} className="refresh-button">Refresh List</button>
        </div>
    );
};

export default DocumentList;
