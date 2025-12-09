# AI-Driven Traffic Congestion Prediction & Action Simulator

A comprehensive system for predicting traffic congestion and simulating mitigation actions in real-time.

## Features

- **Traffic Simulation Engine**: Macroscopic queueing model with dynamic capacity adjustments
- **Congestion Prediction**: 30-60 minute ahead forecasting
- **Action Simulation**: Test traffic light timing and police diversions
- **AI Recommendations**: Optimal action suggestions to minimize congestion
- **Interactive Map Interface**: Visual traffic management dashboard

## Architecture

```
├── backend/           # FastAPI server with simulation engine
├── frontend/          # React + Leaflet interactive map
└── docs/             # Documentation and specifications
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 12000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 12001
```

## Core Components

1. **Simulation Engine**: Queue-based traffic flow modeling
2. **Prediction Module**: Forward simulation for congestion forecasting
3. **AI Optimizer**: Multi-scenario evaluation and recommendation
4. **Web Interface**: Real-time traffic management dashboard

## Traffic Control Actions

- **Green Time Adjustment**: Increase signal timing at intersections
- **Police Flow Control**: Reduce capacity on road segments
- **Scenario Comparison**: Evaluate multiple intervention strategies
- **Real-time Visualization**: Color-coded congestion levels

## Technology Stack

- **Backend**: Python, FastAPI, NumPy, Pandas
- **Frontend**: React, TypeScript, Leaflet, Vite
- **Simulation**: Custom macroscopic traffic model
- **AI**: Multi-objective optimization algorithms