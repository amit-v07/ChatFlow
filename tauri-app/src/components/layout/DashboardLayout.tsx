import { type ReactNode } from 'react';
import { Sidebar } from '../sidebar/Sidebar';
// import { useWebSocket } from '../../hooks/useWebSocket';
// We will move useWebSocket here or higher up to share state

interface DashboardLayoutProps {
    children: ReactNode;
    onlineUsers: string[];
    onSelectFriend: (friendId: string) => void;
}

export const DashboardLayout = ({ children, onlineUsers, onSelectFriend }: DashboardLayoutProps) => {
    return (
        <div className="flex h-screen w-screen bg-gray-100 overflow-hidden">
            {/* Sidebar wrapper with high z-index and debug border */}
            <div className="z-50 relative border-4 border-red-500">
                <Sidebar onlineUsers={onlineUsers} onSelectFriend={onSelectFriend} />
            </div>

            {/* Main content with lower z-index and debug border */}
            <main className="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative z-0 border-4 border-blue-500">
                {children}
            </main>
        </div>
    );
};
