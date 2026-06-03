import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword, 
  signOut, 
  signInWithPopup, 
  onAuthStateChanged,
  updateProfile
} from 'firebase/auth';
import { auth, googleProvider } from '../firebase';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Đăng ký tài khoản mới bằng Email/Mật khẩu và cập nhật Display Name
  async function signup(email, password, displayName) {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    // Cập nhật Profile (tên hiển thị) sau khi tạo tài khoản thành công
    await updateProfile(userCredential.user, {
      displayName: displayName
    });
    // Trả về user cập nhật mới nhất
    return userCredential.user;
  }

  // Đăng nhập bằng Email/Mật khẩu
  function login(email, password) {
    return signInWithEmailAndPassword(auth, email, password);
  }

  // Đăng xuất
  function logout() {
    return signOut(auth);
  }

  // Đăng nhập bằng Google
  function loginWithGoogle() {
    return signInWithPopup(auth, googleProvider);
  }

  // Theo dõi sự thay đổi trạng thái Authentication của Firebase
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value = {
    currentUser,
    signup,
    login,
    logout,
    loginWithGoogle
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
