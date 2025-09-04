// context/AuthContext.js
import React, { createContext, useState, useEffect } from "react";
import { authAPI } from "../services/api"; // your central API file

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // fetch user on app load
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await authAPI.checkAuth(); // calls /api/check-auth/
        if (data.username) {
          setUser(data);
        } else {
          setUser(null);
        }
      } catch (error) {
        setUser(null);
      }
    };
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};
