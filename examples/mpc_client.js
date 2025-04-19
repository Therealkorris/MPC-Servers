/**
 * Example MPC client in JavaScript that connects to the MPC Visio server.
 */

// MPC server configuration
const mpcConfig = {
  mcpServers: {
    visio: {
      transport: "sse",
      url: "http://localhost:8050/sse"
    }
  }
};

/**
 * Send a request to the MPC server
 * @param {string} serverId - The ID of the server in the MPC config
 * @param {string} method - The method to call
 * @param {object} params - The parameters for the method
 * @returns {Promise<object>} - The response from the server
 */
async function sendMpcRequest(serverId, method, params = {}) {
  const serverConfig = mpcConfig.mcpServers[serverId];
  if (!serverConfig) {
    throw new Error(`Server ${serverId} not found in MPC config`);
  }
  
  const url = serverConfig.url || serverConfig.serverUrl;
  if (!url) {
    throw new Error(`No URL defined for server ${serverId}`);
  }
  
  const request = {
    id: crypto.randomUUID(),
    method,
    params
  };
  
  console.log(`Sending request to ${url}:`, request);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Handle SSE response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    const { value, done } = await reader.read();
    if (done) {
      throw new Error('No data received');
    }
    
    const text = decoder.decode(value);
    const lines = text.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        return data;
      }
    }
    
    throw new Error('No data found in response');
  } catch (error) {
    console.error('Error sending MPC request:', error);
    return {
      error: {
        code: -32603,
        message: `Error: ${error.message}`
      }
    };
  }
}

/**
 * Analyze a Visio diagram
 * @param {string} filePath - Path to the Visio file
 * @param {string} analysisType - Type of analysis to perform
 * @returns {Promise<object>} - The analysis result
 */
async function analyzeVisioDiagram(filePath, analysisType = 'structure') {
  return sendMpcRequest('visio', 'analyze_visio_diagram', {
    file_path_or_content: filePath,
    analysis_type: analysisType
  });
}

/**
 * Ask AI about a Visio diagram
 * @param {Array} messages - The conversation messages
 * @param {string} model - The model to use
 * @returns {Promise<object>} - The AI response
 */
async function askAiAboutVisio(messages, model = 'llama3') {
  return sendMpcRequest('visio', 'ask_ai_about_visio', {
    messages,
    model
  });
}

/**
 * Example usage
 */
async function example() {
  try {
    // Example 1: Analyze a diagram
    const filePath = 'examples/sample.vsdx';
    const analysisResult = await analyzeVisioDiagram(filePath);
    console.log('Analysis result:', analysisResult);
    
    // Example 2: Ask AI about the diagram
    const messages = [
      {
        role: 'system',
        content: 'You are an assistant that helps with analyzing Visio diagrams.'
      },
      {
        role: 'user',
        content: `I have a Visio diagram with the following structure: ${JSON.stringify(analysisResult.result)}. Can you explain what this diagram represents?`
      }
    ];
    
    const aiResponse = await askAiAboutVisio(messages);
    console.log('AI response:', aiResponse);
  } catch (error) {
    console.error('Error in example:', error);
  }
}

// Run the example when this script is executed directly
if (typeof require !== 'undefined' && require.main === module) {
  example();
}

// Export functions for use in other modules
if (typeof module !== 'undefined') {
  module.exports = {
    sendMpcRequest,
    analyzeVisioDiagram,
    askAiAboutVisio
  };
} 