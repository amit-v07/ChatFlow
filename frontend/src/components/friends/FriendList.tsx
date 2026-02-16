import React, { useEffect } from 'react';
import { useFriendStore } from '../../store/friendStore';
import { useAuthStore } from '../../store/authStore';

interface FriendListProps {
    onlineUsers: string[];
    onSelectFriend: (friendId: string) => void;
}

export const FriendList: React.FC<FriendListProps> = ({ onlineUsers, onSelectFriend }) => {
    const { friends, fetchFriends } = useFriendStore();
    const token = useAuthStore((state) => state.token);

    useEffect(() => {
        if (token) {
            fetchFriends(token);
        }
    }, [token, fetchFriends]);

    console.log('FriendList Render. onSelectFriend type:', typeof onSelectFriend);

    return (
        <div className="flex-1 overflow-y-auto">
            <h3 className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Friends ({friends.length})
            </h3>
            <div className="space-y-1">
                {friends.map(({ friend }) => {
                    const isOnline = onlineUsers.includes(friend.id);
                    return (
                        <div
                            key={friend.id}
                            onClick={() => {
                                console.log('Clicking friend div:', friend.id);
                                try {
                                    onSelectFriend(friend.id);
                                } catch (e) {
                                    console.error('Error calling onSelectFriend:', e);
                                }
                            }}
                            className="flex items-center gap-3 p-3 hover:bg-red-100 cursor-pointer transition-colors border border-transparent hover:border-red-300"
                        >
                            <div className="relative">
                                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold border border-blue-200">
                                    {friend.email[0].toUpperCase()}
                                </div>
                                {isOnline && (
                                    <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white rounded-full"></span>
                                )}
                            </div>
                            <div className="ml-3 truncate">
                                <p className="text-sm font-medium text-gray-900 truncate">{friend.email}</p>
                                <p className="text-xs text-gray-500">
                                    {isOnline ? 'Online' : 'Offline'}
                                </p>
                            </div>
                        </div>
                    );
                })}
                {friends.length === 0 && (
                    <div className="px-4 py-8 text-center text-gray-500 text-sm">
                        No friends yet. <br />Use search to add some!
                    </div>
                )}
            </div>
        </div>
    );
};
