import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from './styles/FileUploader.module.css';

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

function FileUploader() {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('idle');
    const [filesList, setFilesList] = useState([]);

    function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
        if (event.target.files) {
            setFile(event.target.files[0]);
        }
    }

    async function handleFileUpload() {
        if (!file) return;

        setStatus('uploading');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    ...(token ? { Authorization: `Token ${token}` } : {})
                },
            });
            if (response.status === 201) {
                setStatus('success');
                fetchFiles();
            } else {
                setStatus('error');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            setStatus('error');
        }
    }

    async function fetchFiles() {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://127.0.0.1:8000/api/upload/', {
                headers: {
                    ...(token ? { Authorization: `Token ${token}` } : {})
                }
            });
            if (response.data && response.data.files) {
                setFilesList(response.data.files);
            } else {
                console.error("Unexpected response format:", response.data);
            }
        } catch (error) {
            console.error('Error fetching files:', error);
        }
    }

    useEffect(() => {
        fetchFiles();
    }, []);

    const handleDownload = (fileName: string) => {
        const link = document.createElement('a');
        link.href = `http://127.0.0.1:8000/media/uploads/${fileName}`;
        link.download = fileName;
        link.click();
    };

    return (
        <div className={styles.container}>
            <input
                className={styles.uploading}
                type="file"
                onChange={handleFileChange}
            />
            {file && (
                <div className="mb-2 text-sm">
                    <p>File name: {file.name}</p>
                    <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
                    <p>Type: {file.type}</p>
                </div>
            )}

            {file && status !== 'uploading' && (
                <button className={styles.uploading} onClick={handleFileUpload}>
                    Upload
                </button>
            )}

            {status === 'success' && (
                <p className="text-sm text-green-600">File uploaded successfully!</p>
            )}

            {status === 'error' && (
                <p className="text-sm text-red-600">Upload failed. Please try again.</p>
            )}

            <div>
                <h3 className={styles.uploadedFiles}>Uploaded Files</h3>
                <ul>
                    {filesList.length > 0 ? (
                        filesList.map((file, index) => (
                            <li key={index}>
                                <button
                                    onClick={() => handleDownload(file)}
                                    className={styles.link}
                                >
                                    {file} - Download
                                </button>
                            </li>
                        ))
                    ) : (
                        <p>No files uploaded yet.</p>
                    )}
                </ul>
            </div>
        </div>
    );
}

export default FileUploader;
