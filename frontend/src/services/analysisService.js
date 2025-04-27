import axios from 'axios';
import config from '../config';

const API_BASE_URL = config.API.BASE_URL;

const analysisService = {
    // 创建会话
    async createSession(sessionName) {
        const response = await axios.post(`${API_BASE_URL}/sessions`, { session_name: sessionName });
        return response.data;
    },

    // 上传文件
    async uploadFile(sessionId, file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post(
            `${API_BASE_URL}/upload/${sessionId}`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        return response.data;
    },

    // 执行分析
    async analyze(query, sessionId) {
        const response = await axios.post(`${API_BASE_URL}/analyze`, {
            query,
            session_id: sessionId
        });
        return response.data;
    },

    // 获取会话数据
    async getSessionData(sessionId) {
        const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}`);
        return response.data;
    },

    // 获取分析历史
    async getAnalysisHistory(sessionId) {
        const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}/history`);
        return response.data;
    },

    // 下载分析结果
    async downloadResult(sessionId, resultId) {
        const response = await axios.get(
            `${API_BASE_URL}/download/${sessionId}/${resultId}`,
            { responseType: 'blob' }
        );
        return response.data;
    }
};

export default analysisService; 