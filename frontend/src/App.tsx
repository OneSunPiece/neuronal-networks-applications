//import { useState } from 'react'
import './App.css'
import Header from './components/Header/Header'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import TimeSeries from './TimeSeries/TimeSeries'

function App() {
  return (
    <>
    <Header/>
    <h1 className="text-4xl font-bold">
      asd
    </h1>
    <section className="container mx-auto p-4">
      <Router>
        <Routes>
          <Route path="/series" element={<TimeSeries />} />
        </Routes>
      </Router>
    </section>
    </>
  )
}

export default App
