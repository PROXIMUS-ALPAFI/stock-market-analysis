import React, { useState } from "react";

function TrainModel() {
    const [symbol, setSymbol] = useState("");
    const [message, setMessage] = useState("");
    const [metrics, setMetrics] = useState({
        mse: null,
        r2: null,
        accuracy: null,
        f1: null
    });

    const trainModel = async () => {
        if (!symbol) {
            alert("Enter a stock symbol!");
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/train_model", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol }),
        });

        const data = await response.json();
        setMessage(data.error ? `Error: ${data.error}` : `✅ Model Trained!`);

        if (data.mse && data.r2 && data.accuracy && data.f1) {
            setMetrics({
                mse: data.mse,
                r2: data.r2,
                accuracy: data.accuracy,
                f1: data.f1
            });
        }
    };

    return (
        <div>
            <h2>Train Model</h2>
            <input
                type="text"
                value={symbol}
                placeholder="Enter Stock Symbol"
                onChange={(e) => setSymbol(e.target.value)}
            />
            <button onClick={trainModel}>Train</button>
            <p>{message}</p>

            {/* Display metrics */}
            {metrics.mse && (
                <div>
                    <h3>Model Metrics</h3>
                    <ul>
                        <li>MSE: {metrics.mse}</li>
                        <li>R²: {metrics.r2}</li>
                        <li>Accuracy: {metrics.accuracy}</li>
                        <li>F1 Score: {metrics.f1}</li>
                    </ul>
                </div>
            )}
        </div>
    );
}

export default TrainModel;
