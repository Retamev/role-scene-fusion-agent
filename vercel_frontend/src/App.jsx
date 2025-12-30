import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [characterImage, setCharacterImage] = useState(null);
  const [referenceImage, setReferenceImage] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);

  const addLog = (message) => {
    setLogs(prev => [...prev, { id: Date.now(), message }]);
  };

  const handleImageUpload = (e, type) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      if (type === 'character') {
        setCharacterImage(file);
      } else {
        setReferenceImage(file);
      }
    } else {
      alert('请选择有效的图片文件');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!characterImage || !referenceImage) {
      alert('请上传角色图和参考图');
      return;
    }

    setLoading(true);
    setLogs([]);
    addLog('开始处理图像...');
    
    try {
      // 使用外部API端点，需要在环境变量中配置
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
      
      const formData = new FormData();
      formData.append('character_image', characterImage);
      formData.append('reference_image', referenceImage);
      if (prompt) {
        formData.append('prompt', prompt);
      }

      addLog('正在上传图像到处理服务...');
      
      const response = await axios.post(`${API_BASE_URL}/api/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60秒超时
      });

      setResult(response.data);
      addLog('图像处理完成！');
    } catch (error) {
      console.error('Error:', error);
      const errorMsg = error.response?.data?.message || error.message || '处理失败';
      alert('处理失败: ' + errorMsg);
      addLog('处理失败: ' + errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const renderImageComparison = () => {
    if (!result) return null;

    return (
      <div className="result-section">
        <h3>结果对比</h3>
        <div className="image-comparison">
          <div className="image-container">
            <h4>原始参考图</h4>
            {referenceImage && (
              <img 
                src={URL.createObjectURL(referenceImage)} 
                alt="Original Reference" 
                className="result-image"
              />
            )}
          </div>
          
          <div className="image-container">
            <h4>适配垫图</h4>
            {result.intermediate_files && (
              <img 
                src={result.intermediate_files.adapted_reference_path} 
                alt="Adapted Reference" 
                className="result-image"
              />
            )}
          </div>
          
          <div className="image-container">
            <h4>最终融合图</h4>
            {result.generated_image_path && (
              <img 
                src={result.generated_image_path} 
                alt="Generated Result" 
                className="result-image"
              />
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>角色与场景融合优化 Agent</h1>
        <p>通过前置处理解决角色与构图参考图不匹配的问题</p>
      </header>

      <main className="app-main">
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="upload-section">
            <div className="upload-group">
              <label>角色图 (Character Image)</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleImageUpload(e, 'character')}
                required
              />
              {characterImage && (
                <div className="preview">
                  <img 
                    src={URL.createObjectURL(characterImage)} 
                    alt="Character Preview" 
                    className="preview-image"
                  />
                </div>
              )}
            </div>

            <div className="upload-group">
              <label>构图参考图 (Reference Image)</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleImageUpload(e, 'reference')}
                required
              />
              {referenceImage && (
                <div className="preview">
                  <img 
                    src={URL.createObjectURL(referenceImage)} 
                    alt="Reference Preview" 
                    className="preview-image"
                  />
                </div>
              )}
            </div>
          </div>

          <div className="prompt-section">
            <label>生成提示词 (可选)</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="描述你想要的场景和效果..."
              rows="4"
            />
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? '处理中...' : '生成融合图像'}
          </button>
        </form>

        {loading && (
          <div className="loading-section">
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
            <p>正在处理图像，请稍候...</p>
          </div>
        )}

        <div className="logs-section">
          <h3>处理日志</h3>
          <div className="logs-container">
            {logs.map(log => (
              <div key={log.id} className="log-entry">
                {log.message}
              </div>
            ))}
          </div>
        </div>

        {result && renderImageComparison()}

        {result && (
          <div className="validation-section">
            <h3>验证结果</h3>
            <div className="validation-results">
              {result.validation_results && Object.entries(result.validation_results).map(([key, value]) => (
                <div key={key} className={`validation-item ${value.success ? 'success' : 'error'}`}>
                  <span className="validation-name">{key}:</span>
                  <span className="validation-score">得分: {value.score}</span>
                  <span className="validation-feedback">{value.feedback}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;