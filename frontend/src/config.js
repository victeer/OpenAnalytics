// 检查环境变量是否加载
const checkEnvVars = () => {
    const requiredVars = [
        'REACT_APP_API_HOST',
        'REACT_APP_API_PORT',
        'REACT_APP_API_BASE_PATH',
        'REACT_APP_BASE_PATH'
    ];

    const missingVars = requiredVars.filter(varName => !process.env[varName]);
    if (missingVars.length > 0) {
        console.error('缺少必要的环境变量:', missingVars);
        console.log('当前环境变量:', process.env);
    }
};

// 执行检查
checkEnvVars();

const config = {
    // API配置
    API: {
        HOST: process.env.REACT_APP_API_HOST || 'localhost',
        PORT: process.env.REACT_APP_API_PORT || '80',
        BASE_PATH: process.env.REACT_APP_API_BASE_PATH || '/op/api',
        // 完整的基础URL，由上面的配置组合而成
        get BASE_URL() {
            return `http://${this.HOST}:${this.PORT}${this.BASE_PATH}`;
        }
    },
    
    // 基础路径配置
    BASE_PATH: process.env.REACT_APP_BASE_PATH || '/',
    
    // 导航配置
    NAVIGATION: {
        // 根据环境设置不同的基础路径
        get BASE_PATH() {
            return process.env.NODE_ENV === 'production' ? '/analysis' : '/';
        },
        // 获取完整路径
        getPath(path) {
            return `${this.BASE_PATH}${path}`;
        }
    },
    
    // 文件上传配置
    MAX_FILE_SIZE: process.env.REACT_APP_MAX_FILE_SIZE || 100 * 1024 * 1024, // 100MB
    ALLOWED_FILE_TYPES: ['.csv', '.xlsx'],
    
    // 会话配置
    SESSION_TIMEOUT: process.env.REACT_APP_SESSION_TIMEOUT || 30 * 60 * 1000, // 30分钟
    
    // 重试配置
    MAX_RETRIES: 5,
    
    // 性能配置
    TABLE_RENDER_TIMEOUT: 500 // 500ms
};

export default config; 