import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({
    username: 'Nachatra',
    first_name: 'Nachatra',
    email: 'nachatra@example.com',
  });

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        loading: false,
        isAuthenticated: true,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: { username: 'Nachatra', first_name: 'Nachatra' },
      loading: false,
      isAuthenticated: true,
    };
  }
  return context;
};
