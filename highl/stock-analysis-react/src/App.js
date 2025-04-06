// src/App.js
import React from "react";
import { BrowserRouter as Router, Route, Routes, NavLink, useNavigate } from "react-router-dom";
import FetchStockData from "./components/FetchStockData";
import TrainModel from "./components/TrainModel";
import PredictExit from "./components/PredictExit";
import History from "./components/History";
import Auth from "./components/Auth";
import ProtectedRoute from "./components/ProtectedRoute";
import "./App.css";

const AppLayout = () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/auth");
  };

  return (
    <div className="App">
      <h1>📈 Stock Analysis App</h1>

      {isLoggedIn && (
        <>
          <nav>
            <NavLink to="/fetch">Fetch Data</NavLink>
            <NavLink to="/train">Train Model</NavLink>
            <NavLink to="/predict">Predict Exit Price</NavLink>
            <NavLink to="/history">History</NavLink>
          </nav>
          <button onClick={handleLogout} style={{ marginTop: "10px" }}>
            Logout
          </button>
        </>
      )}

      {!isLoggedIn && (
        <nav>
          <NavLink to="/auth">Login / Signup</NavLink>
        </nav>
      )}

      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route path="/fetch" element={<ProtectedRoute><FetchStockData /></ProtectedRoute>} />
        <Route path="/train" element={<ProtectedRoute><TrainModel /></ProtectedRoute>} />
        <Route path="/predict" element={<ProtectedRoute><PredictExit /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/" element={<Auth />} />
      </Routes>
    </div>
  );
};

const App = () => (
  <Router>
    <AppLayout />
  </Router>
);

export default App;
