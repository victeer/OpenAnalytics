/**
 * 会话管理工具
 */

// 会话ID的LocalStorage键名
const SESSION_KEY = 'analysis_session_id';

/**
 * 从localStorage获取会话ID
 * @returns {string|null} 会话ID，不存在则返回null
 */
export const getSessionId = () => {
  return localStorage.getItem(SESSION_KEY);
};

/**
 * 保存会话ID到localStorage
 * @param {string} sessionId 要保存的会话ID
 */
export const saveSessionId = (sessionId) => {
  if (sessionId) {
    localStorage.setItem(SESSION_KEY, sessionId);
    console.log('会话ID已保存:', sessionId);
  }
};

/**
 * 清除保存的会话ID
 */
export const clearSessionId = () => {
  localStorage.removeItem(SESSION_KEY);
  console.log('会话ID已清除');
};

/**
 * 检查是否存在有效会话
 * @returns {boolean} 是否存在会话ID
 */
export const hasSession = () => {
  return !!getSessionId();
};

export default {
  getSessionId,
  saveSessionId,
  clearSessionId,
  hasSession
}; 