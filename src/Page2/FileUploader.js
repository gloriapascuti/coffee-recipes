import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from './styles/FileUploader.module.css';

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

function FileUploader() {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('idle');
    const [lastOperation, setLastOperation] = useState('upload'); // 'upload' or 'delete'
    const [filesList, setFilesList] = useState([]);

    function handleFileChange(event) {
        if (event.target.files) {
            setFile(event.target.files[0]);
        }
    }

    async function handleFileUpload() {
        if (!file) return;

        setStatus('uploading');
        setLastOperation('upload');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const accessToken = localStorage.getItem('access_token');
            const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
                },
            });
            if (response.status === 201) {
                setStatus('success');
                setFile(null); // Clear the file input after successful upload
                fetchFiles();
                // Reset the file input
                const fileInput = document.querySelector('input[type="file"]');
                if (fileInput) fileInput.value = '';
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
            const accessToken = localStorage.getItem('access_token');
            const response = await axios.get('http://127.0.0.1:8000/api/upload/', {
                headers: {
                    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
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

    const handleDownload = (fileName) => {
        const link = document.createElement('a');
        link.href = `http://127.0.0.1:8000/media/uploads/${fileName}`;
        link.download = fileName;
        link.click();
    };

    const handleDelete = async (fileName) => {
        if (!window.confirm(`Are you sure you want to delete "${fileName}"?`)) {
            return;
        }

        try {
            const accessToken = localStorage.getItem('access_token');
            console.log('Attempting to delete file:', fileName);
            console.log('Access token present:', !!accessToken);
            
            if (!accessToken) {
                alert('You must be logged in to delete files. Please log in and try again.');
                setStatus('error');
                return;
            }
            
            const response = await axios.delete(`http://127.0.0.1:8000/api/upload/${encodeURIComponent(fileName)}/`, {
                headers: {
                    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
                }
            });
            
            console.log('Delete response:', response);
            
            if (response.status === 200 || response.status === 204) {
                // Remove the file from the list immediately
                setFilesList(prevFiles => prevFiles.filter(file => file !== fileName));
                setLastOperation('delete');
                setStatus('success');
                console.log('File deleted successfully');
            } else {
                console.log('Unexpected response status:', response.status);
                setStatus('error');
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            console.error('Error response:', error.response?.data);
            console.error('Error status:', error.response?.status);
            
            if (error.response?.status === 401) {
                alert('Authentication failed. Please log in again and try to delete the file.');
            } else if (error.response?.status === 404) {
                alert('File not found. It may have already been deleted.');
                // Remove from list anyway since it doesn't exist
                setFilesList(prevFiles => prevFiles.filter(file => file !== fileName));
                setLastOperation('delete');
                setStatus('success');
            } else {
                alert(`Failed to delete file: ${error.response?.data?.error || error.message}`);
            }
            
            setStatus('error');
        }
    };

    const getFileIcon = (fileName) => {
        const extension = fileName.split('.').pop()?.toLowerCase();
        switch (extension) {
            case 'pdf': return '📄';
            case 'jpg':
            case 'jpeg':
            case 'png':
            case 'gif': return '🖼️';
            case 'mp4':
            case 'avi':
            case 'mov': return '🎥';
            case 'mp3':
            case 'wav': return '🎵';
            case 'doc':
            case 'docx': return '📝';
            case 'xls':
            case 'xlsx': return '📊';
            default: return '📎';
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className={styles.container}>
            {/* Upload Section */}
            <div className={styles.uploadSection}>
                <h2 className={styles.uploadTitle}>
                    <span className={styles.uploadIcon}>☁️</span>
                    Upload Your Files
                </h2>
                
                <input
                    className={styles.fileInput}
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mov,.mp3,.wav,.doc,.docx,.xls,.xlsx"
                />
                
                {file && (
                    <div className={styles.fileInfo}>
                        <div className={styles.fileInfoTitle}>
                            <span>{getFileIcon(file.name)}</span>
                            Selected File Details
                        </div>
                        <div className={styles.fileInfoItem}>
                            <span className={styles.fileInfoLabel}>Name:</span>
                            <span>{file.name}</span>
                        </div>
                        <div className={styles.fileInfoItem}>
                            <span className={styles.fileInfoLabel}>Size:</span>
                            <span>{formatFileSize(file.size)}</span>
                        </div>
                        <div className={styles.fileInfoItem}>
                            <span className={styles.fileInfoLabel}>Type:</span>
                            <span>{file.type || 'Unknown'}</span>
                        </div>
                    </div>
                )}

                {file && (
                    <button 
                        className={styles.uploadButton} 
                        onClick={handleFileUpload}
                        disabled={status === 'uploading'}
                    >
                        {status === 'uploading' ? (
                            <>
                                <span className={styles.loadingSpinner}></span>
                                Uploading...
                            </>
                        ) : (
                            <>
                                <span>📤</span>
                                Upload File
                            </>
                        )}
                    </button>
                )}

                {/* Status Messages */}
                {status === 'uploading' && (
                    <div className={`${styles.statusMessage} ${styles.uploadingMessage}`}>
                        <span className={styles.loadingSpinner}></span>
                        Uploading your file...
                    </div>
                )}

                {status === 'success' && (
                    <div className={`${styles.statusMessage} ${styles.successMessage}`}>
                        <span>✅</span>
                        {lastOperation === 'upload' ? 'File uploaded successfully!' : 'File deleted successfully!'}
                    </div>
                )}

                {status === 'error' && (
                    <div className={`${styles.statusMessage} ${styles.errorMessage}`}>
                        <span>❌</span>
                        {lastOperation === 'upload' ? 'Upload failed. Please try again.' : 'Delete failed. Please try again.'}
                    </div>
                )}
            </div>

            {/* Files Section */}
            <div className={styles.filesSection}>
                <h3 className={styles.filesTitle}>
                    <span>📁</span>
                    Your Uploaded Files
                </h3>
                
                {filesList.length > 0 ? (
                    <ul className={styles.filesList}>
                        {filesList.map((fileName, index) => (
                            <li key={index} className={styles.fileItem}>
                                <div className={styles.fileName}>
                                    <span>{getFileIcon(fileName)}</span>
                                    {fileName}
                                </div>
                                <div className={styles.fileActions}>
                                    <button
                                        onClick={() => handleDownload(fileName)}
                                        className={styles.downloadButton}
                                        title="Download file"
                                    >
                                        <span>📥</span>
                                        Download
                                    </button>
                                    <button
                                        onClick={() => handleDelete(fileName)}
                                        className={styles.deleteButton}
                                        title="Delete file"
                                    >
                                        <span>✕</span>
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <div className={styles.emptyState}>
                        <div className={styles.emptyStateIcon}>📂</div>
                        <div className={styles.emptyStateText}>
                            No files uploaded yet. Upload your first file above!
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default FileUploader;
