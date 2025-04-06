import React, { useState } from "react";

function PredictExit() {
    const [symbol, setSymbol] = useState("");
    const [predictedPrice, setPredictedPrice] = useState("");
    const [error, setError] = useState("");

    const predictExitPrice = async () => {
        const userId = localStorage.getItem("user_id");

        if (!symbol) {
            alert("Enter a stock symbol!");
            return;
        }

        if (!userId) {
            alert("You must be logged in to make predictions.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/predict_exit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbol, user_id: userId }),
            });

            const data = await response.json();

            if (response.ok) {
                setPredictedPrice(`Predicted Exit Price for ${symbol.toUpperCase()}: $${data.predicted_exit_price.toFixed(2)}`);
                setError("");
            } else {
                setPredictedPrice("");
                setError(data.error || "An error occurred while predicting.");
            }
        } catch (err) {
            console.error(err);
            setPredictedPrice("");
            setError("Failed to connect to server.");
        }
    };

    return (
        <div style={{ maxWidth: "400px", margin: "0 auto", padding: "20px" }}>
            <h2>Predict Exit Price</h2>
            <input
                type="text"
                value={symbol}
                placeholder="Enter Stock Symbol"
                onChange={(e) => setSymbol(e.target.value)}
                style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
            />
            <button onClick={predictExitPrice} style={{ width: "100%", padding: "10px" }}>
                Predict
            </button>
            {predictedPrice && <p style={{ marginTop: "20px", color: "green" }}>{predictedPrice}</p>}
            {error && <p style={{ marginTop: "20px", color: "red" }}>{error}</p>}
        </div>
    );
}

export default PredictExit;
