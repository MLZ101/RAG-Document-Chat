import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// --- Document Endpoints ---

export const uploadDocument = async (file: File, onUploadProgress?: (progressEvent: any) => void) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload-doc', formData, {
        headers: {
            'Content-Type': 'multipart/form-data', // for file uploads
        },
        onUploadProgress, // Pass progress callback
    });
    return response.data;
};

export const getDocuments = async () => {
    const response = await api.get('/documents');
    return response.data;
};

export const deleteDocument = async (fileId: string) => {
    const response = await api.delete(`/documents/${fileId}`);
    return response.data;
};

// --- Chat Endpoint ---

export const sendMessageToChat = async (message: string, documentId: string | null = null) => {
    const payload: { query: string; file_id?: string } = { query: message };
    if (documentId) {
        payload.file_id = documentId;
    }
    const response = await api.post('/chat', payload);
    return response.data;
};

export default api;