/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from 'react';
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword, 
  signOut, 
  signInWithPopup, 
  onAuthStateChanged,
  updateProfile
} from 'firebase/auth';
import { auth, googleProvider, isFirebaseConfigured } from '../firebase';

const AuthContext = createContext();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001';
const AUTH_SESSION_KEY = 'authSession';

function ensureFirebaseAuth() {
  if (!isFirebaseConfigured || !auth) {
    throw new Error('Firebase chưa được cấu hình. Vui lòng kiểm tra các biến VITE_FIREBASE_* trong frontend.');
  }
}

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [session, setSession] = useState(() => {
    const storedSession = localStorage.getItem(AUTH_SESSION_KEY);
    return storedSession ? JSON.parse(storedSession) : null;
  });
  const [loading, setLoading] = useState(true);

  async function createBackendSession(firebaseUser) {
    const idToken = await firebaseUser.getIdToken();
    const response = await fetch(`${API_BASE_URL}/api/auth/session`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${idToken}`
      }
    });

    if (!response.ok) {
      throw new Error('Không thể tạo phiên đăng nhập trên server.');
    }

    const nextSession = await response.json();
    localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(nextSession));
    setSession(nextSession);

    return nextSession;
  }

  // Đăng ký tài khoản mới bằng Email/Mật khẩu và cập nhật Display Name
  async function signup(email, password, displayName) {
    ensureFirebaseAuth();
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    // Cập nhật Profile (tên hiển thị) sau khi tạo tài khoản thành công
    await updateProfile(userCredential.user, {
      displayName: displayName
    });
    await userCredential.user.reload();
    return createBackendSession(auth.currentUser ?? userCredential.user);
  }

  // Đăng nhập bằng Email/Mật khẩu
  async function login(email, password) {
    ensureFirebaseAuth();
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return createBackendSession(userCredential.user);
  }

  // Đăng xuất
  async function logout() {
    ensureFirebaseAuth();
    const refreshToken = session?.token?.refreshToken;

    if (refreshToken) {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refreshToken })
      }).catch(() => {});
    }

    localStorage.removeItem(AUTH_SESSION_KEY);
    setSession(null);
    return signOut(auth);
  }

  // Đăng nhập bằng Google
  async function loginWithGoogle() {
    ensureFirebaseAuth();
    const userCredential = await signInWithPopup(auth, googleProvider);
    return createBackendSession(userCredential.user);
  }

  // Theo dõi sự thay đổi trạng thái Authentication của Firebase
  useEffect(() => {
    if (!isFirebaseConfigured || !auth) {
      queueMicrotask(() => setLoading(false));
      return undefined;
    }

    const loadingFallback = setTimeout(() => {
      setLoading(false);
    }, 2500);

    const unsubscribe = onAuthStateChanged(auth, (user) => {
      clearTimeout(loadingFallback);
      setCurrentUser(user);
      setLoading(false);
    });

    return () => {
      clearTimeout(loadingFallback);
      unsubscribe();
    };
  }, []);

  const value = {
    currentUser,
    session,
    accessToken: session?.token?.accessToken ?? null,
    refreshToken: session?.token?.refreshToken ?? null,
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
