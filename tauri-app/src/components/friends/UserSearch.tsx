import React from 'react';
import { useFriendStore } from '../../store/friendStore';
import { useAuthStore } from '../../store/authStore';

export const UserSearch: React.FC = () => {
    const [query, setQuery] = React.useState('');
    const { searchUsers, searchResults, sendFriendRequest, isLoading, error } = useFriendStore();
    const token = useAuthStore((state) => state.token);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.length >= 3 && token) {
            searchUsers(query, token);
        }
    };

    const handleAddFriend = async (userId: string) => {
        if (token) {
            try {
                await sendFriendRequest(userId, token);
                alert('Friend request sent!');
            } catch (err) {
                alert('Failed to send request');
            }
        }
    };

    return (
        <div className="p-4 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Find Friends</h3>
            <form onSubmit={handleSearch} className="flex gap-2 mb-4">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search by email..."
                    className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    minLength={3}
                />
                <button
                    type="submit"
                    disabled={isLoading}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
                >
                    Search
                </button>
            </form>

            {error && <p className="text-red-500 text-sm mb-2">{error}</p>}

            <div className="space-y-2">
                {searchResults.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                        <div>
                            <p className="font-medium">{user.email}</p>
                        </div>
                        <button
                            onClick={() => handleAddFriend(user.id)}
                            className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
                        >
                            Add
                        </button>
                    </div>
                ))}
                {searchResults.length === 0 && query.length >= 3 && !isLoading && (
                    <p className="text-gray-500 text-center text-sm">No users found</p>
                )}
            </div>
        </div>
    );
};
