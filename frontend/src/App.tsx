import React, { useState, useEffect } from 'react';
import './App.css'; 
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import { Document } from './types';
import { getDocuments } from './services/api';

const App: React.FC = () => {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchDocuments = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getDocuments();
            setDocuments(data);
        
        } catch (err: any) {
            console.error('Error fetching documents:', err);
            setError(err.response?.data?.detail || 'Failed to fetch documents.');
        
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <img src={"/assets/logo.png"} alt="logo" />
                <h1>Document Chat</h1>
            </header>
            <main className="App-main">
                <div className="sidebar">
                    <h2>Upload Documents</h2>
                    <FileUpload onUploadSuccess={fetchDocuments} />
                    <h2>Your Documents</h2>
                    <DocumentList
                        documents={documents}
                        setDocuments={setDocuments}
                        onDocumentSelect={setSelectedDocumentId}
                        selectedDocumentId={selectedDocumentId}
                        fetchDocuments={fetchDocuments}
                    />
                </div>
                <div className="chat-section">
                    <h2>Chat with your Documents</h2>
                    <ChatInterface selectedDocumentId={selectedDocumentId} />
                </div>
            </main>
        </div>
    );
};

export default App;