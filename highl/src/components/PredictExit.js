import React, { useState } from "react";

function PredictExit() {
    const [symbol, setSymbol] = useState("");
    const [predictedPrice, setPredictedPrice] = useState("");

    const predictExitPrice = async () => {
        if (!symbol) {
            alert("Enter a stock symbol!");
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/predict_exit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol }),
        });

        const data = await response.json();
        setPredictedPrice(data.error ? `Error: ${data.error}` : `Predicted Exit Price: ${data.predicted_exit_price}`);
    };

    return (
        <div>
            <h2>Predict Exit Price</h2>
            <input
                type="text"
                value={symbol}
                placeholder="Enter Stock Symbol"
                onChange={(e) => setSymbol(e.target.value)}
            />
            <button onClick={predictExitPrice}>Predict</button>
            <p>{predictedPrice}</p>
        </div>
    );
}

export default PredictExit;
