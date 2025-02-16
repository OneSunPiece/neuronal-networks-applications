//import { useState } from 'react'
import './App.css'
import Header from './components/Header/Header'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import TimeSeries from './TimeSeries/TimeSeries'
import ImageClassifier from './ImageClassifier/ImageClassifier'
import Recommendations from './Recommendations/Recommendations'

function App() {
  return (
    <>
    <Header/>
    
    <section className="container mx-auto p-4">
      <Router>
        <Routes>
          <Route path="/series" element={<TimeSeries />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/images" element={<ImageClassifier />} />
        </Routes>
      </Router>
    </section>
    </>
  )
}

export default App
