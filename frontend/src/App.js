import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Search from './components/Search';
import Case from './components/Case';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Search />} />
        <Route path="/case/:filename" element={<Case />} />
      </Routes>
    </Router>
  );
}

export default App;
