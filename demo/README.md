# Project Setup Guide

## Backend Setup

### 1. Open Anaconda Prompt and navigate to the Backend Directory
```bash
cd backend
```

### 2. Create and activate Python virtual environment
```bash
conda create -n ds
conda activate ds
```

### 3. Install Required Python Packages
```bash
conda install -c anaconda flask pandas numpy pillow scikit-learn
conda install -c conda-forge flask_cors fuzzywuzzy matplotlib
```
### 4. Run the Flask Server
```bash
python app.py
```

## Frontend Setup

### 1. Open a new terminal and navigate to the Frontend Directory
```bash
cd frontend
```
### 2. Install Required Node Packages
```bash
npm install
```
### 3. Run the React App
```bash
npm start
```
