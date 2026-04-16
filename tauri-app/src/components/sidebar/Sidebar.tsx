import React, { useState } from 'react';
import { LogOut, Users, MessageSquare, Search } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { FriendList } from '../friends/FriendList';
import { UserSearch } from '../friends/UserSearch';

interface SidebarProps {
    onlineUsers: string[];
    onSelectFriend: (friendId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onlineUsers, onSelectFriend }) => {
    const logout = useAuthStore((state) => state.logout);
    const user = useAuthStore((state) => state.user);
    const [activeTab, setActiveTab] = useState<'chats' | 'friends'>('chats');
    const [showSearch, setShowSearch] = useState(false);

    return (
        <div
            className="w-80 bg-white border-r flex flex-col h-full bg-gray-50"
            onClick={() => console.log('Sidebar Root Clicked')} // DEBUG
        >
            {/* User Header */}
            <div className="p-4 border-b bg-white">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">
                            {user?.email?.[0].toUpperCase()}
                        </div>
                        <span className="font-semibold text-gray-800 truncate max-w-[120px]" title={user?.email}>
                            {user?.email}
                        </span>
                    </div>
                    <button onClick={logout} className="text-gray-500 hover:text-red-500 transition-colors" title="Logout">
                        <LogOut size={20} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex bg-gray-100 p-1 rounded-lg">
                    <button
                        onClick={() => setActiveTab('chats')}
                        className={`flex-1 flex items-center justify-center py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === 'chats' ? 'bg-white shadow text-indigo-600' : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        <MessageSquare size={16} className="mr-2" />
                        Chats
                    </button>
                    <button
                        onClick={() => setActiveTab('friends')}
                        className={`flex-1 flex items-center justify-center py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === 'friends' ? 'bg-white shadow text-indigo-600' : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        <Users size={16} className="mr-2" />
                        Friends
                    </button>
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden flex flex-col">
                {activeTab === 'friends' ? (
                    <>
                        <div className="p-2 border-b">
                            <button
                                onClick={() => setShowSearch(!showSearch)}
                                className="w-full flex items-center justify-center px-3 py-2 border rounded-md text-sm text-gray-600 hover:bg-gray-50 transition-colors gap-2"
                            >
                                <Search size={16} />
                                {showSearch ? 'Hide Search' : 'Find Friends'}
                            </button>
                        </div>

                        {showSearch && (
                            <div className="p-2 bg-gray-50 border-b">
                                <UserSearch />
                            </div>
                        )}

                        <FriendList onlineUsers={onlineUsers} onSelectFriend={onSelectFriend} />
                    </>
                ) : (
                    <div className="flex-1 flex items-center justify-center text-gray-400 p-4 text-center">
                        <div>
                            <MessageSquare size={48} className="mx-auto mb-2 opacity-50" />
                            <p>Recent chats will appear here</p>
                            <p className="text-xs mt-2">Start a conversation from your Friends list!</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
