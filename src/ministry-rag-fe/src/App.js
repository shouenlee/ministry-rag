import './App.css';
import React from 'react';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      apiResponse: "",
      userInput: ""
    };
  }

  handleInputChange = (event) => {
    this.setState({ userInput: event.target.value });
  }

  callAPI = () => {
    fetch("http://localhost:5000/prompt", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question: this.state.userInput })
    })
    .then(res => {
      if (!res.ok) {
        throw new Error('Network response was not ok');
      }
      return res.json();
    })
    .then(res => this.setState({ apiResponse: res.response }))
    .catch(error => console.error('There was a problem with the fetch operation:', error));
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <div style={{ display: "flex", alignItems: "center" }}>
            <input 
              type="text" 
              value={this.state.userInput} 
              onChange={this.handleInputChange} 
              placeholder="Ask a question" 
              style={{ width: "300px", height: "40px", marginRight: "10px" }}
              onKeyPress={(event) => {
                if (event.key === "Enter") {
                  this.callAPI();
                }
              }}
            />
            <button 
              onClick={this.callAPI} 
              style={{ height: "40px" }}
            >
              Submit
            </button>
          </div>
          <p style={{ width: "50vw" }}>{this.state.apiResponse}</p>
        </header>
      </div>
    );
  }
}

export default App;