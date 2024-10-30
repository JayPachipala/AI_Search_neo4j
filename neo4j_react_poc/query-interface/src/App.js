import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import './App.css';

function App() {
  const [userInput, setUserInput] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [viewType, setViewType] = useState('table'); // State to track the current view type
  const [history, setHistory] = useState([]); // State to store question and answer history
  const [metric, setMetric] = useState('total_spending'); // Default metric for the chart

  const submitQuery = async () => {
    setError(null);
    try {
      const res = await axios.post('http://127.0.0.1:8000/generate_query', {
        user_input: userInput
      });
      console.log("API Response:", res.data);
      setResponse(res.data);
      setUserInput(''); // Clear input after submission

      // Add the current question and response to history
      setHistory([...history, { question: userInput, response: res.data }]);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred");
      setResponse(null);
    }
  };

  const renderChart = (data) => {
    if (!data || !data.results || data.results.length === 0) {
      return <p>No results found.</p>;
    }

    // Prepare dynamic data for the chart based on the selected metric
    const chartData = data.results.map(item => ({
      name: item.vendor_name || item.department_name || item.contract_id || item.expense_category,
      value: item[metric] // Use the selected metric for the bar chart
    }));

    return (
      <BarChart
        width={600}
        height={300}
        data={chartData}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" fill="#8884d8" />
      </BarChart>
    );
  };

  const renderTable = (data) => {
    if (!data || !data.results || data.results.length === 0) {
      return <p>No results found.</p>;
    }

    const columns = Object.keys(data.results[0]);

    return (
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.results.map((item, index) => (
            <tr key={index}>
              {columns.map((col) => (
                <td key={col}>{item[col]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div className="App">
      <h1>Query Interface</h1>
      <div className="interface-container">
        <div className="input-section">
          <h3>Your Question:</h3>
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Enter your query..."
            rows={4}
            style={{ width: '97%', padding: '10px', marginBottom: '10px' }}
          />
          <button onClick={submitQuery} style={{ padding: '10px' }}>Submit</button>
        </div>
        <div className="response-section">
          <h3>Response:</h3>
          <div>
            <label>
              <input
                type="radio"
                value="table"
                checked={viewType === 'table'}
                onChange={() => setViewType('table')}
              />
              Table
            </label>
            <label style={{ marginLeft: '10px' }}>
              <input
                type="radio"
                value="chart"
                checked={viewType === 'chart'}
                onChange={() => setViewType('chart')}
              />
              Chart
            </label>
          </div>
          {error ? (
            <p style={{ color: 'red' }}>{error}</p>
          ) : (
            viewType === 'chart' ? renderChart(response) : renderTable(response)
          )}
        </div>
      </div>
      <div className="history-section">
        <h3>Previous Questions & Responses:</h3>
        {history.length === 0 ? (
          <p>No previous questions.</p>
        ) : (
          <ul>
            {history.map((item, index) => (
              <li key={index}>
                <strong>Q:</strong> {item.question} <br />
                <strong>A:</strong> {JSON.stringify(item.response, null, 2)} {/* Display response as JSON */}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;
