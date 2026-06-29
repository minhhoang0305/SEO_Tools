import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children }) {
  const { currentUser } = useAuth();

  if (!currentUser) {
    // Chuyển hướng người dùng về trang Đăng nhập nếu chưa đăng nhập
    return <Navigate to="/login" replace />;
  }

  return children;
}
