import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { useAuthStore } from './store/authStore';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const { isAuthenticated } = useAuthStore();
    return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    }
                />
                <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
