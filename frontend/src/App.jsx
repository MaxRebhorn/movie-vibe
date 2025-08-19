// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage/LandingPage";
import MoviePage from "./pages/MoviePage/MoviePage"; // adjust if path differs

function App() {
  return (
    <Router>
      <Routes>
        {/* Base route */}
        <Route path="/" element={<LandingPage />} />
       <Route path="/movies/:id" element={<MoviePage />} />
        {/* Example of other routes */}
        {/* <Route path="/about" element={<About />} /> */}
        {/* <Route path="/contact" element={<Contact />} /> */}
      </Routes>
    </Router>
  );
}

export default App;
