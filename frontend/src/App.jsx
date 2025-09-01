// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage/LandingPage";
import MoviePage from "./pages/MoviePage/MoviePage";
import LoginPage from "./pages/LoginPage/LoginPage";
import RegisterPage from "./pages/RegisterPage/RegisterPage"; // adjust if path differs
import UserPage from "./pages/UserPage/UserPage";
import Questionnaire from "./pages/Questionnaire/Questionnaire";
function App() {
  return (
    <Router>
      <Routes>
        {/* Base route */}
        <Route path="/" element={<LandingPage />} />
       <Route path="/movies/:id" element={<MoviePage />} />
          <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          <Route path="/user" element={<UserPage />} />
           <Route path="/movies/:id/review" element={<Questionnaire />} />
        {/* Example of other routes */}
        {/* <Route path="/about" element={<About />} /> */}
        {/* <Route path="/contact" element={<Contact />} /> */}
      </Routes>
    </Router>
  );
}

export default App;
