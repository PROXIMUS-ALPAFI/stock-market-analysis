import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import FetchStockData from "./components/FetchStockData";
import TrainModel from "./components/TrainModel";
import PredictExit from "./components/PredictExit"
import History from "./components/history";


function App() {
  return (
      <Router>
        <div style={{ textAlign: "center" }}>
          <h1>Stock Analysis App</h1>
          <nav>
            <Link to="/">Fetch Data</Link> |
            <Link to="/train">Train Model</Link> |
            <Link to="/predict">Predict Exit Price</Link>|
            <Link to="/history">History</Link> |
          </nav>

          <Routes>
            <Route path="/" element={<FetchStockData />} />
            <Route path="/train" element={<TrainModel />} />
            <Route path="/predict" element={<PredictExit />} />
            <Route path="/history" element={<History/>}/>
          </Routes>
        </div>
      </Router>
  );
}

export default App;
